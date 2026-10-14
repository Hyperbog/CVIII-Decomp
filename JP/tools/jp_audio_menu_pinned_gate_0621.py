#!/usr/bin/env python3
"""JP0621: verify all four private SDL overlays against the *actual* pinned SDL source.

Read-only source-level audit. Run Windows/Linux CI with --source pointed at the
checkout of pinned mstan/nesrecomp. No original ROM and no generated source
are committed. Synthetic --smoke intentionally is NOT a substitute.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
PINNED_SDL_GIT_BLOB = "a10d0fce1d1e568a2ef672738cbee7eded323fdb"
STAGES = (
    ("0591", "patch_cyc_savestates_0591.py"),
    ("0594", "patch_cyc_stage_menu_0594.py"),
    ("0596", "patch_cyc_stage_bootstrap_0596.py"),
    ("0620", "patch_cyc_audio_menu_0620.py"),
)

def module(path: Path):
    name = "_jp0621_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Could not import project overlay: " + str(path))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\0" + data).hexdigest()

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("JP0621 " + message)

def verify_final(s0: str, sources: tuple[str, str, str, str]) -> dict:
    s1, s2, s3, s4 = sources
    require(len(s0) < len(s1) < len(s2) < len(s3) < len(s4),
            "source layering lost insertions")
    for marker, staged in (
        ("CVIII_SAVE_SLOTS_0591", s1),
        ("CVIII_STAGE_WARP_0594", s2),
        ("CVIII_STAGE_WARP_0594", s3),
        ("CVIII_AUDIO_MENU_0620", s4),
    ):
        require(marker in staged, "missing stage marker " + marker)
    require(s4.count("CVIII_AUDIO_MENU_0620") == 1,
            "duplicated audio modal patch")
    require(s4.count('#include "cviii_audio_menu_0620.h"') == 1,
            "missing or duplicated game-owned menu adapter include")
    require(s4.count("cviii_audio_menu_key(&ev.key)") == 1,
            "duplicate F6 keyboard handling")
    require(s4.count("cviii_audio_menu_button(ev.cbutton.button)") == 1,
            "duplicate D-pad handling")
    require(s4.count("cviii_audio_menu_toggled=false") == 1,
            "wrong modal transition boundary")
    require(s4.count("SDL_ClearQueuedAudio(dev)") == 1,
            "audio pause requires clearing queued PCM")

    # Prioritize F6 Audio over CYC_DEV_UI diagnostic intercept while the
    # regular F10 debug menu retains its own F6/password shortcut.
    event = s4[s4.index("else if (ev.type == SDL_KEYDOWN) {"):]
    require(event.index("cviii_audio_menu_key(&ev.key)") <
            event.index("cviii_stage_key(&ev.key)") <
            event.index("dev_key(ev.key.keysym.scancode)"),
            "audio/stage/debug keyboard interception order changed")
    stage = event[event.index("cviii_audio_menu_key(&ev.key)"):]
    require("(!open && !cviii_stage_open)" in stage,
            "F6 audio must not hijack F10 password debug menu")
    require("SDL_SCANCODE_F6" in s4 and
            "SDL_CONTROLLER_BUTTON_DPAD_LEFT" in s4,
            "keyboard/gamepad branches missing")
    require("if (was_open && !open)" in s4 and
            "hold_input = true;" in s4 and
            "if (hold_input)" in s4,
            "host input release barrier lost")
    require("if (online || (!open && !inactive))" in s4 and
            "cyc_run_frame();" in s4,
            "host frame pause predicate lost")
    require("open = menu_open() || cviii_stage_open || cviii_audio_menu_active()" in s4,
            "modal omitted from frame pause")
    require("if (edge[CYC_SC_SAVE_STATE]" in s4 and
            "!cviii_audio_menu_active()" in s4,
            "state shortcut not isolated")
    require("cviii_audio_menu_move(sc==SDL_SCANCODE_LEFT?-2:2)" in s4 and
            "if (cviii_audio_menu_move(2)) save_settings();" in s4,
            "one-percent keyboard/gamepad persistence lost")
    require("cviii_audio_menu_close();" in s4,
            "no close action")
    require("s_extras->save_settings" in s0,
            "upstream config persistence callback lost")
    require("cyc_session_audio_mix(pcm,n)" in s4,
            "native audio callback unexpectedly lost")
    return {
        "pinned_upstream_git_blob": PINNED_SDL_GIT_BLOB,
        "overlay_chain": [version for version, _ in STAGES],
        "original_source_bytes": len(s0.encode("utf-8")),
        "final_source_bytes": len(s4.encode("utf-8")),
        "keyboard_priority_verified": True,
        "modal_pause_and_release_anchors_verified": True,
        "native_compilation_or_interactive_gameplay_verified": False,
    }

def chain(src: str, patches=None):
    if patches is None:
        patches = [module(TOOLS / filename) for _, filename in STAGES]
    first = patches[0].generate(src)
    patches[0].validate(src, first)
    second = patches[1].generate(first)
    third = patches[2].generate(second)
    fourth = patches[3].generate(third)
    return first, second, third, fourth

def smoke() -> None:
    assert git_blob_sha(b"test") == "30d74d258442c7c65512eafab474568dd706c430"
    assert git_blob_sha(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    patches = [module(TOOLS / filename) for _, filename in STAGES]
    for script in patches:
        script.smoke()
    # An already-patched input is never a valid source for the final layer.
    a = patches[-1]
    fragments = (
        "/* CVIII_STAGE_WARP_0594 */",
        "static bool cviii_stage_open;", a.KEY, a.CONTROLLER,
        a.OPEN_START, a.OPEN_FINAL,
        "if (edge[CYC_SC_MENU] && s_have_menu)",
        "if (edge[CYC_SC_SAVE_STATE] && !menu_open() && !cviii_stage_open)",
        "if (edge[CYC_SC_LOAD_STATE] && !menu_open() && !cviii_stage_open)",
    )
    src = "\n".join(fragments)
    final = a.generate(src)
    try:
        a.generate(final)
    except ValueError:
        pass
    else:
        raise AssertionError("double-patched SDL modal accepted")
    print("PASS JP0621 pin-gate imported 4 overlays; source check requires --source")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--source", type=Path,
                   help="Pinned mstan/nesrecomp runner/cyc/cyc_sdl.c")
    a = p.parse_args()
    if a.smoke:
        smoke()
        return
    if a.source is None:
        p.error("--source is required (real pinned SDL checkout)")
    data = a.source.read_bytes()
    actual_sha = git_blob_sha(data)
    require(actual_sha == PINNED_SDL_GIT_BLOB,
            f"upstream drift: got Git blob {actual_sha}")
    src = data.decode("utf-8")
    result = verify_final(src, chain(src))
    import json
    print(json.dumps(result, sort_keys=True))
    print("PASS JP0621 authentic pinned SDL 0591->0594->0596->0620 source contract")

if __name__ == "__main__":
    main()
