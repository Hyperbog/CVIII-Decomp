#!/usr/bin/env python3
"""JP0664: sound $51's original six bank05 control-state graphs.

This is inherited 04FB source grammar, not a note decoder or chronological
playback. Conditional FE loops explore both paths. No commercial stream
bytes, source pointer lists or musical pitches are emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_SHA = "58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b"
START, STOP = 0x87AE, 0x9A6B
MODES = (0, 1, 2, 3, 4, 7)
STATES = (759, 813, 781, 927, 820, 366)
COMMANDS = (345, 364, 385, 510, 371, 320)
E7 = (2, 2, 3, 1, 1, 0)


def check(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def graph(bank: bytes, mode: int, root: int) -> dict:
    check(len(bank) == 0x4000 and mode in MODES and START <= root < STOP,
          "invalid original stream/mode")
    q = deque([(root, None, None)])  # parser PC, FD return PC, FB loop anchor
    states = set()
    sites = {}
    read_sites = set()
    edges = set()
    e7 = set()

    def word(pc: int, n: int) -> bytes:
        check(START <= pc < STOP and pc + n <= STOP,
              "source command or operand escaped 04FB window")
        read_sites.update(range(pc, pc+n))
        return bank[pc-0x8000:pc-0x8000+n]

    while q:
        pc, ret, anchor = q.popleft()
        state = (pc, ret, anchor)
        if state in states:
            continue
        check(len(states) < 8192, "unbounded stream graph")
        states.add(state)
        cmd = word(pc, 1)[0]
        high, low = cmd >> 4, cmd & 15
        kind, width = "", 1
        successors = []
        if high == 15:
            if low <= 10 or low == 12:
                kind, successors = "F-single", [(pc+1, ret, anchor)]
            elif low == 11:
                kind, successors = "FB-anchor", [(pc+1, ret, pc+1)]
            elif low == 13:
                if ret is None:
                    kind, width = "FD-call", 3
                    d = word(pc+1, 2)
                    target = d[0] | d[1] << 8
                    edges.add((pc, kind, target))
                    successors = [(target, pc+3, anchor)]
                else:
                    kind = "FD-return"
                    edges.add((pc, kind, ret))
                    successors = [(ret, None, anchor)]
            elif low == 14:
                parameter = word(pc+1, 1)[0]
                if parameter == 255:
                    kind, width = "FE-absolute", 4
                    d = word(pc+2, 2)
                    target = d[0] | d[1] << 8
                    edges.add((pc, kind, target))
                    successors = [(target, ret, anchor)]
                else:
                    kind, width = "FE-counted-abstract", 2
                    check(anchor is not None, "counted repeat without FB anchor")
                    edges.add((pc, kind, anchor))
                    successors = [(pc+2, ret, anchor), (anchor, ret, anchor)]
            elif low == 15:
                kind = "FF-end"
            else:
                raise ValueError("unexpected original F token")
        elif mode == 7:
            kind, successors = "mode7-byte", [(pc+1, ret, anchor)]
        elif high <= 12:
            kind, successors = "short-byte", [(pc+1, ret, anchor)]
        elif high == 13:
            kind, width = "D-four-byte", 4
            successors = [(pc+4, ret, anchor)]
        elif high == 14:
            if low <= 5:
                kind, successors = "E-short", [(pc+1, ret, anchor)]
            elif low in (6, 7, 8, 9, 10, 12, 13, 14, 15):
                kind, width = "E-two-byte", 2
                if low == 7:
                    e7.add((pc, word(pc+1, 1)[0]))
                successors = [(pc+2, ret, anchor)]
            elif low == 11:
                kind = "E-variable"
                width = 2 if word(pc+1, 1)[0] == 0 else 3
                successors = [(pc+width, ret, anchor)]
            else:
                raise ValueError("unexpected original E token")
        else:
            raise ValueError("unsupported original opcode family")
        word(pc, width)
        if pc in sites:
            check(sites[pc] == kind or {sites[pc], kind} == {"FD-call", "FD-return"},
                  "inconsistent parser command address classification")
        else:
            sites[pc] = kind
        for dest, _, _ in successors:
            check(START <= dest < STOP, "pointer/successor escaped 04FB window")
        q.extend(successors)
    categories = Counter(sites.values())
    branches = Counter(kind for _, kind, _ in edges)
    return {
        "abstract_states": len(states),
        "unique_command_sites": len(sites),
        "unique_command_and_operand_bytes": len(read_sites),
        "structural_class_counts": dict(sorted(categories.items())),
        "unique_control_edges": dict(sorted(branches.items())),
        "decoded_E7_sites": len(e7),
        "decoded_E7_high_nibbles": sorted({p >> 4 for _, p in e7}),
        "has_terminal_FF": bool(categories["FF-end"]),
        "contains_absolute_reentry": bool(branches["FE-absolute"]),
    }


def original(rom: bytes) -> dict:
    check(len(rom) == 393232 and digest(rom) == ROM_SHA,
          "wrong original Japanese ROM")
    bank = rom[16+5*0x4000:16+6*0x4000]
    check(digest(bank[START-0x8000:STOP-0x8000]) == SPAN_SHA,
          "raw05 04FB sound stream SHA mismatch")
    directory = rom[16+12*0x4000:16+13*0x4000]
    offset = (0x8F60-0x8000)+2*(0x51-1)
    ptr = int.from_bytes(directory[offset:offset+2], "little")
    check(0x905A <= ptr < 0x9541, "original sound pointer outside directory")
    rec = ptr-0x8000
    check(directory[rec:rec+2] == bytes((5, 5)),
          "sound $51 is not six original bank05 roots")
    refs = [(directory[rec+2+3*i],
             int.from_bytes(directory[rec+3+3*i:rec+5+3*i], "little"))
            for i in range(6)]
    check(tuple(mode for mode, _ in refs) == MODES, "original sound modes changed")
    result = {}
    for i, (mode, root) in enumerate(refs):
        x = graph(bank, mode, root)
        check((x["abstract_states"], x["unique_command_sites"], x["decoded_E7_sites"]) ==
              (STATES[i], COMMANDS[i], E7[i]),
              "original source graph baseline drift")
        check(x["contains_absolute_reentry"] and not x["has_terminal_FF"],
              "original sound stream loop/end drift")
        result[f"mode_{mode}"] = x
    return {
        "schema": "jp0664-beginning-source-stream-graph/v1",
        "original_sound_id": "51",
        "physical_source_bank16": "05",
        "opaque_mode_bytes": list(MODES),
        "source_stream_count": len(refs),
        "stream_graphs": result,
        "note_and_envelope_decoder": "not implemented",
        "temporal_music_or_sfx_output_parity": "not established",
        "warning": "04FB abstract parser reachability, not notes or hardware voices",
    }


def smoke() -> None:
    bank = bytearray(0x4000)
    p = START-0x8000
    # Invented stream: byte, FB, byte, FE-counted, FE-absolute back to start.
    bank[p:p+9] = bytes((0x30, 0xFB, 0x40, 0xFE, 2,
                          0xFE, 255, START & 255, START >> 8))
    x = graph(bytes(bank), 0, START)
    check(x["abstract_states"] == 7 and
          x["unique_control_edges"]["FE-absolute"] == 1 and
          x["unique_control_edges"]["FE-counted-abstract"] == 1,
          "invented control-path smoke drift")
    check(graph(bytes(bank), 7, START)["contains_absolute_reentry"],
          "mode7 control-loop regression")
    damaged = ((0, b"\xFD\xFF\xFF"),
               (3, b"\xFE\xFF\xFF\xFF"),
               (1, b"\xFE\x01"))
    for where, raw in damaged:
        b = bytearray(bank)
        b[p+where:p+where+len(raw)] = raw
        try:
            graph(bytes(b), 0, START)
        except ValueError:
            continue
        raise AssertionError("corrupt synthetic sound stream accepted")
    print("PASS JP0664 original stream graph parser: synthetic repeat and 3 negative cases")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--rom", type=Path)
    ap.add_argument("--json", type=Path, help="owner-local aggregate-only JSON")
    args = ap.parse_args()
    if args.smoke:
        smoke()
        if args.rom is None:
            return
    if args.rom is None:
        ap.error("--rom authenticated Japanese original is required")
    info = original(args.rom.read_bytes())
    if args.json:
        args.json.write_text(json.dumps(info, indent=2, sort_keys=True)+"\n",
                             encoding="utf-8")
    print("PASS JP0664 Beginning $51 six original stream graphs;"
          " notes, PCM and runtime parity NOT ESTABLISHED")


if __name__ == "__main__":
    main()
