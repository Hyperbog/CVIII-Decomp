#!/usr/bin/env python3
"""JP0651: optional read-only MesenCE original DMC DMA reference source overlay.

Pin: nesdev-org/MesenCE 4b8a196e299b3de297b204fd1208d2981562c89b
Core/NES/NesCpu.cpp Git blob d411c11981f16011bd8a19f7cc0b2a69cae1a019.
This patches a PRIVATE independently-built MesenCE core checkout, never
the CVIII ROM or upstream repository. NOT a claim Mesen was run in CI.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

PIN="d411c11981f16011bd8a19f7cc0b2a69cae1a019"
MARK="CVIII_MESEN_DMC_REFERENCE_0651"
INCLUDE='#include "NES/NesConsole.h"'
EXTRA='#include "NES/BaseMapper.h"\n#include "Shared/MemoryType.h"\n#include <cstdio>\n#include <cstdlib>'
OLD='''\t\t\t\t_isDmcDmaRead = true; //used by debugger to distinguish between dmc and oam/dummy dma reads
\t\t\t\treadValue = ProcessDmaRead(_console->GetApu()->GetDmcReadAddress(), prevReadAddress, enableInternalRegReads);
\t\t\t\t_isDmcDmaRead = false;'''
NEW='''\t\t\t\t_isDmcDmaRead = true; //used by debugger to distinguish between dmc and oam/dummy dma reads
\t\t\t\t// CVIII_MESEN_DMC_REFERENCE_0651: genuine DMC read path only.
\t\t\t\tconst uint16_t cviiiDmcAddr = _console->GetApu()->GetDmcReadAddress();
\t\t\t\treadValue = ProcessDmaRead(cviiiDmcAddr, prevReadAddress, enableInternalRegReads);
\t\t\t\tcviiiMesenDmcReference(_console, _state.CycleCount, cviiiDmcAddr, readValue);
\t\t\t\t_isDmcDmaRead = false;'''
HOOK=r'''/* CVIII_MESEN_DMC_REFERENCE_0651: local optional reference only.
 * Do NOT register CPU generic/PPU/OAM/dummy memory-read callbacks.
 * This is exclusively the actual original MesenCE DMC DMA get branch.
 * A nonempty CVIII_MESEN_DMC_TRACE environment path opts in. A source
 * capture may include original ROM bytes: NEVER add it to the repo. */
static void cviiiMesenDmcReference(NesConsole* console, uint64_t cycle,
                                    uint16_t address, uint8_t value)
{
    struct Capture {
        FILE* file = nullptr;
        uint32_t rows = 0;
        Capture() {
            const char* path = std::getenv("CVIII_MESEN_DMC_TRACE");
            if(path && *path) {
                file = std::fopen(path, "w");
                if(file) {
                    std::fputs("event,cycle,cpu_addr,physical,byte\n", file);
                    std::fflush(file);
                }
            }
        }
        ~Capture() { if(file) std::fclose(file); }
    };
    static Capture out;
    if(!out.file) return;
    if(out.rows >= 200000u) {
        if(out.rows == 200000u) {
            std::fprintf(out.file, "trace_limit,%llu,-1,-1,-1\n",
                         (unsigned long long)cycle);
            std::fflush(out.file);
            ++out.rows;
        }
        return;
    }
    AddressInfo physical = console->GetMapper()->GetAbsoluteAddress(address);
    const int32_t offset = physical.Type == MemoryType::NesPrgRom
                            ? physical.Address : -1;
    std::fprintf(out.file, "dma_fetch,%llu,%u,%d,%u\n",
                 (unsigned long long)cycle, (unsigned)address,
                 (int)offset, (unsigned)value);
    std::fflush(out.file);
    ++out.rows;
}
'''

def blob_sha(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def generate(source:str)->str:
    if MARK in source:raise ValueError("Already instrumented MesenCE DMC core")
    if source.count(INCLUDE)!=1 or source.count(OLD)!=1:
        raise ValueError("MesenCE real DMC branch changed or absent")
    source=source.replace(INCLUDE,INCLUDE+"\n"+EXTRA,1)
    constructor="NesCpu::NesCpu(NesConsole* console)"
    if source.count(constructor)!=1:
        raise ValueError("MesenCE CPU constructor anchor changed")
    source=source.replace(constructor,HOOK+"\n"+constructor,1)
    source=source.replace(OLD,NEW,1)
    if source.count(MARK)!=2 or source.count("cviiiMesenDmcReference(_console,")!=1:
        raise ValueError("MesenCE diagnostic hook insertion mismatch")
    if source.count("ProcessDmaRead(cviiiDmcAddr, prevReadAddress, enableInternalRegReads)")!=1:
        raise ValueError("MesenCE actual DMC read call was not preserved")
    return source

def smoke()->None:
    fixture=(INCLUDE+"\n"+'NesCpu::NesCpu(NesConsole* console)\n{\n}\n'+OLD)
    x=generate(fixture)
    assert x.count(MARK)==2 and x.count("cviiiMesenDmcReference(_console,")==1
    assert 'GetAbsoluteAddress(address)' in x
    assert 'CVIII_MESEN_DMC_TRACE' in x
    assert 'std::fopen(path, "w")' in x
    assert 'ProcessDmaRead(cviiiDmcAddr' in x
    for damaged in (x,fixture.replace(OLD,"// no DMA hook"),
                    fixture.replace(INCLUDE,"// lost console include")):
        try:generate(damaged)
        except ValueError:pass
        else:raise AssertionError("Altered/duplicate MesenCE source accepted")
    assert blob_sha(b"test")==hashlib.sha1(b"blob 4\0test").hexdigest()
    print("PASS JP0651 MesenCE actual DMC-only fetch observer patch and source fail-closed contracts")

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--source",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.smoke:smoke()
    if args.source or args.out:
        if not args.source or not args.out:
            p.error("--source and --out required together")
        src=args.source.resolve(strict=True);out=args.out.resolve()
        if src.name!="NesCpu.cpp" or out.name!="NesCpu.cpp" or src==out:
            raise ValueError("Source and patched output must be separate NesCpu.cpp locations")
        raw=src.read_bytes()
        if blob_sha(raw)!=PIN:
            raise ValueError("MesenCE original CPU source blob does not match the pinned version")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(generate(raw.decode("utf-8")),encoding="utf-8")
        print("PASS JP0651 generated pinned read-only MesenCE DMC-only source overlay")
    elif not args.smoke:
        p.error("--smoke or --source plus --out required")
if __name__=="__main__":main()
