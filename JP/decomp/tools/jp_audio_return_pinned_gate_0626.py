#!/usr/bin/env python3
"""JP0626 strict pinned SDL seven-layer nested Pause/Audio source gate.

--smoke is ROM-free and host-independent. --source requires the exact pinned
upstream cyc_sdl.c Git blob and executes all seven actual patch generators.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

TOOLS=Path(__file__).resolve().parent

def load(filename:str)->Any:
    path=(TOOLS.parents[1]/'recomp'/'tools' if filename.startswith('patch_cyc_') else TOOLS)/filename
    spec=importlib.util.spec_from_file_location("_jp0626_"+path.stem,path)
    if spec is None or spec.loader is None:
        raise ValueError("missing module: "+filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def require(condition:bool,message:str)->None:
    if not condition:raise ValueError("JP0626 "+message)

def final_check(source:str)->dict:
    require(source.count("CVIII_AUDIO_RETURN_0626")==1,
            "exactly one final seventh-layer marker required")
    require(source.count("cviii_pause_audio_enter()")==1,
            "Audio entry must preserve its resident Pause parent")
    a=source.index("    case CVIII_START_AUDIO:")
    b=source.index("    case CVIII_START_QUIT:",a)
    action=source[a:b]
    require("cviii_pause_audio_enter()" in action and
            "cviii_pause_close();" not in action,
            "Audio action must not discard parent selection")
    require("cviii_audio_menu_toggled=true;" in action,
            "PCM input ownership transition flag lost")
    # F6 closing the child must restore the parent in the *same SDL
    # event batch*, not just in the end-of-frame global open predicate.
    require(source.count(
        "open=menu_open() || cviii_stage_open || cviii_audio_menu_active() ||\n"
        "                         cviii_pause_active();")==1,
        "Audio event completion must keep gameplay paused when parent resumes")
    key=source[source.index("else if (ev.type == SDL_KEYDOWN) {"):]
    require(key.index("cviii_pause_key(&ev.key)") <
            key.index("cviii_audio_menu_key(&ev.key)") <
            key.index("cviii_stage_key(&ev.key)") <
            key.index("dev_key(ev.key.keysym.scancode)"),
            "F4/F6/F10/developer input precedence changed")
    require("if (was_open && !open)" in source and
            "hold_input = true;" in source and
            "if (online || (!open && !inactive))" in source,
            "original frame-pause and input-release gates missing")
    require("case CVIII_START_SAVE:" in source and
            "cviii_pause_slot_begin(action,cviii_save_slot)" in source,
            "Save/Load child slot picker missing")
    return {
        "seven_layers":["0591","0594","0596","0620","0623","0625","0626"],
        "parent_kept_behind_audio":True,
        "same_event_pause_ownership":True,
        "native_windows_link_or_gameplay_verified":False
    }

def smoke()->None:
    module=load("patch_cyc_audio_return_0626.py")
    module.smoke()
    print("PASS JP0626 seventh-layer guard; full pinned source requires --source")

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--source",type=Path)
    args=parser.parse_args()
    if args.smoke:smoke();return
    if args.source is None:parser.error("--source required for actual upstream")
    base=load("jp_audio_menu_pinned_gate_0621.py")
    stage5=load("jp_start_menu_pinned_gate_0623.py")
    stage6=load("jp_slot_picker_pinned_gate_0625.py")
    data=base.canonical_checkout_bytes(args.source.read_bytes())
    identity=base.git_blob_sha(data)
    require(identity==base.PINNED_SDL_GIT_BLOB,
            "upstream Git blob differs from strict pinned NESRecomp source")
    original=data.decode("utf-8")
    four=base.chain(original)
    base.verify_final(original,four)
    fifth=load("patch_cyc_start_menu_0623.py").generate(four[3])
    stage5.final_check(fifth)
    sixth=load("patch_cyc_slot_picker_0625.py").generate(fifth)
    stage6.final_check(sixth)
    seventh=load("patch_cyc_audio_return_0626.py").generate(sixth)
    result=final_check(seventh)
    result["pinned_source_git_blob"]=identity
    result["generated_source_bytes"]=len(seventh.encode("utf-8"))
    print(json.dumps(result,sort_keys=True))
    print("PASS JP0626 exact pinned 7-stage SDL Pause->Audio->Pause contract")

if __name__=="__main__":main()
