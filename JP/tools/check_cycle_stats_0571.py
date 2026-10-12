#!/usr/bin/env python3
"""0571: enforce meaningful compiled-C cycle evidence for the synthetic VRC6 smoke.

Statistics come from the external pinned NESRecomp headless runner.
100% synthetic native execution is NOT original retail game compatibility.
"""
from __future__ import annotations
import argparse,re,sys
from pathlib import Path

SUMMARY=re.compile(r"mode=native\s+frames=(\d+)\s+cycles=(\d+)\s+native_cycles=(\d+)")
FALLBACK=re.compile(r"interpreted:\s+ROM\s+(\d+)\s+\([^\n]*?RAM\s+(\d+)")

def check(s:str, frames:int)->dict:
    m=SUMMARY.search(s)
    if not m:raise ValueError("external runner did not report a native cycle summary")
    actual,total,native=map(int,m.groups())
    if actual!=frames or not 1<=frames<=12000:
        raise ValueError(f"expected {frames} complete frames, runner reported {actual}")
    if total<10000*frames or native>total or native*100<total*99:
        raise ValueError(f"synthetic VRC6 ROM native coverage too low: {native}/{total}")
    fallback=FALLBACK.search(s)
    if not fallback:raise ValueError("external interpreter counters absent")
    rom,ram=map(int,fallback.groups())
    if rom or ram:raise ValueError(f"synthetic mapper24 test interpreted instructions: ROM={rom}, RAM={ram}")
    return {"frames":actual,"total_cpu_cycles":total,"native_cpu_cycles":native,
            "native_fraction":native/total,"interpreted_rom":rom,
            "interpreted_ram":ram,"media":"synthetic mapper24 VRC6",
            "original_gameplay_parity_verified":False}

def expect_fail(output:str):
    try:check(output,3)
    except ValueError:return
    raise AssertionError("bad cycle/ROM-fallback report accepted")

def smoke():
    good=("mode=native frames=3 cycles=86958 native_cycles=86951 (100.0%)\n"
          "  interpreted: ROM 0 (0.0%, add to cycle_seed_file)"
          "  RAM 0 (0.0%, CPU RAM code no view covers: --capture-log)\n")
    result=check(good,3)
    assert result["total_cpu_cycles"]==86958
    assert result["native_cpu_cycles"]==86951
    expect_fail(good.replace("frames=3","frames=2"))
    expect_fail(good.replace("native_cycles=86951","native_cycles=574"))
    expect_fail(good.replace("ROM 0","ROM 1"))
    expect_fail(good.replace("RAM 0","RAM 1"))
    expect_fail(good.replace("cycles=86958","cycles=0"))
    expect_fail("process success without original native-cycle stats")
    print("PASS JP0571 independent external native cycle/fallback metrics gate")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--log",type=Path)
    p.add_argument("--frames",type=int,default=3)
    args=p.parse_args()
    if args.smoke:smoke()
    elif args.log:
        report=check(args.log.read_text(encoding="utf-8"),args.frames)
        print("PASS JP0571 upstream C11 mapper24 headless synthetic: "
              f'{report["native_cpu_cycles"]}/{report["total_cpu_cycles"]} '
              "native CPU cycles, zero interpreted ROM/RAM")
    else:p.error("--smoke or --log required")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError,AssertionError) as e:
        print("JP0571 FAIL "+str(e),file=sys.stderr);raise SystemExit(2)
