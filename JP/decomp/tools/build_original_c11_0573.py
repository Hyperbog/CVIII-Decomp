#!/usr/bin/env python3
"""JP0573: persist a native C11 executable compiled from the authenticated JP ROM.

Reuses the existing 0562/0563 source and CPU pipelines. Original ROM and
ROM-derived generated C remain strictly private in the chosen build directory;
never run with output in this Git repository.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from build_fullbank_0a_source import build as recover_original
from build_whole_cart_recomp_0529 import assemble
from static_recompile_bank0a import source_cases,JP_SHA,BANK_SHA
from static_recompile_c_0562 import generate
from test_static_bank0a_0552 import bounded_cases
from test_raw0a_lookup_cpu import run as reference_cpu

ROOT=Path(__file__).resolve().parents[3]
C=ROOT/"JP/recomp/native/c6502"

def authenticated(path:Path)->tuple[bytes,bytes]:
    rom=path.read_bytes()
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP_SHA:
        raise ValueError("wrong Japanese retail ROM SHA-256")
    bank=rom[16+10*16384:16+11*16384]
    if hashlib.sha256(bank).hexdigest()!=BANK_SHA:
        raise ValueError("physical VRC6 raw0A SHA-256 drift")
    return rom,bank

def compile_c(cc:str,code:Path,output:Path)->None:
    command=[cc,"-std=c11","-O2","-Wall","-Wextra","-Werror",
       "-pedantic","-I"+str(C),str(C/"cpu.c"),
       str(C/"opcode_table.c"),str(C/"raw0a_driver_0563.c"),
       str(code),"-o",str(output)]
    subprocess.run(command,check=True)

def synthetic_smoke(cc:str)->None:
    rows=[
        dict(pc=0x801e,category="audited",opcode=0xa5,arg=0x34,next=0x8020),
        dict(pc=0x8020,category="candidate",opcode=0x0a,arg=0,next=0x8021)]
    with tempfile.TemporaryDirectory(prefix="jp0573-") as tmp:
        path=Path(tmp)
        src=path/"sample.c";src.write_text(generate(rows))
        subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror",
          "-pedantic","-I"+str(C),"-c",str(src),"-o",str(path/"sample.o")],check=True)
        try:generate(list(reversed(rows)))
        except ValueError:pass
        else:raise AssertionError("unsorted source instruction sites accepted")
        print("PASS JP0573 synthetic ROM-free C11 generator and assembler gate")

def build(rom_path:Path,out:Path,cc:str)->dict:
    original,bank=authenticated(rom_path)
    out=out.resolve();root=ROOT.resolve()
    if out==root or root in out.parents:
        raise ValueError("original-ROM derived C/build output must be OUTSIDE Git repository")
    out.mkdir(parents=True,exist_ok=True)
    src=out/"original_source"
    recover_original(original,src)
    asm=(src/"banked/prg_raw0a.asm").read_text(encoding="ascii")
    if assemble(asm,0x8000,0x4000)!=bank:
        raise ValueError("authentic original 6502 source does not reassemble")
    rows,counts=source_cases(asm,bank)
    if len(rows)!=2357 or counts["audited_instructions"]!=992:
        raise ValueError("original bank0A code-site inventory drift")
    generated=out/"bank0a_compiled.c"
    generated.write_text(generate(rows),encoding="utf-8")
    exe=out/"jp_original_selector_c11"
    compile_c(cc,generated,exe)
    cases=bounded_cases(bank)
    if len(cases)!=135:raise ValueError("expected 135 producer-bounded selectors")
    csv=out/"selector_cases.csv"
    csv.write_text("".join(f"{x},{y},{z}\n" for x,y,z,*_ in cases))
    result=subprocess.run([str(exe),str(rom_path.resolve()),str(csv)],
          check=True,text=True,capture_output=True)
    actual=[tuple(int(x) for x in line.split(",")) for line in result.stdout.splitlines()]
    if len(actual)!=len(cases):
        raise ValueError("wrong C11 selector return count")
    for index,(expected,observed) in enumerate(zip(cases,actual)):
        x,y,z,p1,p2,p3=expected
        reference=reference_cpu(bank,x,y,z)
        if observed!=expected or tuple(reference[:3])!=(p1,p2,p3):
            raise ValueError(f"original CPU/native C mismatch case {index}: {expected} vs {observed}")
    report=dict(schema="JP0573-original-rom-recompiled-C11-selector/v1",
      rom_sha256=JP_SHA,original_reassembly_exact=True,
      generated_bank0a_sites=len(rows),audited_sites=992,
      independently_matched_selector_cases=len(cases),
      compiled_selector_fallback_calls=0,
      local_executable=str(exe),
      original_gameplay_frames_tested=0,nesrecomp_cycle_engine_linked=False,
      strict_prg_bytes_added=0,vpp_points_added=0)
    (out/"jp0573_build_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("PASS JP0573 original ROM: compiled C11 executable and 135/135 selector CPU parity")
    print(json.dumps(report,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--rom",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--cc",default="cc")
    args=p.parse_args()
    if not shutil.which(args.cc):raise ValueError("C11 compiler unavailable")
    if args.smoke:synthetic_smoke(args.cc)
    elif args.rom and args.out:build(args.rom,args.out,args.cc)
    else:p.error("provide --rom ORIGINAL_JP.nes --out /private/build or --smoke")

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:
        print("JP0573 FAIL: "+str(exc),file=sys.stderr);raise SystemExit(2)
