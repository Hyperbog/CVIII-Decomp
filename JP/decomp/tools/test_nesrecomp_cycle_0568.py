#!/usr/bin/env python3
"""ROM-free external C11 NESRecomp cycle-project adapter contract tests."""
from __future__ import annotations
import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from nesrecomp_cycle_0568 import ROOT,authenticated,commands,validate_engine

def expect_error(action,description):
    try:action()
    except (OSError,ValueError):return
    raise AssertionError(description)

def main():
    with tempfile.TemporaryDirectory(prefix="jp0568-external-") as tmp:
        p=Path(tmp);engine=p/"upstream";engine.mkdir()
        rom=p/"private_jp.nes";rom.write_bytes(b"NES\x1a")
        expect_error(lambda:authenticated(rom),"short ROM passed")
        (engine/"runner/cyc").mkdir(parents=True)
        (engine/"runner/cyc/project.cmake").write_text("# test stub\n")
        (engine/"LICENSE").write_text("PolyForm Noncommercial License 1.0.0\n")
        validate_engine(engine)
        old=engine/"LICENSE";old.write_text("unknown license\n")
        expect_error(lambda:validate_engine(engine),"unknown engine license passed")
        old.write_text("PolyForm Noncommercial License 1.0.0\n")
        out=p/"out"
        cfg,build,run=commands(rom,engine,out,120,True)
        assert cfg[:2]==["cmake","-S"]
        assert cfg.count("-DJP_CYCLE_HEADLESS=ON")==1
        assert cfg.count("-DJP_PPU_IMPLEMENTATION=LLE")==1
        assert cfg[-1]=="-DJP_PPU_IMPLEMENTATION=LLE"
        assert "-DJP_ORIGINAL_JP_ROM="+str(rom) in cfg
        assert "-DNESRECOMP_EXTERNAL_ROOT="+str(engine) in cfg
        assert build[:2]==["cmake","--build"]
        assert run[-2:]==["--frames","120"]
        cfg_hle, _, _ = commands(rom,engine,out,120,True,ppu_impl="HLE")
        assert cfg_hle.count("-DJP_PPU_IMPLEMENTATION=HLE")==1
        assert "-DJP_PPU_IMPLEMENTATION=LLE" not in cfg_hle
        expect_error(lambda:commands(rom,engine,out,120,True,ppu_impl="BAD"),
                     "unknown PPU backend accepted")
        expect_error(lambda:commands(rom,engine,out,0,True),"zero frames accepted")
        expect_error(lambda:commands(rom,engine,out,12001,True),"unbounded frames accepted")
    print("PASS JP0568 C11 external cycle runner commands, mapper24 ROM gate, "
          "license and non-vendoring policy")

if __name__=="__main__":main()
