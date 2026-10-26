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
#include "cviii_imgui_editor.h"
/* Called by optional genuine ReShade add-on through host C export. */
#if defined(_WIN32)
__declspec(dllexport)
#endif
void cviii_light_force_save(void){save_settings();}
#if defined(_WIN32)
__declspec(dllexport)
#endif
int cviii_light_place_window(int window_x,int window_y){
    int native_x=-1,native_y=-1;
    zapper_window_point(window_x,window_y,&native_x,&native_y,NULL,NULL);
    return cviii_lighting_editor_add(native_x,native_y);
}
static bool cviii_light_rebinding;
static SDL_Scancode cviii_light_bind_pending=SDL_SCANCODE_UNKNOWN;
static SDL_Scancode cviii_light_key(void)
{
    SDL_Scancode sc=SDL_GetScancodeFromName(cviii_lighting_editor_key());
    return sc==SDL_SCANCODE_UNKNOWN?SDL_SCANCODE_HOME:sc;
}
static bool cviii_light_reserved(SDL_Scancode sc)
{
    switch(sc){
    case SDL_SCANCODE_UNKNOWN: case SDL_SCANCODE_ESCAPE:
    case SDL_SCANCODE_F4: case SDL_SCANCODE_F6:
    case SDL_SCANCODE_F8: case SDL_SCANCODE_F9:
    case SDL_SCANCODE_F10: case SDL_SCANCODE_F11:
    case SDL_SCANCODE_F12: case SDL_SCANCODE_RETURN:
    case SDL_SCANCODE_LCTRL: case SDL_SCANCODE_RCTRL:
    case SDL_SCANCODE_LSHIFT: case SDL_SCANCODE_RSHIFT:
    case SDL_SCANCODE_LALT: case SDL_SCANCODE_RALT:
        return true;
    default: return false;
    }
}
static void cviii_light_sdl_status(void)
{
    char details[128];
    if(cviii_lighting_editor_status(details,sizeof details))
        note("LIGHT",details);
}
static bool cviii_light_sdl_event(const SDL_Event *ev, bool other_open)
{
    /* Remapping holds the machine pause until the captured key is released. */
    if(cviii_light_rebinding){
        if(ev->type==SDL_KEYDOWN){
            if(ev->key.repeat || cviii_light_bind_pending!=SDL_SCANCODE_UNKNOWN)
                return true;
            SDL_Scancode sc=ev->key.keysym.scancode;
            if(sc==SDL_SCANCODE_ESCAPE){
                cviii_light_rebinding=false;
                note("LIGHT KEY","Remap cancelled");
                return true;
            }
            if(cviii_light_reserved(sc)){
                note("LIGHT KEY","Reserved key; choose another");
                return true;
            }
            const char *name=SDL_GetScancodeName(sc);
            if(!name || !cviii_lighting_editor_set_key(name)){
                note("LIGHT KEY","Unsupported key; try another");
                return true;
            }
            save_settings();
            cviii_light_bind_pending=sc;
            note("LIGHT KEY",name);
            return true;
        }
        if(ev->type==SDL_KEYUP){
            if(ev->key.keysym.scancode==cviii_light_bind_pending){
                cviii_light_rebinding=false;
                cviii_light_bind_pending=SDL_SCANCODE_UNKNOWN;
            }
            return true;
        }
        return false;
    }
    if(ev->type==SDL_KEYDOWN && !ev->key.repeat &&
       ev->key.keysym.scancode==SDL_SCANCODE_HOME &&
       (SDL_GetModState()&KMOD_CTRL) &&
       (!other_open || cviii_lighting_editor_active())){
        cviii_light_rebinding=true;
        note("LIGHT KEY","Press new key (Escape cancels)");
        return true;
    }
    if(ev->type==SDL_KEYDOWN &&
       ev->key.keysym.scancode==cviii_light_key() &&
       !(SDL_GetModState()&(KMOD_CTRL|KMOD_ALT))){
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
                    "Workbench: ADD then click level; select from list; drag sliders":
                    "Closed; level lighting remains visible");
            }
        }
        return true;
    }
    if(!cviii_lighting_editor_active())return false;
    /* ReShade handles mouse input inside its own overlay. Never let
     * its clicks also drag a gameplay emitter in the native editor. */
    if(cviii_lighting_editor_external_active() &&
       (ev->type==SDL_MOUSEBUTTONDOWN || ev->type==SDL_MOUSEBUTTONUP ||
        ev->type==SDL_MOUSEMOTION || ev->type==SDL_MOUSEWHEEL))return true;
    if(cviii_imgui_event(ev,s_win,s_ren))return true;
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
        if(code && cviii_lighting_editor_input(code,-1,-1)){
            save_settings();
            cviii_light_sdl_status();
        }
        return true;
    }
    if(ev->type==SDL_KEYUP)return true;
    if(ev->type==SDL_MOUSEBUTTONDOWN ||
       ev->type==SDL_MOUSEBUTTONUP || ev->type==SDL_MOUSEMOTION){
        int x=-1,y=-1,code=0;
        if(ev->type==SDL_MOUSEMOTION){
            if(!(ev->motion.state&SDL_BUTTON_LMASK))return true;
            int mx=0,my=0;
            cviii_imgui_window_point(s_ren,ev->motion.x,ev->motion.y,&mx,&my);
            zapper_window_point(mx,my,&x,&y,NULL,NULL);
            code=3;
        }else{
            int mx=0,my=0;
            cviii_imgui_window_point(s_ren,ev->button.x,ev->button.y,&mx,&my);
            zapper_window_point(mx,my,&x,&y,NULL,NULL);
            if(ev->type==SDL_MOUSEBUTTONUP && ev->button.button==SDL_BUTTON_LEFT)
                code=4;
            else if(ev->type==SDL_MOUSEBUTTONDOWN && ev->button.button==SDL_BUTTON_LEFT)
                code=2;
            else if(ev->type==SDL_MOUSEBUTTONDOWN && ev->button.button==SDL_BUTTON_RIGHT)
                code=13;
        }
        if(code){
            int panel=cviii_imgui_scene_click(code,x,y);
            if(panel){
                if(panel==2)save_settings();
                return true;
            }
            if(cviii_lighting_editor_input(code,x,y) && code!=3){
                save_settings();
                if(code!=4)cviii_light_sdl_status();
            }
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
        if(changed){
            save_settings();
            cviii_light_sdl_status();
        }
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
                     cviii_pause_active() || cviii_lighting_editor_active() ||
                     cviii_light_rebinding;
                continue;
            }
'''+KEY_ANCHOR)
    text=once(text,START,START[:-1]+" || cviii_lighting_editor_active() || cviii_light_rebinding;")
    text=once(text,FINAL,FINAL[:-1]+" || cviii_lighting_editor_active() || cviii_light_rebinding;")
    text=once(text,"    if (s_ui_shot_id >= 0) {",
        "    if(cviii_imgui_render(s_win,s_ren))save_settings();\n"
        "    if (s_ui_shot_id >= 0) {")
    text=once(text,"    SDL_DestroyRenderer(s_ren);",
        "    cviii_imgui_shutdown();\n    SDL_DestroyRenderer(s_ren);")
    return text

def smoke() -> None:
    fixture="\n".join(("/* "+PREV+" */","static bool cviii_stage_open;",
                       KEY_ANCHOR,START,FINAL,"    if (s_ui_shot_id >= 0) {",
                       "    SDL_DestroyRenderer(s_ren);"))
    product=generate(fixture)
    assert product.count(MARKER)==1
    assert "SDL_SCANCODE_HOME" in product
    assert "SDL_GetScancodeFromName(cviii_lighting_editor_key())" in product
    assert "cviii_light_rebinding" in product
    assert "cviii_lighting_editor_set_key(name)" in product
    assert "SDL_RenderWindowToLogical" not in SHELL # uses engine mapping
    assert product.count("|| cviii_light_rebinding;")==2
    assert "cviii_pause_active() || cviii_lighting_editor_active() ||\n                     cviii_light_rebinding;" in product
    assert "SDL_MOUSEMOTION" in product and "SDL_MOUSEWHEEL" in product
    assert '#include "cviii_imgui_editor.h"' in product
    assert "cviii_imgui_render(s_win,s_ren)" in product
    assert "cviii_imgui_event(ev,s_win,s_ren)" in product
    assert "cviii_imgui_window_point(s_ren,ev->motion.x,ev->motion.y,&mx,&my)" in product
    assert "cviii_imgui_window_point(s_ren,ev->button.x,ev->button.y,&mx,&my)" in product
    assert "cviii_imgui_scene_click(code,x,y)" in product
    assert "cviii_imgui_shutdown();" in product
    assert "cviii_light_sdl_status();" in product
    assert "if(code!=4)" in product
    for invalid in (product,fixture.replace(KEY_ANCHOR,"/* changed */")):
        try: generate(invalid)
        except ValueError: continue
        raise AssertionError("An already-patched/drifted SDL anchor was accepted")
    print("PASS JP0662 pinned SDL Home/mappable/mouse lighting editor smoke")

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
