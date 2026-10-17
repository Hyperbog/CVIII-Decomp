#!/usr/bin/env python3
"""JP0653: original NMOS-6502 phrase-pointer reads vs native C11 lookup.

Owner ROM stays private. No musical opcode meanings, notes, PCM or phrase
payloads are exported. Source table membership is not gameplay liveness.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
TABLE_SHA = "2c2b1d4a4f59c39c8ad46ad4b2c103055cf61911fdd3e68e104b1a5d2cfd8945"
POOL_SHA = "a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5"
CODE_SHA = (
    "7b5d76bfa7b74521769c25f33258af5d2929461695e80c78ae3769274c4fc350",
    "cb9975a69bde783bc881ed8c2e9ee35a97f755d28913653a278cbbbeb9d28941",
)
BANK_SIZE = 16384
TABLE_START, TABLE_END, POOL_END = 0xA304, 0xA42C, 0xA957
BLOCKS = ((0x8B2C, 0x8B3B, 0xA304), (0x8D07, 0x8D15, 0xA404))


def hash256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def require(cond: bool, why: str) -> None:
    if not cond:
        raise ValueError(why)


def rd(b: bytes, pc: int) -> int:
    require(len(b) == BANK_SIZE and 0x8000 <= pc < 0xC000, "raw0C source outside physical bank")
    return b[pc - 0x8000]


def phrase_partition(b: bytes, *, authenticated: bool) -> dict:
    require(len(b) == BANK_SIZE, "raw0C must be exactly 16KiB")
    if authenticated:
        require(hash256(b[TABLE_START-0x8000:TABLE_END-0x8000]) == TABLE_SHA,
                "source phrase pointer table SHA mismatch")
        require(hash256(b[TABLE_END-0x8000:POOL_END-0x8000]) == POOL_SHA,
                "source phrase pool SHA mismatch")
        for (lo, hi, _), expected in zip(BLOCKS, CODE_SHA):
            require(hash256(b[lo-0x8000:hi-0x8000]) == expected,
                    "original 6502 phrase lookup opcode SHA mismatch")
    entries = [rd(b, TABLE_START+2*i) | rd(b,TABLE_START+2*i+1) << 8
               for i in range(148)]
    require(entries == sorted(entries) and entries[0] == TABLE_END
            and all(TABLE_END <= p < POOL_END for p in entries),
            "nonmonotone or out-of-bank structural phrase pointer")
    roots = sorted(set(entries))
    require(len(roots) == 140 and roots[-1] < POOL_END,
            "structural original phrase root count changed")
    intervals = list(zip(roots, roots[1:] + [POOL_END]))
    require(all(hi > lo and rd(b,hi-1) == 0xFF for lo,hi in intervals),
            "unterminated or zero-width original phrase interval")
    require(sum(hi-lo for lo,hi in intervals) == 1323,
            "original 1323-byte phrase pool partition drift")
    internal = sum(rd(b,off) == 0xFF for lo,hi in intervals for off in range(lo,hi-1))
    if authenticated:
        require(internal == 1 and rd(b, 0xA94F) == 0xFF and
                rd(b, 0xA956) == 0xFF,
                "original trailing phrase structural interval changed")
    return {"source_table_entries":len(entries), "unique_phrase_roots":len(roots),
            "pool_bytes":1323, "internal_ff_terminators":internal,
            "primary_table_entries":128, "secondary_table_entries":20,
            "index_wrap_selector_domain":256,
            "primary_bounded_selectors":256, "secondary_bounded_selectors":40,
            "entries":entries, "bounds":dict(intervals)}


def original_cpu(b: bytes, mode: int, selector: int, x: int) -> dict:
    """Execute actual authenticated 6502 opcodes, never a pointer formula."""
    require(mode in (0,1) and 0 <= selector <= 255 and 0 <= x <= 255,
            "original CPU bounded input")
    ram = bytearray(2048)
    ram[0x01B7+x] = selector
    ram[0x06] = selector
    pc, stop, _ = BLOCKS[mode]
    a = y = 0; z = n = 0
    steps = 0
    while pc < stop:
        op = rd(b,pc); pc += 1; steps += 1
        if op == 0xBD:  # LDA abs,X
            low, high = rd(b,pc), rd(b,pc+1); pc += 2
            at = ((high << 8 | low) + x) & 0xFFFF
            require(at < len(ram), "source CPU indexed RAM escaped fixture")
            a = ram[at]
        elif op == 0xA5: # LDA zp
            at = rd(b,pc); pc += 1; a = ram[at]
        elif op == 0x0A: # ASL A (8-bit NMOS wrap)
            a = (a << 1) & 255
        elif op == 0xA8: # TAY
            y = a
        elif op == 0xB9: # LDA abs,Y, read original physical bank0C
            low, high = rd(b,pc), rd(b,pc+1); pc += 2
            a = rd(b,((high << 8 | low) + y) & 0xFFFF)
        elif op == 0x85: # STA zp
            at = rd(b,pc); pc += 1; ram[at] = a
            continue
        else:
            raise ValueError(f"unproven 6502 opcode at {pc-1:04X}: {op:02X}")
        z, n = int(a == 0), int(a & 0x80 != 0)
    require(pc == stop and steps == 7, "wrong actual opcode sequence extent")
    return {"a":a,"x":x,"y":y,"z":z,"n":n,
            "word":ram[0xE2] | ram[0xE3]<<8, "zp_e2":ram[0xE2],
            "zp_e3":ram[0xE3]}


class NativeResult(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint8) for name in
                ("final_a","final_y","final_z","final_n","source_is_indexed_table")]
    _fields_ += [(name, ctypes.c_uint16) for name in
                 ("source_word_cpu_address","original_raw_word","span_start","span_end_exclusive")]


def native_parity(bank: bytes, library: Path) -> dict:
    import ctypes as C
    dll = C.CDLL(str(library.resolve()))
    fn = dll.cviii_phrase_lookup_0653
    fn.argtypes = [C.POINTER(C.c_uint8), C.c_size_t, C.c_int, C.c_uint8,
                   C.POINTER(NativeResult)]
    fn.restype = C.c_int
    image = (C.c_uint8 * BANK_SIZE).from_buffer_copy(bank)
    info = phrase_partition(bank, authenticated=True)
    cases = 0
    for mode in (0,1):
        for selector in range(256):
            for x in (0,1,7,31,127,255):
                reference = original_cpu(bank,mode,selector,x)
                out = NativeResult()
                status = fn(image,BANK_SIZE,mode,selector,C.byref(out))
                index = selector & 127
                bounded = mode == 0 or index < 20
                expected_at = (0xA304 if mode == 0 else 0xA404) + 2*index
                expected_end = info["bounds"].get(reference["word"])
                require(status == int(bounded) and out.source_is_indexed_table == bounded,
                        "native source provenance classification mismatch")
                require((out.final_a,out.final_y,out.final_z,out.final_n,out.original_raw_word,
                         out.source_word_cpu_address) ==
                        (reference["a"],reference["y"],reference["z"],reference["n"],
                         reference["word"],expected_at),
                        "original 6502 vs native final registers/ZP pointer divergence")
                require((out.span_start,out.span_end_exclusive) ==
                        ((reference["word"],expected_end) if bounded else (0,0)),
                        "native original phrase-span boundary mismatch")
                cases += 1
    return {"original_6502_vs_compiled_C11_cases":cases,
            "independent_original_gameplay_liveness_proven":False,
            "phrase_audio_semantics_proven":False}


def artificial_bank() -> bytes:
    b = bytearray(BANK_SIZE)
    # A generator, not copied from any original Japanese sound data.
    for i in range(2):
        lo,hi,_ = BLOCKS[i]
        opcode = (bytes.fromhex("bd b7 01 0a a8 b9 04 a3 85 e2 b9 05 a3 85 e3")
                  if i == 0 else bytes.fromhex("a5 06 0a a8 b9 04 a4 85 e2 b9 05 a4 85 e3"))
        b[lo-0x8000:hi-0x8000] = opcode
    root=TABLE_END; p=[]
    for i in range(140):
        p.append(root); root += 9 + (i<63); b[root-0x8000-1]=255
    require(root==POOL_END,"artificial fixture geometry")
    entries=[]; pos=0
    for i in range(148):
        if 104<=i<=110 or i==128: entries.append(p[pos-1])
        else: entries.append(p[pos]); pos+=1
        b[TABLE_START+2*i-0x8000:TABLE_START+2*i-0x8000+2] = entries[-1].to_bytes(2,"little")
    require(pos==140,"fixture root count")
    return bytes(b)


def smoke() -> None:
    b=artificial_bank()
    info=phrase_partition(b,authenticated=False)
    require(info["internal_ff_terminators"]==0,"artificial terminal count")
    for mode in (0,1):
        for selector in range(256):
            value=original_cpu(b,mode,selector,7)
            at=(0xA304 if mode == 0 else 0xA404)+2*(selector&127)
            require(value["word"]==rd(b,at)|(rd(b,at+1)<<8),"original instruction smoke")
    for location in (TABLE_START, TABLE_START+4, TABLE_END+9, POOL_END-1):
        bad=bytearray(b); bad[location-0x8000]^=255
        try:phrase_partition(bytes(bad),authenticated=False)
        except ValueError:continue
        raise AssertionError(f"damaged synthetic source accepted at {location:04X}")
    print("PASS JP0653 148-entry/140-root synthetic phrase partition and 512 opcode replays")


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--native-lib",type=Path,help="private built C11 shared library for original CPU parity")
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--json",type=Path,help="aggregate metadata only")
    args=p.parse_args()
    if not args.rom and not args.smoke:
        p.error("specify --smoke or --rom original-JP cartridge")
    if args.native_lib and not args.rom:
        p.error("--native-lib requires --rom")
    if args.smoke:smoke()
    if args.rom:
        original=args.rom.read_bytes()
        require(len(original)==393232 and hash256(original)==ROM_SHA and
                original[:4]==b"NES\x1a" and (original[6]>>4 | original[7]&240)==24,
                "wrong original Japanese mapper24 cartridge")
        bank=original[16+12*BANK_SIZE:16+13*BANK_SIZE]
        info=phrase_partition(bank,authenticated=True)
        report={k:v for k,v in info.items() if k not in ("entries","bounds")}
        if args.native_lib:
            report.update(native_parity(bank,args.native_lib))
        if args.json:
            args.json.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print("PASS JP0653 original Japanese 148 pointers, 140 roots and 1323 phrase bytes;",
              report.get("original_6502_vs_compiled_C11_cases",0),"compiled parity cases")

if __name__=="__main__":main()
