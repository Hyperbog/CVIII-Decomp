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
