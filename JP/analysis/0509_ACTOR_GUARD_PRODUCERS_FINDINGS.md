# 0509 actor guards: ROM-stepped source producers, not game-frame liveness

**Evidence grade: PROVISIONAL.** The original JP ROM (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`) supports a bounded producer family for the `$53` and `$07E0,X` checks at raw VRC6 bank `$0A:$8CDD`. These tests intentionally use synthetic RAM, not an independent original Mesen frame trace.

## Exact raw-bank $0A producer domains

The literal `STA $07E0,X` three-byte encoding occurs at exactly **four offsets** in raw bank `$0A`: `$8154`, `$82A5`, `$83EE`, `$8402`. This is a source-byte encoding census, **not a complete global writer or a proof of executable boundaries by itself**. The bounded CPU audit independently steps each site with authentic opcodes:

| Writer | Bounded source behavior | Test cases |
|---|---|---:|
| `$8154` | `$814E: LDA $0A; ADC #0; AND #1; STA $07E0,X`. Incoming carry is explicitly controlled; result is `(RAM[$0A]+C)&1`. The earlier upstream ADC is not executed. | 512 |
| `$82A5` | `$829E` initializes `$07D4,X` from `$0A`, then clears `$07E0,X` and `$07C8,X`. | 256 |
| `$83EE` | `$83D1` with `$65` sign clear subtracts `$6B` from `$07DA,X`; high-field result is `($07E0,X - sign($6B) - borrow)&1`. | 65,536 |
| `$8402` | `$83D1` with `$65` sign set adds `$6B` to `$07D4,X`; high-field result is `($07E0,X + sign($6B) + carry)&1`. If the resulting bit is one, it also clears `$07C2,X`. | 65,536 |

The `sign($6B)` term means `0xFF` for a negative eight-bit `$6B` and zero otherwise; arithmetic is actual 6502 carry/borrow, not host signed arithmetic. `X` varies from 1–12 in the test. The two `$83D1` routes are tested for **all** 256 movement-byte values times **all** 256 low-coordinate values each. Incoming `$07E0,X` is a reproducible varied fixture, not a proof that every possible upstream value occurs during gameplay. Source flag, stores, scratch `$00`, $07C2 and stack checks pass.

## Fixed-bank $53/$54 producer evidence

Original, already-credited PRG31 `$FB7A-$FB87` increments `$53` as low byte and `$54` as high byte; `$FB88-$FB95` decrements them. Each body was stepped for all **65,536** input pairs, verifying exact 16-bit wraparound and byte store order (131,072 additional cases). This establishes the pair can be a counter and its low byte is not a permanent boolean. It **does not** prove the pair's global game-frame meaning or all writers; `$53` has source encodings in other banks and different callers.

## Reproduce / recovery limits

ROM-locked audit: `python3 JP/tools/audit_actor_guard_producers_0509.py ORIGINAL_JP_ROM --report /tmp/actor_guard.json`.

**Total** 262,912 source-execution cases, **3,280,384** authentic original instructions, 55 distinct instruction addresses. [Compact report](0509_actor_guard_producers_report.json), deterministic SHA-256 `ebbf4fa40d13909161b93293f8d3e4aff9e7e2a16bf8972f48cb2a9ca2791b8b`. Four exact ROM block hashes reside in the report; the fixed range is already part of certified prior coverage. The source-specific arithmetic witnesses do **not** close the `$53/$07E0,X` interframe writer domains, prove live entry into `$90C5`, show a mapper-stable call, or establish stage behavior.

**No strict promotion:** 49,504 / 262,144 (18.8843%); VPP 26/100. Last completed semantic checkpoint 0508; first unprocessed fixed byte FB96. Task R-004 and actor-allocation game-frame liveness remain OPEN.
