# CVIII JP — Checkpoint 0508 Phase 4: bounded room-index producer contracts

**Status: PROVISIONAL; repository unchanged, no strict PRG-coverage promotion.** The immutable JP ROM is 393,232 bytes, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. This is supplementary evidence for existing R-001/R-002/R-004, not a complete live-state or frame trace.

## Regression and execution evidence

- The prior provisional Phase 1, Phase 2 and Phase 3 ROM-locked audits were replayed successfully. Phase 1 reproduces 0507's **281 starts / 582 candidate bytes**.
- The 0507 native `room_state_dispatch` contract/test was reproduced against the original JP ROM with `g++ -std=c++17 -Wall -Wextra -Werror -pedantic`: **65,536 / 65,536 test combinations pass**. The local C++ copy implements the same logic and assertions as the repository version; this is not a full CPU or frame-parity test.
- `audit_0508_phase4.py` passes **132,064 bounded executions** of four exact raw-ROM producer blocks and descriptor progressions; opcode support is explicitly limited and unmapped memory reads hard-fail.

| Entry (raw VRC6 bank, CPU) | Physical 8KiB PRG | Exact bytes | SHA-256 | Bounded result |
|---|---:|---:|---|---|
| `$00:$A099-$A0A8` | 01 | 16 | `c2cd21e0d8012509edb0a4a93fc057d23391a02ac9395a985c781ca23e035122` | `$07A0=0`, `$07A1=3F`, `$07C2=FF` |
| `$01:$BB57-$BB61` | 03 | 11 | `b7a361b8a6c870269d778d69058ff8412ff6bafcc19472e1146103d047b76401` | `$07A0 = ROM[$BB62 + (RAM[$30]>>1)]` |
| `$0A:$B622-$B62D` | 21 | 12 | `e0b08d1d1a6c965b7f28eb7a49bc3d792e9cd1860a5d9bd8804ba31ab7551d5c` | **if incoming `$32=1`**: reset `$07A6=0`, increment `$19`, return |
| `$0A:$B7DE-$B7F5` | 21 | 24 | `c7d36f38c567795505254644f2652345d7bfb36154d6d817253fcfd910f05b70` | Reset `$07A6`, increment `$07A0`, conditionally assign `$68` |

**Do not count these isolated physical spans as newly verified coverage:** this bounded evidence does not prove their dynamic reachability from reset/NMI or all external dependency edges. Data and instruction source bytes are ROM-verified, but the project's strict accounting remains unchanged.

## Exhaustive local producer relations

1. **`$B7DE`** — for all 256 incoming `$07A0` values × all 256 incoming `$68` values (**65,536 cases**): `$07A6'=00`, `$07A0' = ($07A0+1)&FF`, and `$68'=FF` **iff old `$07A0=04`**, else `$00`. Final flags are `C = (new $07A0 >= 5)`, `Z = (old $07A0 != 04)`, `N = (old $07A0 == 04)`. This proves an exact *local* state transition without assuming `$07A0` starts 0–4.
2. **`$B622`** — with explicit incoming `$32=01`, for all 256 incoming `$07A6` × all 256 incoming `$19` (**65,536 cases**): `$32'=00`, `$07A6'=00`, `$19'=($19+1)&FF`; final Z/N match that increment. For `$32` other than one, execution may branch to a more complex, not-closed path; no general reset claim is made.
3. **`$A099`** — 256 incoming `$07A0` choices: the short initializer always stores `$00` at `$07A0`, `$3F` at `$07A1`, `$FF` at `$07C2`. The caller and bank-selection context are not certified by this local test.
4. **`$BB57`** — 256 incoming `$30` values: Y becomes `RAM[$30] >> 1`; `$07A0` receives raw-bank `$01` byte `$BB62,Y`. In particular, `$30=06` selects `$BB65=35`, which writes `$07A0=35` if this routine executes. That is a concrete *conditional counterexample* to treating `$07A0<=4` as a global RAM invariant. **Actual cross-frame liveness is not proved.**

## Bounded descriptor series and pointer table

Phase 3 established that `$B873` loads nine three-byte records, with `$07A6` values 0–8 and a sentinel at value 9. Phase 4 chains ten uninterrupted `$B873` calls for each of 16 starting `$1E` values and three inherited `$10` values (**480 actual block calls**). Each of nine records emits 68 bytes and increments `$07A6`; the tenth sentinel emits none and sets carry. End state is `$07A6=09`, `$10=00`, queue index increased by **612 modulo 256**. This proof **requires no other writer to intervene** and does not show a game frame actually executes the ten-call sequence.

The first five encoded words at raw `$0A:$B8C2-$B8CB` are exactly `$BEA4, $BEDB, $BF03, $BE8B, $BF1C` (10 bytes; SHA-256 `38adbfe530adae4b238ccb265162d91938bb0f2010d6d35b1564fa44ed98c3f3`). `$B7F7` computes Y with 8-bit `ASL` on `$07A0`, so values beyond four read outside these five pointer words. Their table shape is **not** a live index bound; the raw-bank `$01:$BB57` indexed write underscores the unresolved producer-domain and bank/context problem.

## Candidate whole-PRG direct writer census

The ROM-wide *byte-start encoding scan* finds exactly these direct absolute store/RMW patterns, without establishing all are live instructions or excluding indexed/indirect aliases:

- `$07A0`: physical PRG01 `$A09B` (`STA`), physical PRG03 `$BB5E` (`STA`), physical PRG21 `$B7E3` (`INC`).
- `$07A6`: physical PRG21 `$B628` (`STA`), `$B7E0` (`STA`), `$B89F` (`INC`).

The correspondence with the four locally executed blocks is stronger than a raw byte pattern, but **does not close the global writer set**. A full RAM-alias analysis, executable call graph, cross-frame trace, and mapper restore contract are still required.

## Follow-up / strict accounting

- R-001: Prove the actual first-level selector values `$18=0C/0D`, predecessor `$19=13`, and uninterrupted cross-frame transition, including NMI/IRQ writes.
- R-002: Establish **live** `$07A0` and `$07A6` domains at `$B7F7` and `$B873`. Reconcile bank-$01`$BB57` versus bank-$0A room context; test `$FB96` temporary bank `$0E` reads and all helper exits.
- R-004: Determine whether the local `$10=0` is the final pre-render value or is subsequently overwritten by collision/object work or IRQ.
- Recovery: run the repository's original `JP/tools/audit_nmi_room_dispatch_0507.py`, the full `check_resume_frontier.py` and the preservation archive integrity audit against a complete current checkout before advancing `RESUME_STATE.json`.
- **Official ledger:** checkpoint 0507 remains last committed, strict PRG = **49,404/262,144 (18.8461%)**, VPP **24/100**, fixed PRG31 frontier **$FB96**. The 8–16 KiB **new strict bytes** target is not met. No branch commit/state file was changed.

## Reproduce

```sh
python3 audit_0508_phase3.py 'Akumajou Densetsu (Japan).nes' 0508_phase3_report.json
python3 audit_0508_phase4.py 'Akumajou Densetsu (Japan).nes' 0508_phase4_report.json
```

`audit_0508_phase4.py` imports the previous `audit_0508_phase3.py` for already-verified descriptor execution. Keep them alongside each other. The JSON report is machine-readable and carries explicit proof limits.