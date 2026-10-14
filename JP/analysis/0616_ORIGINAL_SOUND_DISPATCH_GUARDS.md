# JP0616 — Original JP sound-request guard decisions, full bounded branch domain

**Evidence class:** byte-authenticated control-flow proof from the original Japanese VRC6 ROM and synthetic exhaustive input evaluation. This is **not** actual game-frame liveness, dropped SFX observation or independent Mesen2 runtime parity.

## Original sound driver locations

- Fixed PRG31 $E249 wraps sound requests, temporarily selects raw bank $0C and invokes $8850.
- Physical PRG24 raw bank $0C:$8850 saves request A into $EF, branches to $8842 for A<$50, performs $87AE reset then record installation for $50..$6E, and branches to $8908 for A>=$6F.
- $8842 checks RAM $0109. When $0109==$50, an incoming command A=$06..$4F returns at $884F **before** record installation. The $00..$05 commands and any low command with $0109!=$50 continue at $8860 without the reset used for $50..$6E. This source-level early return is a gate, not evidence an audible effect was rejected.
- $8908 translates high request A to index N=A-$6F (0..$90), increments $06DD if N>=$0D, then applies the DMC gate using old $019E. A new DMC index is rejected by RTS at $8922 **iff** old $019E >=$05 and N<old $019E. Otherwise $8925 stores N to $019E and the driver proceeds at $8928 toward CPU writes $4015/$4010/$4011/$4012/$4013/$4015. The $06DD increment happens **before** the DMC priority rejection, and may therefore occur even on the rejected path. No PCM or actual sample priority correctness is inferred.

## Verification and branch matrix

The [JP0616 original-ROM branch evaluator](../tools/jp_sound_priority_paths_0616.py) verifies full JP ROM SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28, physical PRG24 source spans $8842..$885F, $8908..$8927 and $8928..$8953 by SHA-256 and precise opcode branch/data anchors. It executes **only** the audited subset of original NMOS 6502 instructions for these guards, stopping at known effectful boundaries instead of executing/resetting the rest of the sound engine.

The evaluator checks 256 command IDs × 256 old $019E values × 2 deliberately selected $0109 states (0x50 and 0x00): **131,072 symbolic combinations**. Of these **synthetic inputs** (not distinct original events):

| Branch destination | Synthetic input combinations |
|---|---:|
| $884F low state-guard return | 18,944 |
| $8860 record install without reset | 22,016 |
| $885D metadata reset then install | 15,872 |
| $8922 DMC priority RTS | 53,050 |
| $8928 DMC register programming | 21,190 |
| **Total** | **131,072** |

Every VM result matched the independent arithmetic/branch predicate, including DMC $06DD and $019E side-effect checks. Eight independent original source-byte mutations were rejected. The ROM-free --smoke command builds a small synthetic instruction fixture, uses the same 131,072-value domain, and asserts the full histogram; CI does **not** include the commercial ROM.

The combinatorial coverage is **not whole-NES 6502 correctness**, nor a proof the game ever supplies those A/RAM combinations. In particular JP0611's 131 PRG-wide JSR/JMP raw-byte patterns are not automatically executable producers. The previously authenticated PRG21:$B58C immediate $6B remains a conditional execution witness, not a naturally observed dropped sound.

## Independent-original execution instrument prepared (not yet run)

The [read-only Mesen Lua observer](../tools/mesen_jp_sound_gates_0616.lua) hooks the original ROM's low-guard and DMC gate entry/exit PCs. It requires software-tracked bank $23==$0C and E249 wrapper marker $26==$FF, and captures:

- $8842 entry followed by $884F guard RTS or $8860 install;
- $8908 DMC entry followed by $8922 priority RTS or $8928 register programming;
- $EF index, $019E priority and $06DD counter before/after, owner-local only.

The [Mesen gate-pair verifier](../tools/jp_mesen_gate_report_0616.py) requires the exact Japanese ROM and SHA-pinned Mesen2 v2.1.1 agent/core for *real* runs, a successful Mesen JSONL summary, no truncated Lua messages, and paired original gate PCs/states consistent with the original predicates. A ROM-free --smoke tests four synthetic pairs and rejects seven corrupted reference cases. **This Lua observer has not been executed against the pinned emulator here.** The original emulator's actual callback CPU-state field contract, mapper guard effectiveness and emitted events still require a real reference run.

## Reproduction

Local original ROM branch analysis:

    python3 JP/tools/jp_sound_priority_paths_0616.py --smoke
    python3 JP/tools/jp_sound_priority_paths_0616.py "$JP_ROM" --self-test --json "$PRIVATE/jp0616_gate_domain.json"

Original independent reference (owner-local; ensure the same reset and input schedule as the native request capture):

    mesen-agent "$JP_ROM" --home "$PRIVATE/mesen0616" --frames 520 --lua JP/tools/mesen_jp_sound_gates_0616.lua > "$PRIVATE/mesen0616.jsonl"
    python3 JP/tools/jp_mesen_gate_report_0616.py --rom "$JP_ROM" --emulator "$MESEN_BIN_DIR" --mesen-stdout "$PRIVATE/mesen0616.jsonl" --json "$PRIVATE/jp0616_mesen_gates.json"

The Mesen command is an example, not an executed artifact or matched native controller replay. The interpreter and agent output are not committed. The JP0614 native request CSV **does not include RAM $0109 or $019E at E249**, so its requests cannot be classified as accepted/rejected from existing fields alone; missing register writes do not establish suppression.

**Open R-007:** acquire actual independent original gameplay gate observations, reconcile to JP0614 sound requests in matched input frames, classify earlier producers and hardware-write ownership. Audio playback and VRC6/2A03 PCM mixing remain untouched.

**Accounting unchanged:** strict 49,504/262,144 (18.8843%) verified semantic PRG bytes, VPP 27/100, checkpoint 0508, fixed $FB96 investigation frontier. The three examined original sound code spans are source-verified but not newly certified semantic bytes; RESUME_STATE.json remains unchanged.
