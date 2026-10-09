# 0508 Phase 10 — state-one bank-$0C sound reset and conditional room-state advance

**Status:** PROVISIONAL Japanese-ROM-backed bounded execution. This is **not** proof of the rest of the audio parser, frame liveness, stage progression, or a completed 0508 semantic checkpoint. Source: JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (393,232 bytes; mapper 24 VRC6a).

## Call chain: verified actual 6502 prefix

Phase 9 ends the *conditional* room-state-zero handler with `$19=1`, `$68=0`, raw VRC6 bank `$0A`, and `$07A0=$07A6=0`. When the following NMI selects room state one, the original JP code is:

```asm
raw $0A:B58C  A9 6B       LDA #$6B
raw $0A:B58E  20 49 E2    JSR $E249
raw $0A:B591  20 E9 B4    JSR $B4E9
raw $0A:B594  E6 19       INC $19
raw $0A:B596  60          RTS
```

Fixed PRG31:$E249 first `PHA`s the command, writes `$26=$FF`, saves the tracked PRG bank `$23` into `$25`, selects bank `$0C` through `$E2D0`, restores the command into A, and calls `$8850`. The mapped bank-$0C dispatcher stores `$EF=$6B`; comparisons `CMP #$6F/BCC`, `CMP #$50/BCC` prove that **this particular immediate value** takes the `JSR $87AE` sound reset branch, not the low-command branch `$8842` or high effect branch `$8908`. Bank `$0C` is physical 8 KiB PRG24–25; the `$8850/$87AE` instructions are in PRG24. The caller `$B58C` is physical PRG21.

`$87AE-$8818` clears nine channel-state slots at `$0109-$0111` and `$06D3-$06DB`, plus auxiliary sound fields; the original ROM issues **nine APU/VRC6 register writes** in this exact order:

| Order | Register | Value |
|---:|---|---|
| 1 | `$4000` | `$30` |
| 2 | `$4004` | `$30` |
| 3 | `$400C` | `$30` |
| 4 | `$4001` | `$7F` |
| 5 | `$4005` | `$7F` |
| 6 | `$9000` | `$00` |
| 7 | `$A000` | `$00` |
| 8 | `$B000` | `$00` |
| 9 | `$4015` | `$0F` |

The sound reset invokes `$8F55` (ten `NOP` opcodes followed by `RTS`) between register writes; this audit models each instruction, but **not** 2A03/APU cycle-accurate audio. It stops at **`raw $0C:$8860`**, *after* `$87AE` has returned and *before* `$8850` reads song-pointer/record data and performs more dynamic state updates. At that stop `$23=$0C`, `$25=$0A`, `$26=$FF`, `$EF=$6B`, initial X/Y are restored, and room `$19/$68/$07A0/$07A6` and scratch `$10` are preserved. These are actual observed states within the bounded ROM-fetched execution.

## **Separate hypothetical-return continuation — do not present as executed sound parser**

`$E249` resumes at fixed `$E25B` **if** `$8850` eventually executes an ordinary `RTS` and leaves saved `$25` valid. The audit checks the exact pending JSR return `$E25A` on the stack, then **explicitly injects that one return** without interpreting instructions `$8860` onward. With that declared assumption, it executes the real fixed suffix `$E25B-$E263`, which clears `$26=0`, loads `$25=$0A`, and tail-jumps through `$E2D0` to restore mapper bank `$0A`. It then runs `$B591: JSR $B4E9`, setting `$68=0`, and `$B594: INC $19`, moving `$19=1 → 2`, before returning to the synthetic parent. This is a *postcondition for a properly returning callee*, **not** proof the callee completes or preserves its scratch values.

## Reproducible ROM / machine witness

`JP/tools/audit_0508_phase10.py` imports the previous Phase 9 bounded 6502 CPU, extends mapped reads to use the actual `$23`-tracked bank, implements the remaining needed opcodes, and rejects unknown memory-mapped writes. It checks whole-ROM identity, four pinned original ROM byte sequences and the `$8F55` delay, stack return bytes, sound side effects, bank-write order, all 256 incoming X values (one associated Y/RAM seed each), and the conditional suffix.

**256 cases** pass; each case executes **200** original 6502 instructions to the sound-prefix cutpoint, plus **13** original suffix/room-state instructions after the explicitly injected external return. The latter 13 are never counted as proof of the unexecuted `$8850` interior. Runs are deterministic and emit [JSON](0508_phase10_report.json).

ROM SHA-256 witnesses:

- Fixed PRG31 `$E249-$E263` (27 bytes): `5a5d7b8a0f857c8062faee305b4d752522f281bda0271e402cd4c66759b37324`.
- Raw bank `$0C:$87AE-$8818` (107 bytes): `6fe5b943edcb25a747b13b82afd72551d493792ef1436368b4df015744d53b6e`.
- Raw bank `$0C:$8850-$885F` (16 bytes): `4b34e6a8e7ff0524f45c3cd38e5419aed65a513e7a5dd1d89c6e7420e1ba4790`.
- Raw bank `$0A:$B58C-$B596` (11 bytes): `753c598e794761b9ac19ae468525ee15991d0ce4cf91f68db97570d908ae83dd`.

## Open obligations and conservative ledger

- **R-001:** Initial `$18=$0C/$19=$13` pair still lacks an independently live reset-to-frame producer. The state-one entry is conditional and the experiment does not simulate NMI/IRQ timing.
- **R-002:** To close room state one into live state two, decode `$8850` from `$8860` through its data/script loops, fully reconcile `$25` preservation and bank switching inside `$E19F`, and prove any relevant sound-branch return. Do not treat the synthetic continuation as real sound-parser execution.
- **R-004/R-007:** Local sound reset preserves shared `$10` and changes actual audio registers, but does not certify the sprite-renderer last writer or an audio waveform/event trace.
- **R-009:** The fixed PRG31 tail `$FB96` remains unclaimed. No new strict physical PRG bytes are admitted solely because a tested entry exists behind an unproved live selector.

**Strict new PRG bytes 0; strict cumulative 49,404/262,144 (18.8461%); VPP 24/100; last completed checkpoint 0507; fixed frontier `$FB96`.** No original ROM, lossless PRG listing, or emulator dump is committed.

Run:

```sh
python3 JP/tools/audit_0508_phase10.py 'Akumajou Densetsu (Japan).nes' JP/analysis/0508_phase10_report.json
```
