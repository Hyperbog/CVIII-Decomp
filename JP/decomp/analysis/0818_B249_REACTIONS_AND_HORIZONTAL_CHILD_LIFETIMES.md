# JP0818 — Original $B249/$B258 continuation and horizontal source-child lifetime

**Scope:** Original Japanese Castlevania III Mapper24 VRC6 cartridge, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Physical original 16KiB PRG bank0A SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`;
raw bank0B
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
No original ROM, copyright-bearing bank dump, CHR graphics or savestate is committed.
This PR is stacked on PR #13 resident world through draft PR #16.

## 1. The original $B249 and $B258 are different entries

Authenticated original raw0B `$B249-$B257` (15 bytes) first saves actor
slot `X` into zero-page `$8E`. It compares original actor
`$0438,X` against player `$0438`, saving `$8D=1`
when actor X is **less** than player X, otherwise `$8D=0`.
Control then falls through to `$B258`. A call/branch
directly to `$B258` does **not** write those scratch bytes.

Authenticated original `$B258-$B27F` tests actor type:
- `$16` or `$37` branches straight to **`$B1F7 RTS`**.
- Types **`$61-$7E`** also branch to **`$B1F7 RTS`**.
- Types below `$61` except the special two, and types
  `$7F+`, reach `$B26B`. There, original
  `$068D,X & 1`, `$0630` and `$0413` decide
  whether to jump directly to **`$B29D`** or to
  call **`$B27C JSR $B3EC`**. `$B3EC`'s carry
  then chooses further contact work and is outside this boundary.

**Important correction to initial JP0818 scratch interpretation:** the
`DEC $068D,X` instruction is at **`$B1F4`**, immediately *before*
the `$B1F7 RTS`. The original `$B258` relative branches
end at the `$B1F7` RTS, **not** inside `DEC`.
No original `$068D` decrement is licensed by those branches.
This was corrected in the native code and exhaustive tests
before native acceptance.

The pure `cviii_collision_continue_0818` returns original first-stop
PC, predicted `$8E/$8D` only when entry was `$B249`, the
current actor type and whether `$B3EC` would be needed.
It **does not write** the guest RAM. Its 2048 synthetic
type/guard combinations are compared to an independent
branch-structure oracle. No damage, pushback, whips,
subweapon hits, candle destruction, pickups, score or
offscreen collision behavior is implemented.

## 2. Original event source -> actual child ancestry

Original raw0A `$8B2C-$8B73` row-`$32` event handler,
already observed in native Mesen Stage 1-02 gameplay
(JP0509), allocates an original child via `$8D76`
after the count/free-slot checks and calls `$8B50`.
The original `$8B50` writes:

- `$0470,X |= $04` — original child/source flag.
- `$0645,X = $69` — original **SOURCE** slot index
  `0..5` saved by the `$84EA` dispatcher.

Original `$8D5E` indexes source row
`$32` into `$9194+$32 = $13` (initial script byte)
and `$91EC+$32 = $3D` (allocated actor type).
The parent-source field and flag provide more specific
witness than type `$3D` or apparent sprite proximity alone.

`cviii_horizontal_child_0818()` accepts an authentic
original actor slot X=1..12 **only if**:
`$054E,X=$3D`, `$0470,X&$04!=0` and
`$0645,X<6`. Its output independently reports
whether parent source `$07C2,parent=$32` *currently*
persists and whether sprite frame/bit7 is an eligible
rendering candidate. These are **not** hitboxes and
do not imply an exact historical spawn frame.
When original source is gone but allocated actor
remains, the parent-link evidence survives, although
future parent-slot reuse may make ancestry ambiguous.
We do NOT replace the original parent pointer or
recreate a deallocated child.

The existing Stage 1 native host now snapshots this
witness alongside JP0817's six-source activation
observer for authenticated **horizontal rooms only**.
A world-internal observed child transition count is
a difference between sampled original-RAM snapshots
in one room; it is **not** a proven Mesen spawn count
and cannot establish offscreen CPU scheduling.
Source-parent and sprite visibility are distinct
from original guest actor allocation. Reset/save-state
clears volatile observer history while leaving
authenticated resident world source data intact.

## 3. Reproducibility and acceptance

```sh
python3 JP/decomp/tools/jp_stage1_reaction_lineage_0818.py --smoke
python3 JP/decomp/tools/jp_stage1_reaction_lineage_0818.py \
  --rom "/private/Akumajou Densetsu (Japan).nes"

# Owner C11 NESRecomp build; original ROM and external runtime privately supplied:
cmake --build <owner-native-build> --target \
  jp_collision_continuation_test_0818 jp_horizontal_child_test_0818 \
  jp_level1_world_test_0803
ctest --test-dir <owner-native-build> --output-on-failure -R JP0818_
```

The owner-original bank and seven instruction-range SHA-256 fingerprints
are authenticated, with independent original opcode tests for the
`$B249` side, `$B258` relative return targets,
`$B26B` guards, the distinct `$B1F4 DEC/$B1F7 RTS`,
`$8B50` parent linkage and row32 type/script bytes.
Tests model only synthesized RAM and input states.
Windows CTest includes new standalone bounded
continuation and ancestry tests; full resident-world
test also exercises initial source link, persistent
allocated-but-hidden actor, actual type-zero removal,
wrong-room rejection and observer resets.

**Still missing for original-vs-Enhanced gameplay parity:**
natural emulator frame/writer breakpoint at
`$8B50` with owner-original input, a consecutive
source-parent/actor deallocation log across horizontal
room transitions, downstream `$B3EC` and
`$B29D-$B317` contact loop/effect classification,
and interaction QA for a larger-than-256-pixel view.
This checkpoint **does not create independently active
offscreen enemies or pickups**. Original NESRecomp
collision/AI/OAM remains authoritative.
No strict PRG/VPP accounting increase:
**49,504/262,144 strict PRG bytes, 31/100 VPP**.
