#!/usr/bin/env python3
"""JP0623 strict fifth-layer pinned NESRecomp SDL Start/Pause source gate.

Never copies upstream source or generates distributable proprietary bytes.
The --smoke test exercises synthetic source; --source authenticates real
pinned upstream Git blob and runs all five genuine patch generators.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
PRODUCT=HERE.parents[1]/'recomp'/'tools'
def imp(path:Path)->Any:
    spec=importlib.util.spec_from_file_location("_jp0623_"+path.stem,path)
    if spec is None or spec.loader is None:raise ValueError("Module missing")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def require(test:bool,message:str)->None:
    if not test:raise ValueError("JP0623 "+message)

def final_check(src:str)->dict:
    marker="CVIII_START_PAUSE_0623"
    require(src.count(marker)==1,"wrong Start/Pause marker count")
    require(src.count('#include "cviii_start_host_0623.h"')==1,
            "missing start menu owner API")
    require(src.count("cviii_pause_key(&ev.key)")==1,"wrong keyboard hook count")
    require(src.count("cviii_pause_button(ev.cbutton.button)")==1,
            "wrong gamepad hook count")
    event=src[src.index("else if (ev.type == SDL_KEYDOWN) {"):]
    a=event.index("cviii_pause_key(&ev.key)")
    b=event.index("cviii_audio_menu_key(&ev.key)")
    c=event.index("cviii_stage_key(&ev.key)")
    d=event.index("dev_key(ev.key.keysym.scancode)")
    require(a<b<c<d,"F4/F6/F10/developer key ownership not ordered")
    require("if (online || (!open && !inactive))" in src and
            "cyc_run_frame();" in src,"original emulation pause gate lost")
    require("if (was_open && !open)" in src and
            "hold_input = true;" in src,"host input release barrier lost")
    require(src.count("|| cviii_pause_active();")>=2,
            "Start/Pause omitted from both modal frame predicates")
    require("SDL_ClearQueuedAudio(dev)" in src,
            "old buffered audio not cleared on modal open")
    require("cviii_pause_action(cviii_pause_accept())" in src,
            "action selection not bound")
    require("case CVIII_START_SAVE:" in src and
            "(void)save_state_slot();" in src and
            "case CVIII_START_LOAD:" in src and
            "(void)load_state_slot();" in src,
            "Save/Load must reuse host's full-machine serializer")
    require("case CVIII_START_AUDIO:" in src and
            "cviii_audio_menu_toggle()" in src,
            "Audio must delegate to existing original-art modal")
    require("case CVIII_START_QUIT:" in src and
            "s_running=false;" in src,
            "Quit must be a host action, not emulated RAM mutation")
    require("!cviii_pause_active()" in src,
            "host shortcuts still active inside modal")
    require("SDL_CONTROLLER_BUTTON_A" in src and
            "SDL_CONTROLLER_BUTTON_B" in src,
            "gamepad menu acceptance/back missing")
    require("CVIII_PASSWORD_BOOTSTRAP_0596" in src and
            "CVIII_SAVE_SLOTS_0591" in src,
            "previous patch layers missing")
    return {
        "keyboard_priority":"F4 Pause > F6 Audio > F10 Password > Dev",
        "five_layers":["0591","0594","0596","0620","0623"],
        "pause_and_input_release_static_checks":"pass",
        "native_compilation_verified":False,
        "gameplay_input_or_savestate_execution_verified":False
    }

def smoke()->None:
    gate=imp(HERE/"jp_audio_menu_pinned_gate_0621.py")
    patch=imp(PRODUCT/"patch_cyc_start_menu_0623.py")
    gate.smoke()
    patch.smoke()
    assert gate.canonical_checkout_bytes(b"a\r\nb\r\n")==b"a\nb\n"
    print("PASS JP0623 synthetic fifth-layer source guard and dependency gates")

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--source",type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if a.source is None:p.error("--source required; synthetic smoke is not enough")
    gate=imp(HERE/"jp_audio_menu_pinned_gate_0621.py")
    patch=imp(PRODUCT/"patch_cyc_start_menu_0623.py")
    data=gate.canonical_checkout_bytes(a.source.read_bytes())
    git_sha=gate.git_blob_sha(data)
    require(git_sha==gate.PINNED_SDL_GIT_BLOB,
            "upstream Git blob drift "+git_sha)
    original=data.decode("utf-8")
    first,second,third,fourth=gate.chain(original)
    gate.verify_final(original,(first,second,third,fourth))
    fifth=patch.generate(fourth)
    result=final_check(fifth)
    result["upstream_git_blob"]=git_sha
    result["native_source_bytes"]=len(fifth)
    print(json.dumps(result,sort_keys=True))
    print("PASS JP0623 actual pinned five-layer SDL source and Pause action gates")

if __name__=="__main__":main()
