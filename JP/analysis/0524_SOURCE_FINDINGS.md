# 0524 — Original JP linked-actor reset at raw0B $81B2 and $B56B

Original Japanese Akumajou Densetsu ROM SHA-256: 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28 (VRC6 mapper 24). Source offsets are relative to PRG after the 16-byte iNES header.

| Original CPU source | PRG offset | Bytes | SHA-256 |
|---|---|---:|---|
| raw0B $81B2-$81CB | $02C1B2 | 26 | d84f72f11fe42f867816b7503d55d8bbd0d0796f93b8ba1a8360894a1b8080d4 |
| raw0B $B56B-$B579 | $02F56B | 15 | 15da8668d001967910311e8f390ba85e07b73a2236a39e338f8aff9a6645f3dc |
| fixed $FE6E-$FE75 | $03FE6E | 8 | 409c848d417a2e8fefcf0bce493b8676699a3cbc707dd6d8bc443b60308c6b05 |

Bounded input: initial actor X=$0D..$12, type $054E,X=$4D, and position $041C,X>=$F8. Source fixed FE63 selects bank 0B via E2D0; raw 8161 updates $0470,X bit7 and returns. Original 826C JMP 8193 and CMP #$4D routes to 81B2. LDA $061D,X/TAX selects linked actor; AND #$81 of $0470,linked optionally skips the first B56B. B56B sets A=0, clears $0657, $0470, $05C1, $0400 of selected actor, and caller clears $054E. The second B56B clears the actor indexed by $69 unconditionally. Fixed FE6E increments X modulo 256, CPX #$13 sets N/Z/C and preserves V, then branches to FDEC or FE75.

ROM-free native Release matrix: 110,592 source-bounded cases, conditional clear and skip, linked/owner alias, index $FF, wrap, plus five unsupported lower-index guards and legacy 0523 fallback. Local sanitizer suite passed. Private original-Mesen replay comparator compiled; synthetic fixture compared 1,792 nonstack RAM bytes and register/bank state exactly, deliberately altered P flag correctly rejected. No genuine original-Mesen differential, natural type-$4D event, or whole-frame proof. Prior semantic certificate 0508, strict PRG 49,504/262,144, VPP 27/100 and physical fixed frontier FB96 unchanged. Do not add 0524 to original-evidence ledger until a source-Mesen differential exists.

Reproduce original physical source: python3 JP/tools/audit_linked_actor_0524_rom.py "$ORIGINAL_JP_ROM". Native C++: bash JP/tools/run_native_regressions.sh "$ORIGINAL_JP_ROM" and cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 && cmake --build build/standalone0509 && ctest --test-dir build/standalone0509 --output-on-failure.
