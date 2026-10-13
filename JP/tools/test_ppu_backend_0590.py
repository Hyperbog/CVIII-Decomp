#!/usr/bin/env python3
"""JP0590 background-renderer A/B backend selector (no ROM reconstruction)."""
from pathlib import Path
from nesrecomp_cycle_0568 import commands

def main():
    rom=Path("/private/japanese.nes")
    engine=Path("/external/nesrecomp")
    out=Path("/private/diagnostic-build")
    def arguments(mode):
        cfg,_,_=commands(rom,engine,out,120,True,mode)
        return cfg
    assert "-DJP_PPU_IMPLEMENTATION=LLE" in arguments("LLE")
    assert "-DJP_PPU_IMPLEMENTATION=HLE" in arguments("HLE")
    for mode in ("hle","NO", "HLE;rm -rf", ""):
        try:arguments(mode)
        except ValueError:pass
        else:raise AssertionError("invalid PPU mode accepted "+mode)
    print("PASS JP0590 Original LLE default, opt-in HLE, invalid modes rejected")
if __name__=="__main__":main()
