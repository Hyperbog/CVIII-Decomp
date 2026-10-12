#!/usr/bin/env python3
"""0568 optional external NESRecomp C11 cycle backend for Japanese mapper24.

Runs external PolyForm Noncommercial NESRecomp without copying any of its
source into this repository. The ROM and generated C stay on the user's
machine; public CI uses only synthetic interface checks.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_SIZE=393232

def authenticated(path:Path)->dict:
    data=path.read_bytes()
    if len(data)!=ROM_SIZE or hashlib.sha256(data).hexdigest()!=ROM_SHA:
        raise ValueError("Japanese original ROM fingerprint/size mismatch")
    if data[:4]!=b"NES\x1a" or (data[6]>>4)|(data[7]&0xf0)!=24:
        raise ValueError("Original ROM must be iNES mapper 24 (Konami VRC6a)")
    if data[4]!=16 or data[5]!=16:
        raise ValueError("Expected 256 KiB PRG and 128 KiB CHR")
    return {"sha256":ROM_SHA,"size":ROM_SIZE,"mapper":24,"prg_bytes":262144,"chr_bytes":131072}

def validate_engine(engine:Path)->None:
    if not (engine/"runner/cyc/project.cmake").is_file():
        raise ValueError("External NESRecomp cycle-project CMake interface is absent")
    lic=engine/"LICENSE"
    if not lic.is_file() or "PolyForm Noncommercial License 1.0.0" not in lic.read_text(encoding="utf-8")[:400]:
        raise ValueError("NESRecomp external noncommercial license unrecognized; review manually")
    if engine==ROOT or ROOT in engine.parents:
        raise ValueError("The external NESRecomp checkout must be outside the CVIII repository")

def commands(rom:Path,engine:Path,out:Path,frames:int,headless:bool)->tuple[list[str],list[str],list[str]]:
    if frames<1 or frames>12000:
        raise ValueError("Bounded frame count must be 1..12000")
    opts=["cmake","-S",str(ROOT/"JP/native/nesrecomp_cycle"),"-B",str(out),
          "-DNESRECOMP_EXTERNAL_ROOT="+str(engine),
          "-DJP_ORIGINAL_JP_ROM="+str(rom),
          "-DJP_CYCLE_HEADLESS="+("ON" if headless else "OFF")]
    build=["cmake","--build",str(out),"--config","Release","--parallel","4"]
    return opts,build,[str(out/"jp_akumajou_densetsu"),str(rom),"--frames",str(frames)]

def run(args)->dict:
    rom=args.rom.resolve(strict=True);engine=args.engine.resolve(strict=True)
    out=args.out.resolve()
    if out==ROOT or ROOT in out.parents or out==engine or engine in out.parents:
        raise ValueError("Build output must be separate from source repositories")
    rom_meta=authenticated(rom)
    validate_engine(engine)
    configure,build,execute=commands(rom,engine,out,args.frames,not args.windowed)
    if args.plan:
        return {"schema":"JP0568-external-cycle-plan/v1","rom":rom_meta,
                "external_engine":str(engine),"configure":configure,
                "build":build,"execute":execute,"execution_confirmed":False,
                "gameplay_parity":False}
    out.mkdir(parents=True,exist_ok=True)
    logs={}
    for name,command in (("configure",configure),("build",build)):
        result=subprocess.run(command,capture_output=True,text=True)
        (out/(name+".log")).write_text(result.stdout+"\n"+result.stderr,encoding="utf-8")
        logs[name]={"returncode":result.returncode,
                    "log":str(out/(name+".log"))}
        if result.returncode:
            raise RuntimeError(f"External NESRecomp {name} failed with exit {result.returncode}; "
                               f"inspect {out/(name+'.log')}")
    exe_candidates=[out/"jp_akumajou_densetsu",
                    out/"jp_akumajou_densetsu.exe",
                    out/"Release/jp_akumajou_densetsu.exe",
                    out/"Release/jp_akumajou_densetsu"]
    exe=next((p for p in exe_candidates if p.is_file()),None)
    if exe is None:
        raise RuntimeError("The external C11 cycle runner did not produce jp_akumajou_densetsu")
    execute[0]=str(exe)
    proc=subprocess.run(execute,capture_output=True,text=True,
                        timeout=max(120,min(1800,args.frames*3)))
    (out/"headless_run.log").write_text(proc.stdout+"\n"+proc.stderr,encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(f"External cycle runner exited {proc.returncode}; "
                           f"inspect {out/'headless_run.log'}")
    report={"schema":"JP0568-external-cycle-run/v1","rom":rom_meta,
            "external_engine":str(engine),"headless":not args.windowed,
            "requested_frames":args.frames,"process_exited_zero":True,
            "runner":str(exe),"log":str(out/"headless_run.log"),
            "logs":logs,"original_cpu_trace_compared":False,
            "mesen_frame_parity":False,"strict_prg_new_bytes":0,
            "new_vpp_points":0}
    (out/"jp_cycle_0568.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--validate-rom",type=Path,
                   help="Validate retail iNES identity without an engine")
    p.add_argument("--rom",type=Path)
    p.add_argument("--engine",type=Path,
                   help="Separately obtained PolyForm Noncommercial NESRecomp checkout")
    p.add_argument("--out",type=Path)
    p.add_argument("--frames",type=int,default=120)
    p.add_argument("--windowed",action="store_true")
    p.add_argument("--plan",action="store_true")
    a=p.parse_args()
    if a.validate_rom is not None:
        print(json.dumps(authenticated(a.validate_rom),sort_keys=True))
    else:
        if not all((a.rom,a.engine,a.out)):p.error("--rom --engine --out are required")
        print(json.dumps(run(a),indent=2,sort_keys=True))
if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        print("JP0568 ERROR: "+str(exc),file=sys.stderr)
        raise SystemExit(2)
