#!/usr/bin/env python3
"""Owner-private, final SDL2 lighting editor overlay on top of JP0626.

Fail closed on upstream / prior generated SDL drift. No NESRecomp sources or
copyrighted assets are committed; only a local generated copy is built.
"""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER="CVIII_LIGHTING_EDITOR_0662"
PREV="CVIII_AUDIO_RETURN_0626"
SOURCE="cviii_cyc_sdl_audio_return.c"
TARGET="cviii_cyc_sdl_lighting.c"
KEY_ANCHOR="            if (ev.type == SDL_QUIT) s_running = false;"
START="bool open = menu_open() || cviii_stage_open || cviii_audio_menu_active() || cviii_pause_active();"
FINAL="open = menu_open() || cviii_stage_open || cviii_audio_menu_active() || cviii_pause_active();"

SHELL=r'''
/* CVIII_LIGHTING_EDITOR_0662: paused, game-owned live lighting.
 * Event routing is presentation only; no emulated buttons are changed. */
#include "cviii_lighting_host.h"
static void zapper_window_point(int,int,int*,int*,int*,int*);
static bool cviii_light_sdl_event(const SDL_Event *ev, bool other_open)
{
    if(ev->type==SDL_KEYDOWN &&
       ev->key.keysym.scancode==SDL_SCANCODE_F7){
        if(!ev->key.repeat && (cviii_lighting_editor_active() || !other_open)){
#ifdef NESRECOMP_NET
            if(nes_netplay_active()){
                note("LIGHT EDITOR","Unavailable during netplay");
                return true;
            }
#endif
            if(!cviii_lighting_editor_input(1,-1,-1))
                note("LIGHT EDITOR","Enhanced edition required");
            else {
                save_settings();
                note("LIGHT EDITOR",cviii_lighting_editor_active()?
                    "LMB place/drag, RMB select; wheel radius, Shift wheel power":
                    "Closed; level lighting remains visible");
            }
        }
        return true;
    }
    if(!cviii_lighting_editor_active())return false;
    if(ev->type==SDL_KEYDOWN){
        const SDL_Scancode sc=ev->key.keysym.scancode;
        if(ev->key.repeat)return true;
        if(sc==SDL_SCANCODE_ESCAPE){
            (void)cviii_lighting_editor_input(1,-1,-1);
            save_settings();
            return true;
        }
        int code=0;
        if(sc==SDL_SCANCODE_DELETE || sc==SDL_SCANCODE_BACKSPACE)code=5;
        else if(sc==SDL_SCANCODE_EQUALS || sc==SDL_SCANCODE_KP_PLUS)code=6;
        else if(sc==SDL_SCANCODE_MINUS || sc==SDL_SCANCODE_KP_MINUS)code=7;
        else if(sc==SDL_SCANCODE_PAGEUP)code=8;
        else if(sc==SDL_SCANCODE_PAGEDOWN)code=9;
        else if(sc==SDL_SCANCODE_C)code=10;
        else if(sc==SDL_SCANCODE_RIGHTBRACKET)code=11;
        else if(sc==SDL_SCANCODE_LEFTBRACKET)code=12;
        if(code && cviii_lighting_editor_input(code,-1,-1))save_settings();
        return true;
    }
    if(ev->type==SDL_KEYUP)return true;
    if(ev->type==SDL_MOUSEBUTTONDOWN ||
       ev->type==SDL_MOUSEBUTTONUP || ev->type==SDL_MOUSEMOTION){
        int x=-1,y=-1,code=0;
        if(ev->type==SDL_MOUSEMOTION){
            if(!(ev->motion.state&SDL_BUTTON_LMASK))return true;
            zapper_window_point(ev->motion.x,ev->motion.y,&x,&y,NULL,NULL);
            code=3;
        }else{
            zapper_window_point(ev->button.x,ev->button.y,&x,&y,NULL,NULL);
            if(ev->type==SDL_MOUSEBUTTONUP && ev->button.button==SDL_BUTTON_LEFT)
                code=4;
            else if(ev->type==SDL_MOUSEBUTTONDOWN && ev->button.button==SDL_BUTTON_LEFT)
                code=2;
            else if(ev->type==SDL_MOUSEBUTTONDOWN && ev->button.button==SDL_BUTTON_RIGHT)
                code=13;
        }
        if(code){
            if(cviii_lighting_editor_input(code,x,y) && code!=3)
                save_settings();
        }
        return true;
    }
    if(ev->type==SDL_MOUSEWHEEL){
        int delta=ev->wheel.y;
        if(ev->wheel.direction==SDL_MOUSEWHEEL_FLIPPED)delta=-delta;
        if(delta>8)delta=8;
        if(delta< -8)delta=-8;
        const SDL_Keymod mod=SDL_GetModState();
        int changed=0;
        while(delta){
            int code;
            if(mod&KMOD_CTRL)code=delta>0?11:12;
            else if(mod&KMOD_SHIFT)code=delta>0?8:9;
            else code=delta>0?6:7;
            changed|=cviii_lighting_editor_input(code,-1,-1);
            delta+=delta>0?-1:1;
        }
        if(changed)save_settings();
        return true;
    }
    return false;
}
'''
def once(text: str, old: str, replacement: str) -> str:
    count=text.count(old)
    if count!=1:
        raise ValueError(f"JP0662 pinned final SDL anchor mismatch {old[:70]!r}: count={count}")
    return text.replace(old,replacement,1)

def generate(text: str) -> str:
    if MARKER in text or text.count(PREV)!=1:
        raise ValueError("JP0662 requires one unmodified JP0626 private SDL source")
    text=once(text,"static bool cviii_stage_open;",SHELL+"\nstatic bool cviii_stage_open;")
    text=once(text,KEY_ANCHOR,
        '''            if(cviii_light_sdl_event(&ev,open)){
                open=menu_open() || cviii_stage_open || cviii_audio_menu_active() ||
                     cviii_pause_active() || cviii_lighting_editor_active();
                continue;
            }
'''+KEY_ANCHOR)
    text=once(text,START,START[:-1]+" || cviii_lighting_editor_active();")
    text=once(text,FINAL,FINAL[:-1]+" || cviii_lighting_editor_active();")
    return text

def smoke() -> None:
    fixture="\n".join(("/* "+PREV+" */","static bool cviii_stage_open;",
                       KEY_ANCHOR,START,FINAL))
    product=generate(fixture)
    assert product.count(MARKER)==1
    assert "SDL_SCANCODE_F7" in product
    assert "SDL_RenderWindowToLogical" not in SHELL # uses engine mapping
    assert product.count("|| cviii_lighting_editor_active();")==3
    assert "SDL_MOUSEMOTION" in product and "SDL_MOUSEWHEEL" in product
    for invalid in (product,fixture.replace(KEY_ANCHOR,"/* changed */")):
        try: generate(invalid)
        except ValueError: continue
        raise AssertionError("An already-patched/drifted SDL anchor was accepted")
    print("PASS JP0662 pinned SDL F7/mouse/keyboard lighting editor smoke")

def main() -> None:
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source",type=Path)
    a.add_argument("--out",type=Path)
    a.add_argument("--smoke",action="store_true")
    opt=a.parse_args()
    if opt.smoke:
        smoke()
        return
    if not opt.source or not opt.out:
        a.error("--source and --out are required")
    source=opt.source.resolve(strict=True)
    dest=opt.out.resolve()
    if source.name!=SOURCE or dest.name!=TARGET or source.parent!=dest.parent:
        raise ValueError("JP0662 requires adjacent final owner-private SDL files")
    dest.write_text(generate(source.read_text(encoding="utf-8")),encoding="utf-8")
    print("PASS JP0662 final native SDL lighting editor overlay")

if __name__=="__main__": main()
