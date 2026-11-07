#!/usr/bin/env python3
"""JP0761: F4/F6/F7/F10 direct modal switching and in-game F7 keyboard remap.

Eighth owner-private SDL layer over the exact pinned JP0626 build. This
does not vendor cyc_sdl.c or alter game CPU/input, PPU, VRC6 or savestates.
"""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER="CVIII_LIVE_MENUS_0761"
INSERT="static bool cviii_stage_open;"
KEY='                if ((cviii_pause_active() ||'
PAD='                if (cviii_pause_active()) {'
DRAW='    cviii_stage_draw();'
OPEN='|| cviii_pause_active();'
STATE=r'''
/* CVIII_LIVE_MENUS_0761: F7 is a paused *game window* controls page.
 * s_set.bind is the SAME CycBindings that cyc_input_eval uses; changes
 * apply immediately on keyboard-source Player 1 and persist via host.
 */
static bool cviii_keys_open, cviii_keys_capture;
static unsigned cviii_keys_selected;
static void cviii_keys_close(void)
{
    cviii_keys_open=false;
    cviii_keys_capture=false;
}
static void cviii_keys_bind(SDL_Scancode key)
{
    if(key<=SDL_SCANCODE_UNKNOWN || key>=SDL_NUM_SCANCODES ||
       key==SDL_SCANCODE_ESCAPE || key==SDL_SCANCODE_BACKSPACE ||
       (key>=SDL_SCANCODE_F1 && key<=SDL_SCANCODE_F12)) {
        note("CONTROLS", "Reserved key; choose another");
        return;
    }
    for(int shortcut=0;shortcut<CYC_SC_COUNT;shortcut++)
        if(s_set.bind.shortcut[shortcut].key==(int)key) {
            note("CONTROLS", "Host shortcut reserved");
            return;
        }
    const unsigned button=cviii_keys_selected;
    const int previous=s_set.bind.button[0][button].key;
    if(previous==(int)key) {
        cviii_keys_capture=false;
        return;
    }
    for(unsigned other=0;other<CYC_INPUT_BUTTONS;other++)
        if(other!=button && s_set.bind.button[0][other].key==(int)key) {
            s_set.bind.button[0][other].key=previous; /* conflict swap */
            break;
        }
    s_set.bind.button[0][button].key=(int)key;
    save_settings(); /* production config.ini, atomic upstream writer */
    cviii_keys_capture=false;
    note("CONTROLS", "Keyboard binding saved");
}
static bool cviii_keys_event(const SDL_KeyboardEvent *key)
{
    const SDL_Scancode sc=key->keysym.scancode;
    if(key->repeat)return cviii_keys_open;
#ifdef NESRECOMP_NET
    if((sc==SDL_SCANCODE_F4 || sc==SDL_SCANCODE_F6 ||
        sc==SDL_SCANCODE_F7 || sc==SDL_SCANCODE_F10) &&
       nes_netplay_active()) {
        note("ENHANCED MENU","Unavailable during netplay");
        return true;
    }
#endif
    /* Global F4/F6/F7/F10 switching never falls through to an old
     * active modal. The existing audio-child Pause parent is retained. */
    if(sc==SDL_SCANCODE_F4 &&
       (cviii_audio_menu_active() || cviii_stage_open || cviii_keys_open)) {
        cviii_stage_open=false;
        cviii_keys_close();
        if(cviii_audio_menu_active())cviii_audio_menu_close();
        if(!cviii_pause_active() && !cviii_pause_toggle())
            note("PAUSE","Enhanced and original CHR assets required");
        cviii_audio_menu_toggled=true;
        return true;
    }
    if(sc==SDL_SCANCODE_F6 &&
       (cviii_pause_active() || cviii_stage_open || cviii_keys_open)) {
        cviii_stage_open=false;
        cviii_keys_close();
        if(!cviii_audio_menu_active()) {
            const int ok=cviii_pause_active() ?
                cviii_pause_audio_enter() : cviii_audio_menu_toggle();
            if(!ok)note("AUDIO","Original CHR assets required");
        }
        cviii_audio_menu_toggled=true;
        return true;
    }
    if(sc==SDL_SCANCODE_F10 &&
       (cviii_pause_active() || cviii_audio_menu_active() || cviii_keys_open)) {
        cviii_keys_close();
        cviii_pause_close();
        if(cviii_audio_menu_active())cviii_audio_menu_close();
        cviii_stage_open=true;
        cviii_audio_menu_toggled=true;
        return true;
    }
    if(sc==SDL_SCANCODE_F7) {
        if(cviii_keys_open)cviii_keys_close();
        else {
            if(!cviii_controls_available_0761()) {
                note("CONTROLS","Enhanced Edition required");
                return true;
            }
            cviii_stage_open=false;
            cviii_pause_close();
            if(cviii_audio_menu_active())cviii_audio_menu_close();
            cviii_keys_open=true;
            cviii_keys_capture=false;
            cviii_keys_selected=0;
        }
        cviii_audio_menu_toggled=true;
        return true;
    }
    if(!cviii_keys_open)return false;
    if(sc==SDL_SCANCODE_ESCAPE || sc==SDL_SCANCODE_BACKSPACE) {
        if(cviii_keys_capture)cviii_keys_capture=false;
        else cviii_keys_close();
        return true;
    }
    if(cviii_keys_capture) {
        cviii_keys_bind(sc);
        return true;
    }
    if(sc==SDL_SCANCODE_UP)cviii_keys_selected=
        (cviii_keys_selected+CYC_INPUT_BUTTONS-1u)%CYC_INPUT_BUTTONS;
    else if(sc==SDL_SCANCODE_DOWN)cviii_keys_selected=
        (cviii_keys_selected+1u)%CYC_INPUT_BUTTONS;
    else if(sc==SDL_SCANCODE_RETURN || sc==SDL_SCANCODE_KP_ENTER ||
            sc==SDL_SCANCODE_SPACE)cviii_keys_capture=true;
    return true; /* Consume all keys, never leak to gameplay. */
}
static void cviii_keys_button(int button)
{
    if(!cviii_keys_open)return;
    switch(button) {
    case SDL_CONTROLLER_BUTTON_DPAD_UP:
        cviii_keys_selected=(cviii_keys_selected+CYC_INPUT_BUTTONS-1u)%CYC_INPUT_BUTTONS;
        break;
    case SDL_CONTROLLER_BUTTON_DPAD_DOWN:
        cviii_keys_selected=(cviii_keys_selected+1u)%CYC_INPUT_BUTTONS;
        break;
    case SDL_CONTROLLER_BUTTON_A:
        cviii_keys_capture=true;
        break;
    case SDL_CONTROLLER_BUTTON_B:
    case SDL_CONTROLLER_BUTTON_START:
        if(cviii_keys_capture)cviii_keys_capture=false;
        else cviii_keys_close();
        break;
    default:break;
    }
}
static void cviii_keys_print(int x,int y,const char *text)
{
    for(;text && *text && x<246;text++,x+=4) {
        const uint8_t *glyph=cyc_overlay_glyph(*text);
        if(!glyph)continue;
        for(int gy=0;gy<5;gy++)for(int gx=0;gx<3;gx++)
            if(glyph[gy] & (4>>gx)) {
                SDL_Rect px={x+gx,y+gy,1,1};
                SDL_RenderFillRect(s_ren,&px);
            }
    }
}
static void cviii_keys_draw(void)
{
    if(!cviii_keys_open)return;
    SDL_SetRenderDrawBlendMode(s_ren,SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(s_ren,8,11,26,250);
    SDL_Rect bg={7,7,242,226};SDL_RenderFillRect(s_ren,&bg);
    SDL_SetRenderDrawColor(s_ren,255,255,255,255);
    cviii_keys_print(13,14,"F7 PLAYER 1 KEYBOARD CONTROLS");
    cviii_keys_print(13,27,"UP DOWN SELECT / ENTER REBIND");
    for(unsigned i=0;i<CYC_INPUT_BUTTONS;i++) {
        const int y=44+(int)i*17;
        if(i==cviii_keys_selected) {
            SDL_SetRenderDrawColor(s_ren,43,78,106,255);
            SDL_Rect bar={10,y-3,231,13};SDL_RenderFillRect(s_ren,&bar);
            SDL_SetRenderDrawColor(s_ren,255,255,255,255);
        }
        char keyname[48],line[100];
        cyc_key_text(s_set.bind.button[0][i].key,keyname,sizeof keyname);
        snprintf(line,sizeof line,"%c %-7s  %s",
            i==cviii_keys_selected?'>':' ',cyc_button_label((int)i),keyname);
        cviii_keys_print(19,y,line);
    }
    SDL_SetRenderDrawColor(s_ren,246,204,109,255);
    cviii_keys_print(12,184,cviii_keys_capture ?
        "PRESS NEW KEY / ESC CANCEL" : "ENTER SELECT / ESC CLOSE");
    SDL_SetRenderDrawColor(s_ren,255,255,255,255);
    cviii_keys_print(12,199,"DUPLICATE KEYS AUTO SWAP");
    cviii_keys_print(12,211,"F4 F6 F7 F10 SWITCH MENUS");
    cviii_keys_print(12,223,"SAVED CONFIG IN GAME DIRECTORY");
    SDL_SetRenderDrawBlendMode(s_ren,SDL_BLENDMODE_NONE);
}
'''
def once(s,a,b):
    count=s.count(a)
    if count!=1:
        raise ValueError(f"JP0761 pinned SDL source anchor {a[:70]!r}, count {count}")
    return s.replace(a,b,1)

def generate(src:str)->str:
    if MARKER in src or src.count("CVIII_AUDIO_RETURN_0626")!=1:
        raise ValueError("JP0761 requires exact seven-layer JP0626 source")
    src=once(src,INSERT,INSERT+STATE)
    src=once(src,KEY,'''                if(cviii_keys_event(&ev.key)) {
                    open=menu_open() || cviii_stage_open ||
                         cviii_audio_menu_active() || cviii_pause_active() ||
                         cviii_keys_open;
                    continue;
                }
'''+KEY)
    src=once(src,PAD,'''                if(cviii_keys_open) {
                    cviii_keys_button(ev.cbutton.button);
                    continue;
                }
'''+PAD)
    src=once(src,DRAW,DRAW+"\n    cviii_keys_draw();")
    amount=src.count(OPEN)
    if amount<3 or amount>6:
        raise ValueError("JP0761 SDL open/pause clauses drifted: "+str(amount))
    src=src.replace(OPEN,"|| cviii_pause_active() || cviii_keys_open;")
    if src.count("cviii_keys_draw();")!=1 or src.count("cviii_keys_event(&ev.key)")!=1:
        raise ValueError("JP0761 menu wiring not unique")
    return src

def smoke()->None:
    stub="\n".join([
        "/* CVIII_AUDIO_RETURN_0626 */",INSERT,KEY,PAD,DRAW,
        "bool open=menu_open() || cviii_stage_open || cviii_audio_menu_active() || cviii_pause_active();",
        "open=menu_open() || cviii_stage_open || cviii_audio_menu_active() || cviii_pause_active();",
        "open=menu_open() || cviii_stage_open || cviii_audio_menu_active() || cviii_pause_active();",
    ])
    generated=generate(stub)
    assert "cviii_keys_event(&ev.key)" in generated
    assert "cviii_keys_button(ev.cbutton.button)" in generated
    assert "s_set.bind.button[0][button].key=(int)key;" in generated
    assert "save_settings();" in generated
    assert "cviii_pause_audio_enter()" in generated
    assert "cviii_stage_open=true;" in generated
    assert generated.count("|| cviii_keys_open;")>=3
    for changed in (generated,stub.replace(KEY,"/* bad event owner */")):
        try:generate(changed)
        except ValueError:continue
        raise AssertionError("JP0761 accepted duplicate patch or drift")
    print("PASS JP0761 synthetic F4/F6/F7/F10 transitions, paused F7 live rebind, input shielding")

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--source",type=Path)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    if a.smoke:
        smoke();return
    if not a.source or not a.out:ap.error("Provide --source and --out")
    inp=a.source.resolve(strict=True);out=a.out.resolve()
    if (inp.parent!=out.parent or inp==out or
        inp.name!="cviii_cyc_sdl_audio_return.c" or
        out.name!="cviii_cyc_sdl_live_menus.c"):
        raise ValueError("JP0761 only accepts the final adjacent owner-private SDL layer")
    out.write_text(generate(inp.read_text(encoding="utf-8")),encoding="utf-8")
    print("PASS JP0761 private Enhanced live menu + in-game F7 bindings: "+str(out))
if __name__=="__main__":main()
