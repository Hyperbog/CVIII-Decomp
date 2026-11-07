#!/usr/bin/env python3
"""Build genuine original-JP NESRecomp compiled PRG in an owner-private folder.

Unlike the baseline interpreter+four native boot instructions, this invokes
the pinned NESRecomp STATIC 6502-to-C compiler, compiles per-bank C views, and
optionally uses a private gameplay route solely to discover reachable code.
MesenCE is NOT a correctness oracle or build prerequisite. No ROM or generated
ROM-equivalent C is written into the public repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROM_SHA256="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
PINNED={
  "recompiler/src/cyc_codegen.c":
    "cfc1eb56250a1a59f4daa9bf1f34bdc827eb8e42d8ad4bf40038c27b18177d63",
  "runner/cyc/cyc.cmake":
    "f230354276bff506c7f3e773a28c8e1c333cda967df7531f71a0f3e61a25d739",
  "runner/cyc/cpu6502_interp.c":
    "857eb5106cd5c310671465333bc0b4b667c260c9432f93cabb69b8f46851bfc8",
}
PREFIX="cviii_jp"
def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def run(args, cwd=None):
    print("RUN", Path(str(args[0])).name, *[str(x) for x in args[1:4]], flush=True)
    subprocess.run([str(x) for x in args],cwd=cwd,check=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path,required=True)
    p.add_argument("--nesrecomp-root",type=Path,required=True,
                   help="Pinned 2b4fcdb98c9e702be3fb365cfc645003c50b5fc1 source")
    p.add_argument("--private-build",type=Path,required=True,
                   help="OUTSIDE Git; generated code and ROM-derived seeds stay private")
    p.add_argument("--input",type=Path,
                   help="Optional owner-private native .input route")
    p.add_argument("--frames",type=int,default=2100,
                   help="Number of frames to discover with --input (default 2100)")
    p.add_argument("--verify",action="store_true",
                   help="Compare compiled vs interpreter machine-state hashes on same NES hardware model")
    a=p.parse_args()
    repo=Path(__file__).resolve().parents[3]
    out=a.private_build.resolve()
    rom=a.rom.resolve()
    root=a.nesrecomp_root.resolve()
    if out==repo or repo in out.parents:
        p.error("generated original-ROM-equivalent C must stay outside the Git checkout")
    if not 1<=a.frames<=25000:p.error("--frames must be 1..25000")
    if a.verify and not a.input:p.error("--verify requires an input route")
    if not rom.is_file() or rom.stat().st_size!=393232 or sha(rom)!=ROM_SHA256:
        p.error("original Japanese Mapper24 ROM SHA-256/size mismatch")
    for rel,h in PINNED.items():
        v=root/rel
        if not v.is_file() or sha(v)!=h:
            p.error("pinned NESRecomp source identity mismatch: "+rel)
    if a.input and not a.input.is_file():p.error("missing private gameplay input")
    out.mkdir(parents=True,exist_ok=True)
    generator_build=out/"static-compiler"
    run(["cmake","-S",root/"recompiler","-B",generator_build,
         "-DCMAKE_BUILD_TYPE=Release"])
    run(["cmake","--build",generator_build,"--parallel","4"])
    tool=generator_build/"NESRecomp"
    generated=out/"generated"
    def generate(seed:Path|None=None):
        args=[tool,rom,"--cycle-accurate","--output-prefix",PREFIX]
        if seed:args.extend(["--cycle-seed-file",seed])
        run(args,cwd=out)
        files=list(generated.glob(PREFIX+"_cyc*.c"))
        if len(files)<2:raise RuntimeError("no compiled 6502 PRG bank sources produced")
        return len(files)
    units=generate()
    native_build=out/"native-build"
    run(["cmake","-S",repo/"JP/recomp/native/rom_runtime_0732",
         "-B",native_build,f"-DNESRECOMP_EXTERNAL_ROOT={root}",
         f"-DCVIII_JP_COMPILED_C_DIR={generated}",
         "-DJP0732_WINDOWED=OFF","-DCMAKE_BUILD_TYPE=Release"])
    def compile_native():
        run(["cmake","--build",native_build,"--parallel","4"])
        binary=native_build/"jp_akumajou_runtime_0732"
        if not binary.is_file():raise RuntimeError("compiled native runtime missing")
        return binary
    binary=compile_native()
    seed=None
    if a.input:
        seed=out/"private_reachable_pc.miss"
        run([binary,rom,"--headless","--edition","original",
             "--frames",str(a.frames),"--input",a.input.resolve(),
             "--miss-log",seed])
        units=generate(seed)
        binary=compile_native()
    result={"schema":"cviii-native-recompiled-jp/v1",
            "rom_sha256":ROM_SHA256,
            "engine_pinned":"2b4fcdb98c9e702be3fb365cfc645003c50b5fc1",
            "compiled_c_units":units,
            "binary":str(binary),
            "private_generated_dir":str(generated),
            "proof":"build and guest machine execution, not independent NES hardware or full-game parity",
            "original_source_admission_bytes_added":0}
    if a.verify:
        compiled=out/"compiled.machinehash"
        interpreted=out/"interpreter.machinehash"
        common=[rom,"--headless","--edition","original",
                "--frames",str(a.frames),"--input",a.input.resolve()]
        run([binary,*common,"--hash-out",compiled])
        run([binary,*common,"--interp-only","--hash-out",interpreted])
        if compiled.read_bytes()!=interpreted.read_bytes():
            raise RuntimeError("compiled game != 6502 interpreter on machine-state hashes")
        frames=len(compiled.read_text().splitlines())
        if frames!=a.frames:raise RuntimeError("short native verification run")
        result["same_hardware_compiled_interpreter_frames_identical"]=frames
        print(f"PASS compiled CPU execution == interpreter machine-state for {frames} frames")
    (out/"private_recomp_result.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("COMPILED ORIGINAL JP PRG C SOURCES:",units)
    print("PRIVATE NATIVE EXECUTABLE:",binary)
    print("No original game source, private inputs or generated ROM-equivalent C committed.")
if __name__=="__main__":
    main()
