#!/usr/bin/env python3
"""JP0624: compile and EXECUTE the real JP0623 C SDL action shell ROM-free.

Imports the exact private SDL patcher's SHELL source, uses a tiny SDL-like
input ABI shim and links the real action registry. Does not compile/replace
the pinned NESRecomp project or include any commercial ROM/graphics.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile

TOOLS=Path(__file__).resolve().parent
ENHANCED=TOOLS.parent/"native"/"enhanced"
PREFIX=r'''
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
typedef int SDL_Scancode;
enum {
 SDL_SCANCODE_F4=1, SDL_SCANCODE_ESCAPE, SDL_SCANCODE_BACKSPACE,
 SDL_SCANCODE_UP, SDL_SCANCODE_DOWN, SDL_SCANCODE_RETURN,
 SDL_SCANCODE_KP_ENTER, SDL_SCANCODE_SPACE, SDL_SCANCODE_A
};
enum {
 SDL_CONTROLLER_BUTTON_DPAD_UP=100,
 SDL_CONTROLLER_BUTTON_DPAD_DOWN, SDL_CONTROLLER_BUTTON_A,
 SDL_CONTROLLER_BUTTON_B, SDL_CONTROLLER_BUTTON_START
};
typedef struct {SDL_Scancode scancode;} SDL_Keysym;
typedef struct {SDL_Keysym keysym;int repeat;} SDL_KeyboardEvent;
static bool s_running=true;
static bool cviii_audio_menu_toggled=false;
static int save_calls=0,load_calls=0,audio_calls=0,note_calls=0;
static int assets_ok=1,enhanced=1;
static int audio_open=0;
#ifdef NESRECOMP_NET
static int netplay_on=0;
static bool nes_netplay_active(void) {return netplay_on!=0;}
#endif
static void note(const char *title,const char *detail)
{
 (void)title;(void)detail;note_calls++;
}
static int cviii_audio_menu_toggle(void)
{
 if(!enhanced || !assets_ok)return 0;
 audio_open=!audio_open;
 return 1;
}
#include "cviii_start_host_0623.h"
#include "cviii_start_menu_0623.h"
static CviiiStartMenu game_menu;
int cviii_pause_active(void){return game_menu.open;}
int cviii_pause_toggle(void)
{
 return cviii_start_toggle(&game_menu,enhanced,assets_ok);
}
void cviii_pause_close(void){cviii_start_close(&game_menu);}
void cviii_pause_move(int dir){(void)cviii_start_move(&game_menu,dir);}
int cviii_pause_accept(void){return (int)cviii_start_accept(&game_menu);}
'''
SUFFIX=r'''
static bool save_state_slot(void){save_calls++;return true;}
static bool load_state_slot(void){load_calls++;return true;}
static SDL_KeyboardEvent key(SDL_Scancode sc,int repeat)
{
 SDL_KeyboardEvent event={{sc},repeat};
 return event;
}
int main(void)
{
 assert(cviii_start_defaults(&game_menu));
 cviii_start_seal(&game_menu);
 SDL_KeyboardEvent e=key(SDL_SCANCODE_A,0);
 assert(!cviii_pause_key(&e)); /* outside modal: original game owns key */
 assert(cviii_pause_accept()==CVIII_START_NONE);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A);
 assert(save_calls==0 && load_calls==0);
#ifdef NESRECOMP_NET
 netplay_on=1;
 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 netplay_on=0;
#endif
 enhanced=0;
 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 enhanced=1;assets_ok=0;
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 assets_ok=1;
 e=key(SDL_SCANCODE_F4,1);
 assert(cviii_pause_key(&e) && !cviii_pause_active()); /* no repeat */
 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && cviii_pause_active());
 assert(cviii_audio_menu_toggled);
 e=key(SDL_SCANCODE_A,0);
 assert(cviii_pause_key(&e)); /* ordinary game key consumed */
 e=key(SDL_SCANCODE_RETURN,0);
 assert(cviii_pause_key(&e) && save_calls==1);
 e=key(SDL_SCANCODE_DOWN,0);
 assert(cviii_pause_key(&e));
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A);
 assert(load_calls==1);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_DOWN);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_A);
 assert(audio_calls==0 && audio_open==1);
 assert(!cviii_pause_active()); /* transitioned to Audio submenu */
 audio_open=0;
 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && cviii_pause_active());
 assert(game_menu.selected==0);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_UP);
 assert(game_menu.selected==3); /* wrap selects Quit */
 e=key(SDL_SCANCODE_KP_ENTER,0);
 assert(cviii_pause_key(&e) && s_running && game_menu.quit_armed);
 /* Leaving Quit cancels confirmation. */
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_UP);
 assert(!game_menu.quit_armed);
 cviii_pause_button(SDL_CONTROLLER_BUTTON_DPAD_DOWN);
 assert(game_menu.selected==3);
 e=key(SDL_SCANCODE_SPACE,0);
 assert(cviii_pause_key(&e) && s_running && game_menu.quit_armed);
 assert(cviii_pause_key(&e) && !s_running);
 s_running=true;
 e=key(SDL_SCANCODE_ESCAPE,0);
 assert(cviii_pause_key(&e) && !cviii_pause_active());
 e=key(SDL_SCANCODE_F4,0);
 assert(cviii_pause_key(&e) && cviii_pause_active());
 cviii_pause_button(SDL_CONTROLLER_BUTTON_START);
 assert(!cviii_pause_active());
 e=key(SDL_SCANCODE_A,0);
 assert(!cviii_pause_key(&e)); /* input ownership returned to game */
 assert(save_calls==1 && load_calls==1 && audio_open==0);
 puts("PASS JP0624 actual F4 SDL action shell, gameplay input ownership, save/load/audio/quit");
 return 0;
}
'''
def shell_source()->str:
    patcher_path=TOOLS/"patch_cyc_start_menu_0623.py"
    spec=importlib.util.spec_from_file_location("jp0623_action_shell",patcher_path)
    if spec is None or spec.loader is None:
        raise ValueError("missing JP0623 source patcher")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shell=module.SHELL
    if shell.count("CVIII_START_PAUSE_0623")!=1:
        raise ValueError("missing original JP0623 C shell marker")
    return PREFIX+"\n"+shell+"\n"+SUFFIX

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc",default=os.getenv("CC","cc"))
    parser.add_argument("--emit-c",type=Path)
    parser.add_argument("--smoke",action="store_true",
                        help="Check exact shell extraction without a C compiler")
    a=parser.parse_args()
    source=shell_source()
    if a.smoke:
        for token in ("cviii_pause_key(", "cviii_pause_button(",
                      "case CVIII_START_SAVE:", "case CVIII_START_LOAD:",
                      "case CVIII_START_AUDIO:", "case CVIII_START_QUIT:",
                      "SDL_SCANCODE_F4", "SDL_CONTROLLER_BUTTON_A"):
            if token not in source:
                raise ValueError("Missing expected real SDL shell action: "+token)
        print("PASS JP0624 exact JP0623 F4 action shell extracted safely")
        return
    if a.emit_c:
        a.emit_c.write_text(source,encoding="utf-8")
        print("Wrote owner-independent C integration fixture: "+str(a.emit_c))
        return
    with tempfile.TemporaryDirectory(prefix="jp0624_") as temp:
        c_file=Path(temp)/"audio_start_shell.c"
        exe=Path(temp)/("audio_start_shell.exe" if os.name=="nt" else "audio_start_shell")
        c_file.write_text(source,encoding="utf-8")
        for suffix,extra in (("offline",[]),("netplay",["-DNESRECOMP_NET"])):
            out=exe.with_name(exe.stem+"_"+suffix+exe.suffix)
            subprocess.run([a.cc,"-std=c11","-O2","-Wall","-Wextra",
                            "-Werror","-pedantic",*extra,"-I",str(ENHANCED),
                            str(c_file),str(ENHANCED/"cviii_start_menu_0623.c"),
                            "-o",str(out)],check=True)
            subprocess.run([str(out)],check=True)
    print("PASS JP0624 patcher-extracted SDL shell compiled/executed offline + netplay")

if __name__=="__main__":main()
