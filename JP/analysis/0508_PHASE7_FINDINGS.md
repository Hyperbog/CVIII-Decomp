# Checkpoint 0508 Phase 7 — Conditional two-entry NMI state handoff

**Status:** PROVISIONAL ROM-backed bounded 6502 execution, not a reset-to-frame trace and not a completed 0508 checkpoint. Authoritative JP ROM: SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (393232 bytes; mapper 24 VRC6a).

## New verified conditional transition

The predecessor NMI first-level selector `$18=$0C` selects fixed PRG31:$E51E through the `$E363` inline table. Fixed `$E51E: A9 0A 20 D0 E2 4C A4 AF` sets raw VRC6 bank `$0A` via fixed `$E2D0`, then transfers to raw-`$0A:$AFA4` (physical PRG21). When **incoming RAM $19=$13**, `$AFA4: A5 19 20 FB E7` uses the actual fixed `$E7FB` routine and the inline pointer word at `$AFCF-$AFD0` to tail-jump to raw `$0A:$B36B`.

```asm
B36B AD 89 07   LDA $0789
B36E 8D 81 07   STA $0781
B371 A9 0D      LDA #$0D
B373 85 18      STA $18
B375 A9 00      LDA #$00
B377 85 19      STA $19
B379 60         RTS
```

The handler returns through the original synthetic parent stack frame; the `$E7FB` routine consumes only the intermediate inline-JSR return. End state: `$18=$0D`, `$19=0`, `$0781=$0789`, mapper/tracked `$23=$0A`; Y and X preserved.

**Under the separate explicit assumption that no other game code changes $18/$19 before the next corresponding dispatch**, the next first-level selector `$18=$0D` selects fixed `$E526`, re-establishes raw bank `$0A`, transfers to `$B4CC`, and `$E7FB` fetches `$B4D1-$B4D2` for selector `$19=0`. Its target is `$B570`. This second execution intentionally stops **at** the handler entry; it does not execute `$B570` or its external callees.

## Reproducible instruction/stack/mapper proof

`tools/audit_0508_phase7.py` models the exact JP instruction bytes at each step, 6502 JSR/RTS push/pop, the `$E7FB` PLA/inline pointer/JMP-indirect ABI, zero-page reads/writes and 8-bit flags. It hard-fails on unsupported opcodes, unmapped CPU reads/writes, unexpected banking, stack imbalance, or wrong pointer/flags.

Exhaustive cross-product: **256 initial $0789 values × 256 saved Y values = 65,536 executions of the two-entry sequence**; first half has 30 instructions and reaches synthetic parent return `$9000`, second has 23 instructions and reaches exactly `$B570` with the untouched parent return still on the stack. Pointer reads are respectively `$AFCF,$AFD0` and `$B4D1,$B4D2`. The restored Y gives the final Z/N flags, and the 8-bit ASL sets carry clear for both selectors `$13` and `$00`.

ROM byte witnesses:
- raw VRC6 `$0A`, physical PRG21 `$AFA4-$AFA8`: SHA-256 `0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7`;
- raw VRC6 `$0A`, physical PRG21 `$B36B-$B379`: SHA-256 `bf540ae8289f46a474fb7e476e43fffca9c6da8bf8ac48c2e67f62e497c0668c`;
- fixed PRG31 `$E7FB-$E813`: SHA-256 `d2adbf45aa9746eb53ba2e8ec8513cb338f8fd30f4bc3627074f186c14439091`.

## Deliberate boundaries

1. **R-001 OPEN:** There is no reset-to-first-NMI proof that `$18=$0C`, `$19=$13` is a live pair. The two calls use synthetic parent return context, not a full NMI/PPU/CPU-frame simulation. The second call assumes unchanged selector state between invocations; ordinary admitted IRQ paths preserve these fields as separately proved by [Phase 6](0508_PHASE6_FINDINGS.md), but all other NMI and banked writers remain open.
2. **R-002 OPEN:** The entry at `$B570` is not run. The `$07A0` source domain, carry gate, five-entry pointer table, and complete room-loader path remain conditional.
3. All preexisting NMI/IRQ/mapper code bytes used here were either previously audited or are conditionally decoded; this test **does not** establish globally live semantics or justify promoting new bytes. **Strict added PRG: 0; floor 49,404/262,144 (18.8461%); VPP 24/100.** Fixed PRG31 frontier `$FB96`; last completed machine state remains 0507.
4. No full original-hardware/trace parity or live gameplay occurrence is asserted. The 8–16 KiB strict new-byte goal remains unmet.

## Reproduction

```sh
python3 JP/tools/audit_0508_phase7.py 'Akumajou Densetsu (Japan).nes' 0508_phase7_report.json
```

The audit is standalone, uses the original JP ROM and emits deterministic JSON. It is a new zero-byte provisional research unit, not an update to `RESUME_STATE.json`.
