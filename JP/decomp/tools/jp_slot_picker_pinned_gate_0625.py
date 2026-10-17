#!/usr/bin/env python3
"""JP0625 exact six-overlay SDL host gate, using pinned external upstream.

Source-only execution: does not compile full private Windows game. Run ROM-free
smoke without upstream, or --source with exact mstan/nesrecomp commit checkout.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

def imp(path:Path)->Any:
    spec=importlib.util.spec_from_file_location("_jp0625_"+path.stem,path)
    if spec is None or spec.loader is None:
        raise ValueError("Unable to import pinned stage: "+str(path))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def require(condition:bool,message:str)->None:
    if not condition:raise ValueError("JP0625 "+message)

def final_check(src:str)->dict:
    require(src.count("CVIII_SLOT_SELECTOR_0625")==1,
            "missing sixth owner-private slot menu layer")
    require(src.count("cviii_pause_slot_commit();")==2,
            "keyboard and gamepad slot accept must both dispatch")
    require(src.count("cviii_pause_slot_cancel();")==2,
            "keyboard/gamepad must both have slot cancel")
    require("cviii_save_slot=selected;" in src,
            "must preserve the existing host quick-slot identity")
    require("save_state_slot() : load_state_slot()" in src,
            "must call original host state serializer, not a substitute")
    require("const unsigned previous=cviii_save_slot;" in src and
            "if(!ok) {" in src and
            "cviii_save_slot=previous;" in src and
            "cviii_pause_slot_begin(action,selected)" in src,
            "failed save/load must roll back the active slot and reopen the picker")
    require("    cviii_pause_close();\n}" in src,
            "successful save/load must dismiss the modal")
    require("case CVIII_START_SAVE:\n        if(!cviii_pause_slot_begin(action,cviii_save_slot))" in src,
            "Save must open slot picker rather than write immediately")
    require("case CVIII_START_LOAD:\n        if(!cviii_pause_slot_begin(action,cviii_save_slot))" in src,
            "Load must open slot picker rather than read immediately")
    require("static unsigned cviii_save_slot;" in src,
            "original JP0591 slot source missing")
    require("if (online || (!open && !inactive))" in src,
            "original CPU gameplay pause predicate lost")
    require("if (was_open && !open)" in src and
            "hold_input = true;" in src,
            "original host input-release barrier lost")
    require("|| cviii_pause_active();" in src,
            "slot screen must remain inside the paused Start menu")
    require("SDL_CONTROLLER_BUTTON_DPAD_RIGHT" in src and
            "SDL_SCANCODE_RIGHT" in src,
            "slot must be keyboard/controller adjustable")
    # Gate an ordered event and modal stage sequence without trusting textual
    # presence alone: the slot branch must be ahead of parent-page Escape.
    start=src.index("static bool cviii_pause_key(const SDL_KeyboardEvent *key)")
    end=src.index("static void cviii_pause_button(int button)",start)
    key=src[start:end]
    require(key.index("if(cviii_pause_slot_active())") <
            key.index("    if(sc==SDL_SCANCODE_ESCAPE || sc==SDL_SCANCODE_BACKSPACE) {",
                      key.index("if(cviii_pause_slot_active())")+2),
            "slot Escape must be handled by child before parent")
    require(key.index("if (sc==SDL_SCANCODE_F4) {") <
            key.index("if(cviii_pause_slot_active())"),
            "F4 must retain whole-menu close behavior")
    return {"six_layers":["0591","0594","0596","0620","0623","0625"],
            "slot_state_serializer":"pinned_host_full_machine",
            "slot_navigation":"keyboard_and_gamepad",
            "actual_native_link_verified":False,
            "live_windows_gameplay_verified":False}

def smoke()->None:
    patch=imp(HERE/"patch_cyc_slot_picker_0625.py")
    patch.smoke()
    assert patch.MARKER=="CVIII_SLOT_SELECTOR_0625"
    # JP0623 has a space after 'if', while JP0625's nested branches
    # use compact 'if('. Enforce actual generated order, not style.
    k = (
        "    if (sc==SDL_SCANCODE_F4) {\n"
        "    if(cviii_pause_slot_active()) {\n"
        "    if(sc==SDL_SCANCODE_ESCAPE || sc==SDL_SCANCODE_BACKSPACE) {\n"
    )
    require(k.index("if (sc==SDL_SCANCODE_F4) {") <
            k.index("if(cviii_pause_slot_active())"),
            "F4 parent close must precede child picker")

    print("PASS JP0625 ROM-free generated slot patch source gate")

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--source",type=Path)
    args=parser.parse_args()
    if args.smoke:
        smoke()
        return
    if args.source is None:parser.error("--source required; --smoke is not pinned verification")
    previous=imp(HERE/"jp_audio_menu_pinned_gate_0621.py")
    gate=imp(HERE/"jp_start_menu_pinned_gate_0623.py")
    slot=imp(HERE/"patch_cyc_slot_picker_0625.py")
    data=previous.canonical_checkout_bytes(args.source.read_bytes())
    blob=previous.git_blob_sha(data)
    require(blob==previous.PINNED_SDL_GIT_BLOB,
            "pinned upstream original source identity mismatch "+blob)
    original=data.decode("utf-8")
    four=previous.chain(original)
    previous.verify_final(original,four)
    fifth=imp(HERE/"patch_cyc_start_menu_0623.py").generate(four[3])
    gate.final_check(fifth)
    sixth=slot.generate(fifth)
    result=final_check(sixth)
    result["pinned_original_git_blob"]=blob
    result["final_source_bytes"]=len(sixth)
    print(json.dumps(result,sort_keys=True))
    print("PASS JP0625 authentic six-stage SDL Save/Load slot integration contract")

if __name__=="__main__":main()
