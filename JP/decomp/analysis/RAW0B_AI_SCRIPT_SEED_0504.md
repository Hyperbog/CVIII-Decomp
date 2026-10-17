# Checkpoint 0504 — JP AI-script seed, handler closure and fixed $FC1F

Authoritative JP ROM SHA-256: 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.

This is ROM-backed **static control/data dependency coverage**, not a dynamic playthrough trace and not full native AI parity.

## Producer-derived script

The 0501-admitted raw bank $0B code contains:

    B503  LDA #$1B
    B505  STA $05EF,X       ; AI script ID
    B50D  JSR $B516
    B516  LDA #$00
    B518  STA $05C1,X       ; subscript index reset

Script ID $1B reads its pointer from $BED9-$BEDA (3A B0), selecting script data at $B03A. The following *three* four-byte records have confirmed action dispatch:

| record | JP record bytes | action | pointer pair | handler |
|---|---|---|---|---|
| 0, $B03A | 0B 0E 46 00 | $0B | $BD7D-$BD7E | $8519 |
| 1, $B03E | 45 30 00 00 | $45 | $BDF1-$BDF2 | $965D |
| 2, $B042 | 46 00 00 00 | $46 | $BDF3-$BDF4 | $96B4 |

Action $0B consumes record parameter bytes, updates animation/object data, and increments $05C1,X through $8357. Action $45 loads a record parameter, indexes five ROM tables, and increments $05C1,X at $9688. Action $46 decrements $061D,X and either repeats movement/timer logic or goes to object cleanup. Subsequent record liveness is **not inferred** from adjacency.

Raw-$0B handler $965D computes a table selector through TXA; ADC $1B; AND #$07; TAY, bounding each of the five eight-entry data tables. The exactly covered ranges are $968C-$9693, $9694-$969B, $969C-$96A3, $96A4-$96AB, $96AC-$96B3 (40 bytes total).

## Newly identified fixed PRG31 dependency

The action-$46 graph calls fixed PRG31:$FC1F from raw-$0B:$85F2. Recursively decoded graphs:

- Raw-$0B: 71 official instruction starts, 169 new instruction/operand bytes.
- Fixed PRG31: 185 official instruction starts, 335 new instruction/operand bytes.
- Fixed graph has no JSR, indirect JMP or mapper-register write; the call does not locally switch raw bank $0B.

Five **new direct shared-ZP $10 writers** appear in the fixed graph:

    FBFC  STA $10
    FC1F  STA $10
    FC4F  STA $10
    FCA0  STY $10
    FCF9  STY $10

These extend the candidate final-$10 writer domain beyond the seven previously proven raw-$0B collision writers. Neither checkpoint establishes every runtime path or the actual last writer before PRG26 OAM rendering.

The fixed helper reduces A modulo $0C at $FD1B before $FD25 reads $FD4D,Y: the 12 data bytes $FD4D-$FD58 are index-bounded. A *different* lookup at $FD18 ORA $FD62,Y remains **unbounded** because its Y producer is not yet proved; no data bytes reachable only through that lookup are promoted.

## Larger structural AI-script directory

Mechanical JP pointer interpretation for script IDs $00-$6A:

| Structural candidate metric | Count |
|---|---:|
| Script-ID pointer slots | 107 |
| Distinct pointer values | 72 |
| Distinct aligned pointer starts within $A4A6-$B0DE | 71 |
| Broad candidate region $A4A6-$B105 | 3,168 bytes |
| Four-byte lattice positions in that region | 792 |
| Distinct candidate first-byte actions | 163 |
| High-bit candidate first bytes | 73 |

**These are structural counts, not a claim that all 792 cells are live four-byte records or that all their first-byte values are executable actions.** The $BF79 fallback and high-action pointer alias require concrete JP script-ID and subscript producers before wider semantic promotion.

## Exact tracked new-byte accounting

| Mapping | Code and operands | Bounded data | New total |
|---|---:|---:|---:|
| Raw bank $0B | 169 | 60 | 229 |
| Fixed physical PRG31 | 335 | 12 | 347 |
| **Checkpoint 0504** | **504** | **72** | **576** |

Sixteen physical-bank-tagged, noncontiguous byte ranges are hashed and checked by the reproducible audit. Ordered manifest SHA-256: 4416db601cba553569d4ccc4aba410a6d843a6da3504dac1d735317ca1106eb4.

Reproduction command:

    python3 JP/decomp/tools/audit_ai_script_seed_0504.py "/path/to/Akumajou Densetsu (Japan).nes" optional_report.json

**Strict PRG floor: 48,823 → 49,399 of 262,144 = 18.8442%. VPP unchanged at 24/100.**

## Open provenance and next pass

- Bound $FD62,Y indexed-ROM producer domain, without synthetic bounds or counting unconsumed bytes.
- Trace more JP $05EF,X script-ID and $05C1,X subscript writers under proven mapper state.
- Intersect proven script records with action-table candidates before bulk handler promotion.
- Reconcile fixed-$FC1F ZP $10 writes with the object scheduler and PRG26 renderer entry state.
- Continue full native CPU/PPU/runtime parity independently of candidate structural coverage.

The physical fixed-tail investigation frontier remains $FB96, because 0504 admits two **noncontiguous** fixed spans ($FBF6-$FC16 and $FC1F-$FD4C). $FAA0-$FAA9 stays unclaimed.
