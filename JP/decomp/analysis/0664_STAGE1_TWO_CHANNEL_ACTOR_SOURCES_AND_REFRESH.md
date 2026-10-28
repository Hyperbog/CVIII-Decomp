# JP0664 — Level 1-02 two-channel actor source and conditional refresh

**Source:** Original Japanese Akumajou Densetsu iNES Mapper24,
SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Physical 16KiB PRG **raw0A** mapped at CPU `$8000-$BFFF`, bank SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.
No original ROM or lossless room data is checked into Git.

## Implemented reusable source resolver

[`jp_stage1_actor_sources_0664.py`](../tools/jp_stage1_actor_sources_0664.py)
takes an authenticated private original cartridge and traverses the *original*
`$801E-$8046` three-tier room pointer hierarchy for the **conditional**
selector triple `$34/$35/$36=00/01/00`:

```text
word[$92AE]     = $92CC
word[$92CC+2]   = $9322
word[$9322]     = $93E8  (six two-byte room source cells)
```

The original `$8108-$8182` stage-source loader obtains source ID
from each cell's first byte. It dispatches through either `$9F6E`
or `$A06E` with the **8-bit ASL carry / $07F6** rule. The two
nonzero event-source selectors in this room are **slot 3 / ID $A0**
(pointer `$A444`) and **slot 4 / ID $9F** (pointer `$A43F`).
Both original five-byte records begin with event row `$32`.
Original `$8501` performs row dispatch through
`word[$8523+2*$32]=$8B26`, then event-zero entry
`word[$8B26]=$8B2C`. Event index initializes to zero.

The **other byte in each two-byte room cell** has a distinct source
consumer: `$818C-$81E9`, reading pointer tables `$A56B/$A66B`
and **four-byte auxiliary actors**. For six room phases
`$00-$05`, the `$8440` selection masks are `$01,$02,$04,$08,$10,$20`
of original RAM `$F0`. Conditional on those bits being clear:

| Phase | Source ID | Auxiliary source root | Source actor type | Original destination slot |
| ---: | ---: | ---: | ---: | ---: |
| 1 | $50 | $A893 | $80 | 14 |
| 2 | $50 | $A893 | $80 | 15 |
| 3 | $68 | $A8EF | $80 | 16 |
| 4 | $47 | $A86F | $80 | 17 |

Source phases 0 and 5 do not install auxiliary objects. The original
`$8047-$808E` initial six-cell path clears `$F0-$F3` first.
Type `$80` is **not** automatically labeled a candle or enemy;
object-handler/artwork identification is still open.

## Spatial event conditions — not a fabricated frame timeline

The original `$808F-$80D0` gate decides if `$80D1` should refresh
one source cell. On reaching this routine, the special
`$34/$35/$36=0E/01/01` branch and `$6B=0` suppress refresh.
Otherwise a refresh candidate is created in three bounded cases:

- `$53 & $3F == 0`: an aligned 64-pixel boundary;
- `$6B == 2` and `$53 & $3F == 1`: candidate `$53 & $FE`;
- `$6B not in {1,2,255}` and `$53 & $3F == 63`:
  candidate `($53+1)&255`.

When the candidate equals prior `$74`, no duplicate source
refresh occurs. Otherwise `$74` updates, `$80D1` computes the
source phase, and `$8106` loads the corresponding slot.
Separately, `$84EA-$8500` loops source slots `X=0..5` and calls
`$8501` only for nonzero `$07C2,X`; the row-$32 handler
`$8B2C` checks `$07E0,X`, then `$8DC1`/fixed `$FF06` gate
allocation. The handler's existing-type check is capped at three
among ordinary actor slots `1..8`. This is *activation logic*,
**not proof of the exact gameplay frame or offscreen spawn time**.

## Validation, boundaries, and next integration

Local original-ROM SHA validation, source-root/record resolution,
Python bytecode compilation and synthetic six-source / mask /
movement-boundary smoke **PASS**. The committed Python source has
the exact Git blob fingerprint of the locally executed source,
apart from an equivalent error-string expression. Independent
Mesen execution of row-$32 at original Stage 1-02 frame 3092 is
already documented by
[`0509_MESEN_ACTOR_LIVE_FINDINGS.md`](0509_MESEN_ACTOR_LIVE_FINDINGS.md)
and [source-field feedback](0509_MESEN_ACTOR_FEEDBACK_FINDINGS.md);
**it was not rerun for JP0664**.

Run with private original media (keep JSON private):

```sh
python3 JP/decomp/tools/jp_stage1_actor_sources_0664.py --smoke
python3 JP/decomp/tools/jp_stage1_actor_sources_0664.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --export-private "/private/jp-stage1-sources.json"
```

**No live native gameplay hookup, widescreen spawn fix,
full Stage 1 map, frame-accurate activation schedule, sprite-art
identity, independent original/native frame parity, VPP or strict
PRG-byte promotion is claimed.** Source/world X transformation
(`$09/$0A` and `$07DA/$07E0`), `$83D1` movement, and actual
viewport-driven lifetimes are the next causal integration boundary.
