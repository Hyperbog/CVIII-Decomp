#!/usr/bin/env python3
"""JP0625: strict C11 execute actual sixth-layer slot shell, offline and netplay.

No SDL libraries, original ROM or live machine state are required. Does not
claim full Windows SDL integration, gameplay pause or real save-file success.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

TOOLS=Path(__file__).resolve().parent
SOURCE=TOOLS.parent/"native"/"enhanced"

def imp(path:Path)->Any:
    spec=importlib.util.spec_from_file_location("_jp0625test_"+path.stem,path)
    if spec is None or spec.loader is None:raise ValueError("missing "+str(path))
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

SHIM=r'''
/* JP0625 shim uses the real game-owned slot controller. */
#include "cviii_slot_picker_0625.h"
static CviiiSlotPicker slot_picker;
static unsigned cviii_save_slot;
int cviii_pause_slot_active(void)
{
 return cviii_pause_active() && cviii_slot_active(&slot_picker);
}
int cviii_pause_slot_begin(int action,unsigned current_slot)
{
 return cviii_pause_active() &&
        cviii_slot_begin(&slot_picker,(CviiiStartAction)action,current_slot);
}
void cviii_pause_slot_cancel(void){cviii_slot_cancel(&slot_picker);}
int cviii_pause_slot_step(int direction)
{
 return cviii_pause_active() && cviii_slot_step(&slot_picker,direction);
}
int cviii_pause_slot_accept(unsigned *chosen)
{
 if(!cviii_pause_active())return CVIII_START_NONE;
 return (int)cviii_slot_accept(&slot_picker,chosen);
}
'''
END=r'''
static int saved_slot=-1,loaded_slot=-1;
static bool save_state_slot(void)
{
 save_calls++;saved_slot=(int)cviii_save_slot;return true;
}
static bool load_state_slot(void)
{
 load_calls++;loaded_slot=(int)cviii_save_slot;return true;
}
static SDL_KeyboardEvent key(SDL_Scancode sc,int repeat)
{
 SDL_KeyboardEvent e={{sc},repeat};return e;
}
int main(void)
{
 assert(cviii_start_defaults(&game_menu));
 cviii_start_seal(&game_menu);
 SDL_KeyboardEvent e=key(SDL_SCANCODE_F4,0);
#ifdef NESRECOMP_NET
 netplay_on=1;
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 netplay_on=0;
#endif
 assert(cviii_pause_key(&e) && cviii_pause_active());
 e=key(SDL_SCANCODE_RETURN,0);
 assert(cviii_pause_key(&e)); /* Save opens the child, does not write */
 assert(cviii_pause_slot_active() && save_calls==0);
 e=key(SDL_SCANCODE_A,0);
 assert(cviii_pause_key(&e)); /* gameplay button swallowed */
 e=key(SDL_SCANCODE_LEFT,0);
 assert(cviii_pause_key(&e)); /* 0 -> 9 */
 e=key(SDL_SCANCODE_RETURN,1);
 assert(cviii_pause_key(&e) && save_calls==0);
 e=key(SDL_SCANCODE_RETURN,0);
 assert(cviii_pause_key(&e) && save_calls==1 && saved_slot==9);
 assert(!cviii_pause_active() && !cviii_pause_slot_active());
 assert(cviii_save_slot==9);
 assert(cviii_pause_key(&e)==false); /* game owns Return after close */

 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && cviii_pause_active());
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_DOWN); /* Load */
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A);
 assert(cviii_pause_slot_active() && load_calls==0);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_RIGHT); /* 9 -> 0 */
 cviii_pause_button(SDL_CONTROLLER_BUTTON_B); /* child Back */
 assert(!cviii_pause_slot_active() && cviii_pause_active());
 assert(cviii_save_slot==9 && load_calls==0);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A); /* opens Load from slot 9 */
 assert(cviii_pause_slot_active());
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_RIGHT); /* 9 -> 0 */
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A); /* now load */
 assert(load_calls==1 && loaded_slot==0);
 assert(cviii_save_slot==0 && !cviii_pause_active());

 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e));
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A); /* Save child */
 assert(cviii_pause_slot_active());
 e=key(SDL_SCANCODE_ESCAPE,0);
 assert(cviii_pause_key(&e) && !cviii_pause_slot_active());
 assert(cviii_pause_active() && save_calls==1);
 e=key(SDL_SCANCODE_ESCAPE,0);
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 assert(save_calls==1 && load_calls==1);
 puts("PASS JP0625 exact slot SDL shell: 0/9 wrap, save/load, child cancel, netplay");
 return 0;
}
'''

def fixture()->str:
    old=imp(TOOLS/"jp_start_pause_shell_test_0624.py")
    first=imp(TOOLS/"patch_cyc_start_menu_0623.py")
    slots=imp(TOOLS/"patch_cyc_slot_picker_0625.py")
    base=old.PREFIX
    base=base.replace("SDL_SCANCODE_SPACE, SDL_SCANCODE_A",
                      "SDL_SCANCODE_SPACE, SDL_SCANCODE_A, SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT")
    base=base.replace("SDL_CONTROLLER_BUTTON_B, SDL_CONTROLLER_BUTTON_START",
                      "SDL_CONTROLLER_BUTTON_B, SDL_CONTROLLER_BUTTON_START, SDL_CONTROLLER_BUTTON_DPAD_LEFT, SDL_CONTROLLER_BUTTON_DPAD_RIGHT")
    base=base.replace("void cviii_pause_close(void){cviii_start_close(&game_menu);}",
                      "void cviii_pause_close(void){cviii_start_close(&game_menu);cviii_pause_slot_cancel();}")
    # Real 0623 shell, not a second set of handwritten action callbacks.
    generated=slots.generate(first.SHELL)
    if generated.count(slots.MARKER)!=1:
        raise ValueError("sixth layer not generated")
    return base+"\n"+SHIM+"\n"+generated+"\n"+END

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--cc",default=os.getenv("CC","cc"))
    p.add_argument("--emit-c",type=Path)
    a=p.parse_args()
    source=fixture()
    if a.smoke:
        for token in ("cviii_pause_slot_commit", "cviii_save_slot=selected",
                      "cviii_pause_slot_cancel", "case CVIII_START_SAVE:",
                      "case CVIII_START_LOAD:", "SDL_CONTROLLER_BUTTON_DPAD_RIGHT"):
            if token not in source:raise ValueError("Missing slot action "+token)
        print("PASS JP0625 actual sixth-layer generated shell extracted")
        return
    if a.emit_c:
        a.emit_c.write_text(source,encoding="utf-8")
        print(str(a.emit_c))
        return
    with tempfile.TemporaryDirectory(prefix="jp0625_shell_") as t:
        c=Path(t)/"slot_shell.c"
        c.write_text(source,encoding="utf-8")
        for mode,flags in (("offline",[]),("netplay",["-DNESRECOMP_NET"])):
            exe=Path(t)/("slot_shell_"+mode+(".exe" if os.name=="nt" else ""))
            subprocess.run([a.cc,"-std=c11","-O2","-Wall","-Wextra",
                            "-Werror","-pedantic",*flags,"-I",str(SOURCE),str(c),
                            str(SOURCE/"cviii_start_menu_0623.c"),
                            str(SOURCE/"cviii_slot_picker_0625.c"),
                            "-o",str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
    print("PASS JP0625 exact sixth-layer SDL slot shell: offline/netplay C11")

if __name__=="__main__":main()
