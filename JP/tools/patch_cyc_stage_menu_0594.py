#!/usr/bin/env python3
"""JP0594 F10 full-machine checkpoint menu, layered over the 0591 SDL overlay.

No ROM bytes or copyrighted upstream sources are embedded or committed.
"""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "CVIII_STAGE_WARP_0594"
KEY = "            else if (ev.type == SDL_KEYDOWN) {\n                /* CVIII_SAVE_SLOTS_0591: Ctrl+0..9 selects a quick-save slot."
C_STAGE = r'''
/* CVIII_STAGE_WARP_0594: whole-machine debug checkpoints, no RAM hacks. */
static bool cviii_stage_open;
static unsigned cviii_stage_sel, cviii_partner_sel;
static char cviii_stage_status[84] = "F5 CAPTURE / ENTER WARP";
static const char *cviii_stage_names[18] = {
 "1-01 VILLAGE", "2-01 CLOCK TOWER UP", "2-04 CLOCK TOWER DOWN",
 "3-00 FOREST VILLAGE", "3-01 FOREST TOWER", "4-0A SHIP",
 "5-0A TOWER", "6-0A CAUSEWAY", "4-01 MARSH",
 "5-01 CAVES ENTRANCE", "5-06 CAVES EXIT", "6-01 SUNKEN CITY",
 "6-01 CASTLE BASEMENT", "7-01 MOUNTAIN", "7-0A LOOKOUT",
 "8-01 CASTLE ENTRY", "9-01 VILLA", "A-01 CASTLE KEEP"
};
static const char *cviii_partner_names[4] = { "NONE", "ALUCARD", "SYPHA", "GRANT" };
static const unsigned cviii_partner_ids[4] = { 0, 3, 1, 2 };

static void cviii_stage_path(char *out, size_t size)
{
    char base[1200];
    state_slot(base, sizeof(base));
    char *ext = strrchr(base, '.');
    if (ext) *ext = 0;
    snprintf(out, size, "%s.debug.stage%02u.partner%u.cycstate", base,
             cviii_stage_sel, cviii_partner_ids[cviii_partner_sel]);
}
static bool cviii_stage_key(const SDL_KeyboardEvent *key)
{
    SDL_Scancode sc = key->keysym.scancode;
    if (key->repeat) return cviii_stage_open;
    if (sc == SDL_SCANCODE_F10) {
#ifdef NESRECOMP_NET
        if (nes_netplay_active()) { note("DEBUG", "Unavailable during netplay"); return true; }
#endif
        cviii_stage_open = !cviii_stage_open;
        return true;
    }
    if (!cviii_stage_open) return false;
    if (sc == SDL_SCANCODE_ESCAPE) { cviii_stage_open = false; return true; }
    if (sc == SDL_SCANCODE_UP) cviii_stage_sel = (cviii_stage_sel + 17) % 18;
    else if (sc == SDL_SCANCODE_DOWN) cviii_stage_sel = (cviii_stage_sel + 1) % 18;
    else if (sc == SDL_SCANCODE_LEFT) cviii_partner_sel = (cviii_partner_sel + 3) % 4;
    else if (sc == SDL_SCANCODE_RIGHT) cviii_partner_sel = (cviii_partner_sel + 1) % 4;
    else if (sc == SDL_SCANCODE_F5 || sc == SDL_SCANCODE_RETURN || sc == SDL_SCANCODE_KP_ENTER) {
        char path[1400], err[256] = "";
        cviii_stage_path(path, sizeof(path));
        bool saving = (sc == SDL_SCANCODE_F5);
        bool ok = saving ? save_state_to(path, err, sizeof(err))
                         : load_state_from(path, err, sizeof(err));
        snprintf(cviii_stage_status, sizeof(cviii_stage_status), "%s",
                 ok ? (saving ? "CHECKPOINT CAPTURED" : "STAGE LOADED") :
                      (saving ? "CAPTURE FAILED" : "NO COMPATIBLE CHECKPOINT"));
        note(cviii_stage_status, ok ? NULL : err);
        if (ok && !saving) cviii_stage_open = false;
    }
    return true;
}
static void cviii_stage_print(int x, int y, const char *text)
{
    for (; *text && x < 244; ++text, x += 4) {
        const uint8_t *glyph = cyc_overlay_glyph(*text);
        if (!glyph) continue;
        for (int gy = 0; gy < 5; ++gy)
            for (int gx = 0; gx < 3; ++gx)
                if (glyph[gy] & (4 >> gx)) {
                    SDL_Rect px = { x + gx, y + gy, 1, 1 };
                    SDL_RenderFillRect(s_ren, &px);
                }
    }
}
static void cviii_stage_draw(void)
{
    if (!cviii_stage_open) return;
    SDL_SetRenderDrawBlendMode(s_ren, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(s_ren, 9, 10, 24, 245);
    SDL_Rect bg = { 7, 7, 242, 226 }; SDL_RenderFillRect(s_ren, &bg);
    SDL_SetRenderDrawColor(s_ren, 255, 255, 255, 255);
    cviii_stage_print(14, 14, "F10 STAGE / COMPANION DEBUG");
    cviii_stage_print(14, 26, "UP/DOWN STAGE  LEFT/RIGHT PARTNER");
    for (int index = 0; index < 9; ++index) {
        int stage = (int)cviii_stage_sel - 4 + index;
        if (stage < 0 || stage >= 18) continue;
        int y = 44 + index * 12;
        if (stage == (int)cviii_stage_sel) {
            SDL_SetRenderDrawColor(s_ren, 43, 78, 106, 255);
            SDL_Rect line = { 12, y - 2, 231, 10 };
            SDL_RenderFillRect(s_ren, &line);
        }
        SDL_SetRenderDrawColor(s_ren, 255, 255, 255, 255);
        char label[80];
        snprintf(label, sizeof(label), "%c %02d %s",
                 stage == (int)cviii_stage_sel ? '>' : ' ', stage,
                 cviii_stage_names[stage]);
        cviii_stage_print(17, y, label);
    }
    char partner[80];
    snprintf(partner, sizeof(partner), "COMPANION: %s", cviii_partner_names[cviii_partner_sel]);
    cviii_stage_print(14, 160, partner);
    cviii_stage_print(14, 177, "ENTER = WARP TO SAVED CHECKPOINT");
    cviii_stage_print(14, 188, "F5 = CAPTURE CURRENT GAME HERE");
    cviii_stage_print(14, 199, "ESC = CLOSE / KEEP PLAYING");
    SDL_SetRenderDrawColor(s_ren, 238, 190, 88, 255);
    cviii_stage_print(14, 217, cviii_stage_status);
    SDL_SetRenderDrawBlendMode(s_ren, SDL_BLENDMODE_NONE);
}
'''

def once(src: str, anchor: str, replacement: str) -> str:
    if src.count(anchor) != 1:
        raise ValueError("Pinned upstream SDL overlay anchor changed: " + repr(anchor[:70]))
    return src.replace(anchor, replacement, 1)

def generate(src: str) -> str:
    if MARKER in src or "CVIII_SAVE_SLOTS_0591" not in src:
        raise ValueError("Must use unmodified JP0591 patched SDL source")
    src = once(src, "static bool save_state_slot(void)",
               C_STAGE + "\nstatic bool save_state_slot(void)")
    src = once(src, KEY, """            else if (ev.type == SDL_KEYDOWN) {
                /* F10 stage snapshot menu has no guest controller side effects. */
                if ((!open || cviii_stage_open) && cviii_stage_key(&ev.key)) {
                    open = menu_open() || cviii_stage_open;
                    continue;
                }
                /* CVIII_SAVE_SLOTS_0591: Ctrl+0..9 selects a quick-save slot.""")
    src = once(src, "#ifdef CYC_WITH_RECOMP_UI\n    cyc_ui_render();",
               "    cviii_stage_draw();\n#ifdef CYC_WITH_RECOMP_UI\n    cyc_ui_render();")
    src = once(src, "        bool open = menu_open();",
               "        bool open = menu_open() || cviii_stage_open;")
    src = once(src, "        open = menu_open();",
               "        open = menu_open() || cviii_stage_open;")
    src = once(src, "if (edge[CYC_SC_SAVE_STATE] && !menu_open())",
               "if (edge[CYC_SC_SAVE_STATE] && !menu_open() && !cviii_stage_open)")
    src = once(src, "if (edge[CYC_SC_LOAD_STATE] && !menu_open())",
               "if (edge[CYC_SC_LOAD_STATE] && !menu_open() && !cviii_stage_open)")
    return src

def smoke() -> None:
    anchors = ("static bool save_state_slot(void)", KEY,
               "#ifdef CYC_WITH_RECOMP_UI\n    cyc_ui_render();",
               "        bool open = menu_open();", "        open = menu_open();",
               "if (edge[CYC_SC_SAVE_STATE] && !menu_open())",
               "if (edge[CYC_SC_LOAD_STATE] && !menu_open())")
    stub = "/* CVIII_SAVE_SLOTS_0591 */\n" + "\n".join(anchors)
    patched = generate(stub)
    assert patched.count(MARKER) == 1
    assert "load_state_from(path, err, sizeof(err))" in patched
    assert "cviii_stage_draw();" in patched
    for bad in (patched, stub.replace(KEY, "/* source changed */")):
        try: generate(bad)
        except ValueError: continue
        raise AssertionError("Unpinned SDL overlay accepted")
    print("PASS JP0594 F10 full-machine stage / companion menu smoke")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke: smoke(); return
    if not a.source or not a.out: p.error("--source and --out required")
    src, dst = a.source.resolve(strict=True), a.out.resolve()
    if (src.name != "cviii_cyc_sdl_slots.c"
            or dst.name != "cviii_cyc_sdl_debug.c"
            or src.parent != dst.parent or src == dst):
        raise ValueError("Patch must follow JP0591 in the external SDL directory")
    dst.write_text(generate(src.read_text(encoding="utf-8")), encoding="utf-8")
    print("PASS JP0594 stage/companion F10 SDL host overlay: " + str(dst))

if __name__ == "__main__":
    main()
