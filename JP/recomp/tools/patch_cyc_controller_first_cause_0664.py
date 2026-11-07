#!/usr/bin/env python3
"""Backport Player-1 gamepad input without changing the pinned NESRecomp engine.

Only a private adjacent cyc_input.c overlay is used by the windowed Japanese
game. All CPU, 2A03, OAM DMA and DMC DMA behavior is unchanged.
"""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = 'CVIII_P1_PAD_0664'
ASSIGN_OLD = '''    for (int p = 0; p < CYC_INPUT_PLAYERS; ++p) {
        if (b->source[p] != 2 || player_pad[p] >= 0) continue;
        for (int i = 0; i < pads; ++i)
            if (!taken[i]) { player_pad[p] = i; taken[i] = true; break; }
    }
'''
ASSIGN_NEW = '''    /* CVIII_P1_PAD_0664: keyboard Player 1 also accepts an unclaimed pad.
     * Honor explicitly named gamepad users first; never steal their device. */
    if (b->source[0] == 1) {
        for (int i = 0; i < pads; ++i)
            if (!taken[i]) { player_pad[0] = i; taken[i] = true; break; }
    }
''' + ASSIGN_OLD
EVAL_OLD = '''            if (b->source[p] == 1) {
                on = key_down(f, pb->key) && !key_taken[pb->key];
            } else if (b->source[p] == 2 && pad >= 0 && pb->pad) {
                uint32_t m;
                on = pad_down(f, pad, pb->pad, threshold, &m) && !(m & pad_taken[pad]) &&
                     !(CYC_PAD_IS_AXIS(pb->pad) && axis_taken[pad] == pb->pad);
            }
'''
EVAL_NEW = '''            if (b->source[p] == 1)
                on = key_down(f, pb->key) && !key_taken[pb->key];
            /* Controller input is additive for keyboard Player 1. */
            if (!on && b->source[p] != 0 && pad >= 0 && pb->pad) {
                uint32_t m;
                on = pad_down(f, pad, pb->pad, threshold, &m) && !(m & pad_taken[pad]) &&
                     !(CYC_PAD_IS_AXIS(pb->pad) && axis_taken[pad] == pb->pad);
            }
'''
AXIS_OLD = '''        if (b->source[p] == 2 && pad >= 0) {
            /* the left stick also works the D-pad */'''
AXIS_NEW = '''        if (b->source[p] != 0 && pad >= 0) {
            /* the left stick also works the D-pad */'''
INCLUDE_OLD = '#include <stdio.h>\n'
INCLUDE_NEW = '#include <stdio.h>\n#include <stdlib.h>\n'
TRACE_OLD = '''        out->buttons[p] = bits;
    }
}'''
TRACE_NEW = '''        out->buttons[p] = bits;
    }
    /* Opt-in host boundary sample: no extra NES bus reads or writes. */
    static int cviii_route_trace = -1;
    static unsigned cviii_route_samples;
    if (cviii_route_trace < 0) {
        const char *value = getenv("CVIII_CONTROLLER_ROUTE_TRACE");
        cviii_route_trace = value && value[0] == '1';
    }
    if (cviii_route_trace && cviii_route_samples < 512u) {
        fprintf(stderr, "[CVIII-P1-route] sample=%u source1=%d pad1=%d buttons1=%02X source2=%d pad2=%d buttons2=%02X\\n",
                ++cviii_route_samples, b->source[0], out->player_pad[0], (unsigned)out->buttons[0],
                b->source[1], out->player_pad[1], (unsigned)out->buttons[1]);
    }
}'''


def patch(source: str) -> str:
    if MARKER in source:
        raise ValueError('JP0664 already patched; refusing repeated overlay')
    for old in (ASSIGN_OLD, EVAL_OLD, AXIS_OLD, TRACE_OLD, INCLUDE_OLD):
        if source.count(old) != 1:
            raise ValueError('JP0664 pinned Player-1 input anchor missing/repeated')
    for old, new in ((ASSIGN_OLD, ASSIGN_NEW), (EVAL_OLD, EVAL_NEW),
                     (AXIS_OLD, AXIS_NEW), (TRACE_OLD, TRACE_NEW),
                     (INCLUDE_OLD, INCLUDE_NEW)):
        source = source.replace(old, new, 1)
    return source


def smoke() -> None:
    specimen = INCLUDE_OLD + ASSIGN_OLD + EVAL_OLD + AXIS_OLD + TRACE_OLD
    result = patch(specimen)
    assert result.count(MARKER) == 1
    assert ASSIGN_NEW in result and EVAL_NEW in result and AXIS_NEW in result
    assert TRACE_NEW in result and INCLUDE_NEW in result
    assert result.count('if (b->source[p] != 2 || player_pad[p] >= 0)') == 1
    for damaged in (result, specimen.replace(ASSIGN_OLD, ''),
                    specimen.replace(EVAL_OLD, ''), specimen.replace(AXIS_OLD, ''),
                    specimen.replace(TRACE_OLD, '')):
        try:
            patch(damaged)
        except ValueError:
            continue
        raise AssertionError('Changed/patched upstream source accepted')
    print('PASS JP0664 fail-closed source overlay and additive Player-1 routing')


def main() -> None:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source', type=Path)
    a.add_argument('--out', type=Path)
    a.add_argument('--smoke', action='store_true')
    x = a.parse_args()
    if x.smoke:
        smoke()
        return
    if x.source is None or x.out is None:
        a.error('Specify --source and --out')
    src, dst = x.source.resolve(strict=True), x.out.resolve()
    if (src.name != 'cyc_input.c' or dst.name != 'cviii_cyc_input_p1.c' or
            src.parent != dst.parent or src == dst):
        raise ValueError('JP0664 requires an adjacent private cyc_input.c overlay')
    dst.write_text(patch(src.read_text(encoding='utf-8')), encoding='utf-8')
    print('PASS JP0664 private Player-1 controller source overlay')


if __name__ == '__main__':
    main()
