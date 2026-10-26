# JP0739 — First causal write to $62 / player vertical-action state

**Finding:** first *incorrect CPU write* remains **unproven** from the recovered
JP0718 original and JP0719 native files. This is a bounded original-ROM source
census and preserved forensic gate, not a gameplay fix or a new Mesen run.

## What the saved evidence actually records

Verified original Japanese Mapper24 ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

JP0718 Mesen `*-events.tsv` has **16,099** event rows:
15,699 `PPU_WRITES`, 256 `SNAPSHOT`, 76 `TARGET_STATE`, 28
`LOOKUP_ENTRY`, 28 `LOOKUP_RETURN`, 11 `RAM_CHANGE`, and one
`TARGETS_REACHED`. **All 11 RAM_CHANGE events are $35/$36 selector
writes** (four $35, seven $36). There are zero historical event records
identifying a live CPU PC/value for writes to $62, player action $0565,
Y speed $0520 or player Y $041C.

JP0719 native captures **245 periodic full 2KiB-RAM samples**, with
no individual 6502 PC, memory-write callback, preceding register state,
PRG bank at write, or $4016 read-phase trace. All 17,562 original input-poll
masks match the original JP0719 native schedule, but **identical scheduled
button masks do not prove identical guest CPU reads**.

| Original sampled frame | $62 | $63 | camera X | player Y | action $0565 | Y speed $0520 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9376 | 2 | 0 | 0 | 96 | 20 | 0 |
| 9440 | 1 | 0 | 10 | 128 | 4 | 0 |
| 9504 | 0 | 32 | 49 | 101 | 12 | 5 |
| 9576 | 1 | 64 | 93 | 155 | 8 | 5 |

| Older JP0719 native **nominal** frame | $62 | $63 | camera X | player Y | action $0565 | Y speed $0520 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9368 | 2 | 0 | 0 | 102 | 20 | 0 |
| 9432 | 2 | 0 | 0 | 128 | 4 | 0 |
| 9496 | 0 | 32 | 54 | 128 | 4 | 0 |
| 9560 | 2 | 32 | 56 | 44 | 26 | 0 |
| 9592 | 2 | 32 | 56 | 128 | 24 | 0 |

**Caution:** historical frames are **not cycle-aligned**. An apparent mode
disagreement at original 9440/native 9432 cannot establish an incorrect
store. Native X camera stays at 56 across its own 9560/9592 observations,
while the original has reached 93 by 9576. The original Y/action/Y-speed
state is already different in the 9504 neighborhood, before the sustained
native camera stall. This is a **divergence envelope**, not an identified
misexecuted 6502 opcode or exact first mismatching frame.

## Original-Japanese direct-store candidate map

`jp0739_mode62_writer_census.py` locks the authentic ROM identity, verifies
11 local candidate CPU instruction neighborhoods, and enumerates all raw
byte patterns for **direct** zero-page `STA/STX/STY $62`. Its authentic
source run finds **10 STA, 3 STX, 1 STY** byte-pattern hits across the entire
256KiB PRG. These raw matches may include non-code data or operands;
they do not include indirect/indexed/aliased writers and are **not proof
of live execution**.

| Raw PRG bank / candidate CPU PC | Bounded original store | Statical result / hypothesis |
| --- | --- | --- |
| $0E:$86E2 | `STA $62` | mode 1, room/player boundary |
| $0E:$86F8 | `STA $62` | mode 0 |
| $0E:$8748 | `STA $62` | mode 1, player X/edge branch |
| $0E:$877D | `STA $62` | mode 0, left-side branch |
| $0E:$936E, $9C11, $9C54, $A58D | four `STA $62` | each mode 2, action-dispatch entry candidates |
| fixed bank30:$C997 | `STA $62` | **table-selected** from `$CA32,Y`, not a constant store |
| fixed bank30:$C99C | `STA $62` | mode 2 |
| fixed bank30:$CA08 | `STX $62` | mode 0 after `LDX #$00` |

Other literal patterns in raw banks $00 and $07 are also listed in
the JSON output. No exact `STA/STX/STY $62` *literal pattern* is present
in raw $0D, even though RAM $23 indicates bank $0D at the sampled
boundaries; bank switching and indirect/aliased stores remain possible.
**Do not infer runtime bank from the saved $23 alone.**

The fixed-bank source at $D2FE uses **existing $62**; it is not shown to
produce an incorrect $62. Mode 0/1 camera movement updates $53/$54/$55
using velocity; mode >=2 returns through the $6B delta path. At
$D340–$D348 camera high-five-bit boundary is checked against $63.
At original 9504 $63 is $20, rising to $40 by 9576; older JP0719 native
remains $20 at its 9560/9592 samples. This makes upstream action,
vertical-motion and mode selection the next source family to investigate,
**not** a reason to change the correct $D2FE arithmetic.

## Exact proof gate / uncompleted evidence

Determining the **first incorrect write**, rather than the first mismatched
state *sample*, requires physically mapped original and native CPU writes
to $62, $0565, $0520, $041C, and collision/scroll dependencies, ordered by
instruction time, plus equivalent controller latch/read timing. These
records do not exist in the recovered captures. They cannot be fabricated
by scanning opcode patterns or by interpolating sparse RAM samples.
A later JP0737 CYCFRAME frame log is a **different native executable**
and has not been supplied here; do not claim JP0719 is JP0737 execution.

Run without ROM in CI:
`python3 JP/decomp/tools/jp0739_mode62_writer_census.py --smoke`.
An owner-private source census is optional:
`python3 JP/decomp/tools/jp0739_mode62_writer_census.py --rom original-japanese.nes`.

**No gameplay, controller, PPU or native-handler changes.**
Certification remains **31/100 VPP** and **49,504/262,144 strict PRG bytes**.
