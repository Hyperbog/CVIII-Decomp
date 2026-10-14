# 07 — Sound Bytecode, Audio Sources, APU and VRC6 Sound

**Status:** PARTIAL data/parser decompilation; full output audio and native mixer parity OPEN. Evidence [bank $0C parser](../analysis/NMI_BANK0C_PARSER_MODE.md), [bank $04 alt parser](../analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md), [bank $05 closure](../analysis/NMI_BANK05_PRG11_TAIL.md).

## Distinguish three layers

1. **Serialized musical data / sound-bytecode parser** in physical JP PRG banks, under specific mapper states.
2. **Audio scheduler and hardware-register effects** (APU $4000-$4017, VRC6 extra square/saw channels), affected by NMI/IRQ timing.
3. **Final rendered waveforms**, resampling, expansion mixing and frame-cycle synchronization; not yet parity-certified.

Parser-data closure is neither proof of timing, register waveform parity, nor a native sound engine.

## Audited metadata and root domains

- Raw VRC6 bank $04 alternate parser (physical PRG08/09): **96/96 metadata roots** recursively closed by the 04F7–04FA audits.
- Raw bank $05 alternate parser (physical PRG10/11): **72/72 roots** closed through 04FD. Last 04FD tail was CPU $AD97-$BF05, 4,463 byte dependency span, with 5,346 abstract parser states and 3,433 unique decoded command addresses across the final remaining roots.
- Raw bank $0C sound parser graph was studied in 04F5/04F6. Its use of shared zero-page scratch is audited within a specific NMI context; do not generalize that every path preserves $10.

This is an exact count of **specific discovered root families**, not a census of every possible sound/track in the game. NSF metadata and US sound architecture are accelerators, not authoritative JP code.

## Stateful stream grammar and bounded parameters

The alternate parser tracks context-sensitive `FB` loop anchors, `FD` call/return, `FE nn` loop counts, and `FE FF lo hi` absolute stream-pointer operands. Operand width matters: **all four bytes of `FE FF lo hi` must be accounted** before following the target. In raw bank $05, the audited decoded $E7 command high-nibble domain is precisely $0, $2, $8, all landing within the ten-word instrument table $8430–$8443 and resolving through $8444. This **does not authorize arbitrary host-side index clamping** for other unproved producer values. [04FD source](../analysis/NMI_BANK05_PRG11_TAIL.md).

## Audio/native port contract

Port the bytecode interpreter as a state machine retaining loop/call stacks, bank-aware pointer reads, signed/unsigned integer effects and original termination rules. Reproduce actual APU/VRC6 write order at CPU-cycle granularity as needed. Hardware reference: user-provided EveryNES/NESDoc, NESdev and the MOS manual for CPU timing and register syntax, **not** evidence that the game schedules a channel in a particular way.

**Open:** all live music/SFX selector domains, envelope/voice allocation, NSF↔ROM mapping completeness, exact VRC6 pulse/saw synthesis, APU frame IRQ arbitration, output traces and per-track golden audio.

## Provisional 0508 Phase 10 — sound command $6B channel reset

[Original-ROM bounded audit](../analysis/0508_PHASE10_FINDINGS.md) identifies the state-one sound command $6B and actual bank-$0C:$87AE reset path. The executed reset clears nine sound-channel state slots and issues nine ordered bus writes: $4000/$4004/$400C=$30, $4001/$4005=$7F, $9000/$A000/$B000=$00, $4015=$0F. The $8F55 delay contains ten NOPs and RTS, modelled as instructions, not cycles. The audit stops at $8860; downstream song-pointer parsing and proper RTS are unverified. An independently injected hypothetical return only checks the mapper-restoring suffix. No audio waveform/frame parity or VPP increase.


## Provisional 0508 Phase 11 — command $6B installs six bank-$05 instrument roots

[Executable JP-ROM audit](../analysis/0508_PHASE11_FINDINGS.md) follows sound command $6B through its natural $8850 RTS, **not** an injected return. The sound-ID pointer at raw-$0C:$9034 selects a 20-byte metadata record at $94B5. Six slot/pointer pairs 0/$BB48, 1/$BBEA, 2/$BD42, 3/$B90A, 4/$BA14 and 7/$BAC9 all select source bank $05. Fixed $E19F executes six temporary $05 reads, returning $D9 for each; the instrument mode initializer consequently sets bit 0 of $011B,X to zero in those slots. These are **installed streams**: later per-frame parsing, decoded sound contents, APU/VRC6 waveform parity and exact audio timing remain OPEN. Audit: 256 seeds × 650 instructions; strict byte increment zero.


## Cross-title Konami music-driver comparison research (unproved hypotheses)

The [SharedNES Konami-family queue](../SharedNES/KONAMI_DRIVER_HYPOTHESES.md) records a sourced community hypothesis that Castlevania III/Contra/Gradius II share a music-driver lineage, while Metal Gear and Madara fall under another; Esper Dream 2 is listed as a distinct/unknown variant. This ranking is not a ROM similarity proof and **cannot raise sound VPP**, but provides a rational selection order for a user-supplied additional commercial ROM. Original JP sound code still controls all claims. No cross-game source code was imported.

## JP0611 — Proven request entry; ROM-wide call sites remain candidates

The original fixed PRG31:$E249 wrapper saves the tracked mapper bank, enters raw bank $0C:$8850 and restores the prior bank. The $8850 decision separates incoming A into $00-$4F (state-check path $8842), $50-$6E (record reset/installation), and $6F-$FF (DMC programming path $8908, including $4010-$4013/$4015). [ROM-locked audit](../tools/jp_sound_request_census_0611.py) and [source findings](../analysis/0611_SOUND_REQUEST_ENTRY_CENSUS.md) locate 123 JSR + 8 JMP $E249 **byte-pattern candidates**; 120 have adjacent A9/immediate signatures, 11 do not. No code/operand liveness is inferred from these physical patterns. Real command acceptance, rejected events before register writes, music/SFX ownership, native synthesis and audio parity remain OPEN (R-007). This adds no new strict PRG bytes or VPP points.

## JP0612 — Original $E249 request-entrance trace (observer, not polyphony)

The [new private opcode-fetch overlay](../tools/patch_cyc_sound_requests_0612.py) captures the original ROM-authenticated fixed PRG31:$E249 command input (A), X/Y/S/P, CPU cycle, tracked mapper bank $23 and uninterpreted stack bytes, through both generated-code and interpreter fallbacks. The [bounded logger](../native/enhanced/cviii_sound_requests_0612.c) emits `CVIII-Sound-Requests.csv` during the same opt-in `-AudioTrace` session as JP0610's `CVIII-Audio-Registers.csv`. It excludes interrupt-discarded fetches and does not alter APU/VRC6 programming or SDL audio. This captures entries, **not** all earlier game-side event producers, accepted voice ownership or original-internal cancellations. Synthetic C11 and overlay contract tests pass; real retail GUI/MesenCE correlation is OPEN. No strict PRG/VPP increase.

## JP0613 — Paired request/register timing report (noncausal)

[JP0613](../analysis/0613_SOUND_REQUEST_REGISTER_PROXIMITY.md) adds a strict two-schema checker for the original $E249 request trace and actual 2A03/VRC6 register-write log. It produces owner-local bounded forward-cycle **proximity windows** only. Per-file cycle regressions fail closed; save-state epoch/session correspondence between the two files remains unproved. A nearby register rewrite neither proves that a command caused it nor that the game accepted/rejected a music/SFX voice. The ROM-free CI fixture is not retail gameplay evidence. R-007 remains OPEN, with no strict PRG or VPP increment.

## JP0614 — Session identity and save-state epoch boundaries

[JP0614 source and verification limits](../analysis/0614_AUDIO_SESSION_EPOCH_PROVENANCE.md) introduce an owner-only power-on/state-loaded marker CSV recording GUID, CPU cycle and cumulative JP0612 request/JP0610 register-log row counts. Launcher-created SHA-256 manifest binds all three files. The verifier splits CPU-time epochs even when a saved game rewinds the CPU cycle counter; the old JP0610 whole-file analyzer is skipped for multi-epoch captures. Synthetic strict-C11/Python tests pass, but owner-original-ROM/MesenCE sound attribution and runtime build remain unverified. R-007 OPEN; no music/SFX separation, PCM alteration, semantic PRG or VPP increment.

## JP0615 — Independent original-JP E249 request-execution reference gate

[JP0615 source and reference contract](../analysis/0615_MESEN_SOUND_REQUEST_REFERENCE_GATE.md) adds a MesenCE/Mesen2 read-only NES CPU execute callback at fixed $E249 and a comparator against one manifest-verified JP0614 native power-on epoch. The original full-ROM check also pins physical raw-$0A PRG21 immediate calls at $B0C8 ($06), $B1CE ($6A), and $B58C ($6B). Only the last has the historical conditional 0508 Phase 11 original-6502 execution proof; the first two are byte-pattern callers, not independently live source events. The comparator tests A/X/Y/S/P (virtual bits masked), software bank $23, raw stack bytes, and separately reports request cycle deltas. ROM-free synthetic tests pass; actual Mesen2 agent execution and matched native sound traces remain missing. Neither "silenced effects" nor independent music/SFX voices are proved. R-007 remains OPEN; no additional strict PRG/VPP points.

## JP0616 — Original low-command and DMC software rejection predicates (ROM-backed)

[JP0616 original sound-dispatch proof](../analysis/0616_ORIGINAL_SOUND_DISPATCH_GUARDS.md) authenticates source byte ranges in physical PRG24: low command A<$50 reaches $8842; if $0109==$50 and A>=$06, $884F returns before record install. High command A>=$6F enters $8908, sets index A-$6F, increments $06DD when index>=$0D, and returns at $8922 without DMC register writes when prior $019E>=$05 and index<prior $019E. The $06DD increment can precede this rejection; accepted requests update $019E and proceed at $8928 to original DMC hardware programming. Exact-ROM bounded branch evaluation passed 131,072 **synthetic state combinations**, including eight ROM corruption rejections, not 131,072 live sounds. Mesen2 callback and strict event-pair parser are prepared for owner-local original gameplay proof, but were not executed against original Mesen2 here. No independent SFX voices, mute changes, software mixer, new PRG/VPP credit or completed R-007.

## JP0617 — Unified original request/driver-decision provenance

[JP0617 source contract](../analysis/0617_UNIFIED_SOUND_DISPATCH_REFERENCE.md) adds a single original Mesen2 Lua sound command-to-outcome observer, beginning after $8850 stores A at $8852. This closes the observability hole in the separate JP0616 entry/exit callbacks: metadata commands $50–$6E execute the reset JSR at $885D **then** proceed to common $8860 install, rather than producing two independent outcomes. Each original request ID now requires one terminal with a verified branch predicate and post-decision state, with a separate $885D phase for metadata. ROM-free negative fixtures reject missing phases, orphan/duplicated requests, bad DMC counter wrap and malformed reset epochs. The original Mesen agent and matched native gameplay have not been executed here: request rejection frequency, sound producer ownership and PCM/audio parity remain unproven. R-007 OPEN; no new strict PRG/VPP credit.

## JP0618 — Enhanced-only player gains, master bus implemented

[JP0618](../analysis/0618_ENHANCED_AUDIO_LEVELS.md) confirms Enhanced as the sole shipping port with **original gameplay behavior retained as the default baseline** and deliberate enhancements allowed. Native C11 now persists Master, Music and SFX numeric 0–100 integer settings with 1% steps and 100% defaults. Enhanced Master gain scales the host's already mixed PCM (not emulated 2A03/VRC6 registers); Music and SFX settings are intentionally **not yet applied**, since the original mixer has not produced separately owned music/effect buses. Final three-row interface must use verified original health-bar graphics and in-game font numerals, not the generic host UI. Strict standalone C11 tests pass locally, but Windows audio/UI playback remains unverified; R-007 source separation stays OPEN.

## JP0619 — Actual health-bar/font tiles for Enhanced audio options

[ROM-backed JP0619 CHR identities](../analysis/0619_AUTHENTIC_AUDIO_SLIDER_ART.md) confirm original 0–9 numeric font tiles $1041..$104A, Latin A–Z $1050..$1069, empty two-cell health meter $1085 and filled meter $1093, with the authentic JP ROM SHA256 and four source-CHR block hashes. A developer-only C11 presentation overlay renders Master/Music/SFX rows, original meter segments and numeric values 0–100, including pixel-clipped 1% increments; colors remain a selected approximation pending live original palette witness. No gameplay input, pause or true separate music/SFX gains are connected yet. ROM-free strict C11 pixel tests and original ROM tile-source audit pass locally; Windows GUI and Actions unverified. Enhanced only for players, original gameplay physics/timing baseline retained, R-007 sound independence remains open.

## JP0620 — Interactive Enhanced Audio UI, source ownership not inferred

[JP0620](../analysis/0620_PAUSED_ENHANCED_AUDIO_MENU.md) now wires an original-CHR health-bar/font F6 audio modal via a private pinned SDL host overlay: pause/input isolation, three 0–100 values with 1% keyboard/D-pad steps and saved preference updates. This is **not** evidence of independent original Music/SFX voice ownership; Music/SFX are explicitly marked PENDING and only Master attenuates final PCM. RGB palette still provisional. Local C11 registry and SDL patcher synthetic smoke PASS; actual Windows native SDL run or Mesen sound-source trace not claimed. R-007 remains OPEN.
