# PRG02/PRG03 IRQ dispatch analysis

## Context

`PRG31:$E0F5` is the IRQ vector. At `$E100` it loads bank value `$01` and calls raw VRC6 16 KiB bank select `$E2D2`. Therefore, during IRQ dispatch:

- CPU `$8000-$9FFF` = physical `PRG02`
- CPU `$A000-$BFFF` = physical `PRG03`
- `$E000-$FFFF` remains fixed `PRG31`

The IRQ handler loads zero-page `$6A`, executes `ASL A`, and branches to the common `$E118` exit if carry is set. Thus values with bit 7 set bypass the pointer table. Otherwise the doubled value indexes a little-endian pointer table at `$9F01,Y/$9F02,Y`, and the handler executes `JMP ($0000)`.

NESdev documents VRC6a `$F000/$F001/$F002` as IRQ latch/control/acknowledge registers and confirms mapper 24's 16 KiB `$8000-$BFFF` bank plus fixed `$E000-$FFFF` bank:

- https://www.nesdev.org/wiki/VRC6
- https://www.nesdev.org/wiki/VRC_IRQ

## 2026-10-03 boundary correction

The first pass incorrectly extended the table through indices `$2D-$2F` and therefore incorrectly claimed a code/data overlap at `$9F60`.

Fresh direct disassembly proves that was wrong.

The table is exactly:

- start: `$9F01`
- end: `$9F5A` inclusive
- size: `$5A` bytes = 90 bytes
- entries: **45** (`$00-$2C`)

The next byte, `$9F5B`, is the first opcode of a real referenced helper:

```asm
9F5B  CE 81 07  DEC $0781
9F5E  D0 26     BNE $9F86
9F60  A5 7A     LDA $7A
...
9F86  60        RTS
```

`$9F5B` is called from `$A090` and `$A185`, independently proving it is code. Therefore `$9F5B+` must **not** be interpreted as additional IRQ pointer entries. There is no proven `$9F60` code/data overlap from this structure.

This correction is important methodology: a sequence of plausible little-endian addresses is not sufficient evidence to extend a table past a directly referenced code entry.

## Proven dispatch table

| state | target | state effect / exit |
|---:|---:|---|
| `00` | `E118` | terminal/common IRQ-disable exit |
| `01` | `A078` | no `$6A` change; `$E118` exit |
| `02` | `A0A8` | `$6A++ -> 03`; `$E11D` acknowledge/continue exit |
| `03` | `A0CF` | remains `03` while `$0780 != 0`; otherwise `$6A++ -> 04`; `$E11D` |
| `04` | `A102` | no change; `$E118` |
| `05` | `A10D` | `$6A++ -> 06`; `$E11D` |
| `06` | `A120` | `$6A++ -> 07`; `$E11D` |
| `07` | `A14B` | `$6A++ -> 08`; `$E11D` |
| `08` | `A16F` | no change; `$E118` |
| `09` | `A1D5` | `$6A++ -> 0A`; `$E11D` |
| `0A` | `A1FA` | no change; `$E118` |
| `0B` | `A10D` | `$6A++ -> 0C`; `$E11D` |
| `0C` | `A120` | `$6A++ -> 0D`; `$E11D` |
| `0D` | `A18B` | `$6A++ -> 0E`; `$E11D` |
| `0E` | `A1B1` | `$6A++ -> 0F`; `$E11D` |
| `0F` | `A1FA` | no change; `$E118` |
| `10` | `A235` | `$6A++ -> 11`; `$E11D` |
| `11` | `A243` | no change; `$E118` |
| `12` | `A249` | no change; `$E118` |
| `13` | `A293` | `$6A++ -> 14`; `$E11D` |
| `14` | `A2E2` | all completed paths reach `$A2F3`; `$6A++ -> 15`; `$E11D` |
| `15` | `A310` | no change; `$E118` |
| `16` | `A01C` | no change; `$E118` |
| `17` | `9FD5` | `$6A++ -> 18`; `$E11D` |
| `18` | `9FE3` | no change; `$E118` |
| `19` | `9FA1` | no change; `$E118` |
| `1A` | `A323` | assigns from `{1B,1B,1C}` indexed by `$0782`; `$E11D` |
| `1B` | `A340` | assigns from `{1D,1C,1D}` indexed by `$0789`; `$E11D` |
| `1C` | `A357` | `$6A++ -> 1D`; `$E11D` |
| `1D` | `A36B` | no change; `$E118` |
| `1E` | `A3A8` | if `$078A==0`, `$6A++ -> 1F`; else no change; `$E11D` or `$E118` |
| `1F` | `A3ED` | if `$078B==0`, `$6A++ -> 20`; else no change; `$E11D` or `$E118` |
| `20` | `A405` | no change; `$E118` |
| `21` | `A3A8` | if `$078A==0`, `$6A++ -> 22`; else no change; `$E11D` or `$E118` |
| `22` | `A420` | no change; `$E118` |
| `23` | `9F99` | no change; `$E118` |
| `24` | `A293` | `$6A++ -> 25`; `$E11D` |
| `25` | `A2DD` | falls into `$A2E2`; `$6A++ -> 26`; `$E11D` |
| `26` | `A316` | `$6A++ -> 27`; `$E11D` |
| `27` | `A2EA` | converges on `$A2F3`; `$6A++ -> 28`; `$E11D` |
| `28` | `A310` | no change; `$E118` |
| `29` | `A497` | `$6A++ -> 2A`; `$E11D` |
| `2A` | `A4B2` | `$6A++ -> 2B`; `$E11D` |
| `2B` | `A4DF` | `$6A++ -> 2C`; `$E11D` |
| `2C` | `A4EC` | no change; `$E118` |

The highest sequential chain is therefore explicitly closed:

```text
29 -> 2A -> 2B -> 2C -> terminal/no increment
```

There is no table state `$2D`.

## `$E118` versus `$E11D`

These are intentionally distinct exits in fixed `PRG31`:

```asm
E118  A9 00     LDA #$00
E11A  8D 01 F0  STA $F001   ; VRC6 IRQ Control
E11D  8D 02 F0  STA $F002   ; VRC6 IRQ Acknowledge
E120  A5 23     LDA $23
E122  20 D0 E2  JSR $E2D0   ; restore tracked 16 KiB PRG bank
...
E130  40        RTI
```

Per NESdev's VRC IRQ documentation, writing `$F002` acknowledges the pending IRQ and applies the control register's A->E behavior; writing `$F001` also acknowledges and changes control state. Therefore `$E118` explicitly writes zero to IRQ Control before acknowledge, while `$E11D` enters at acknowledge without that control write. A native model must preserve the distinction.

## `$6A` / `$43` producer audit

NMI copies the frame IRQ seed from `$43` into active IRQ state `$6A`:

```asm
E073  A5 43     LDA $43
E075  85 6A     STA $6A
```

`$E616` clears both:

```asm
E61A  A9 00     LDA #$00
E61C  85 6A     STA $6A
E61E  85 43     STA $43
```

A raw whole-PRG byte-pattern scan was reconciled against code/data context. Executable `$6A` mutations are the NMI copy, the fixed clear, the IRQ-handler `INC $6A` instructions listed above, and the two table assignments at `$A332/$A34F`. Apparent `STX/STY $6A` and the PRG22 `85 6A` byte sequence occur in tables/inline data, not accepted instruction boundaries. In particular, the PRG22 sequence follows `JSR $E7FB`; `$E7FB` pops the JSR return address and indexes inline pointer data, proving the apparent `85 6A` is data consumed by the inline-dispatch helper.

For `$43`, all accepted writes resolve as follows:

- fixed clear at `$E61E` -> `00`
- direct immediate seeds observed in code: `01,05,0B,10,12,13,16,17,19,1A,1E,21,23,29,80`
- helper `$8E97` stores A to `$43`; all direct call/jump sites supply `09`, `02`, or `13/24` depending a branch
- `$94D9` restores `$43` from `$A3`; `$B55A` proves `$A3` is a snapshot of the prior `$43`, so this introduces no new value
- `$9A67` executes only after `CMP #$01` succeeds, so it writes `01`

Raw non-`STA` byte-pattern hits for `$43` were checked in their surrounding ROM regions and fall inside table/graphics/data streams rather than accepted executable boundaries.

The currently proven active state domain is therefore table states `$00-$2C` plus the high-bit bypass sentinel `$80`. The table itself is only accessed when bit 7 of `$6A` is clear.

## Local helper at `$9F5B`

`$9F5B` decrements `$0781`. When it reaches zero it uses low nibble `$7A` to choose a pointer from `$9F8B`, reloads `$0781` from the selected stream, advances `$0780`, and updates `$3D`; `$FF` wraps the stream cursor back to 1. This helper is called by handlers `$A078` and `$A16F` on their `$7A & F0 == 40` paths.

## Next required proof

1. Reconcile the exact semantics/valid domains of `$0780/$0781/$0782/$0789-$0794` used by the multi-step IRQ programs.
2. Trace the frame-side routines that choose direct `$43` seeds and connect them to gameplay/render states.
3. Continue the `PRG26:$817F` sprite-pointer-table and 28-slot object-array analysis.
4. Begin a reusable native VRC6 IRQ state-machine implementation only after those RAM contracts are stable.
