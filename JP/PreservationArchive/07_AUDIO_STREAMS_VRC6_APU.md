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
