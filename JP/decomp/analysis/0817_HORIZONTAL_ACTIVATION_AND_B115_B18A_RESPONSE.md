# JP0817 — Horizontal Stage 1 source activation and $B115/$B18A responses

**Owner cartridge:** Japanese Akumajou Densetsu Mapper24 SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Verified source physical 16KiB PRG raw0A SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`;
raw0B SHA-256
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
ROM and savestates are not checked into Git.

## Source activation trace — exact decision boundaries

Original raw0A `$84EA-$8500` loops **six scheduler SOURCE slots X=0..5**.
Only nonzero `$07C2,X` dispatches `$8501` then invokes
`$83D1`; zero-row slots skip both. The original `$8501-$8522`
dispatcher uses row `$07C2,X`, event nibble
`$07C8,X & $0F`, indirect pointer tables and source handler calls.
Those handlers are *not* all the same. The common
`$8CDD` allocator gate, **if that handler calls it**, first
checks original `$53=0` and `$07E0,X=0`, then fixed
`$FF06` scans ordinary actor slots 1..12.
Hence **nonzero event row ≠ successful actor spawn**.

`cviii_horizontal_activation_0817.h` reads actual guest
`$07C2/$07C8/$07DA/$07D4/$07E0` and records
the row, event state, positions, optional common-gate
eligibility and first empty actor slot.
It computes the original `$83D1-$840F` next-step
coordinate/page result **without applying it**:

- If signed `$65` is nonnegative, subtract `$6B`
  from `$07DA,X` with original 8-bit borrow and
  update the one-bit page `$07E0,X`.
- If `$65` is negative, add `$6B` to
  `$07D4,X` with original carry/page arithmetic.
  When the resulting page is one, original `$83D1`
  clears `$07C2,X`, disabling later source dispatch.
- If source row is already zero, `$84EA`
  skips `$83D1` entirely.

The authenticated native host records six **actual original
CPU source-slot states** after verified horizontal game frames,
plus source-row transitions and event-index changes.
Observation counts are neither spawn counts nor full original
instruction timelines. Slot and trace epochs reset on save-state
restore; source tables remain resident.

## $B115 / $B18A bounded original interaction-state semantics

Original raw0B `$B162` is entered **only for eligible
types $69–$7F** through the ordinary collision entry.
Type `$80` bypasses this path at `$B20B`
(documented correction JP0816).
The existing JP0816 `$B634` gate returns first proximity
carry and transfers to **`$B115`** (carry set) or
**`$B18A`** (carry clear). Neither means a confirmed
damage or pickup event.

The JP0817 bounded pure function
`cviii_response_b115_b18a_0817` predicts only
`$7E`, `$AC`, `$0669,X`, first-stop PC and
`$B80E` carry, without writing emulator RAM:

- **At `$B115`**: `$7E=1` jumps to
  `$B258`; otherwise `JSR $B80E` is evaluated.
  Far `$B80E` carry branches `$B258`.
  When near, original type `$6D` uses
  `$0657,X` to select `$7E=$0C`; type
  `$72` selects `$7E=$1C` or `$0C`
  using `$0606,X/$0657,X`; other supported
  types use original `$B0E3` source table.
  The bounded next PC is `$B249`.
- **At `$B18A`**: special type
  `$6E/$74/$76/$77/$78` checks
  `$AC` ownership against `$B5`.
  The matching owner exits to `$B258`;
  a different owner clears `$AC` and the
  original accumulator before table lookup.
  `$6D/$72/$73` have `$0657,X` sources;
  other supported types use `$B0E2`.
  The modeled path writes `$7E` and
  `$0669,X=$10` *as a returned prediction*,
  then stops at `$B249`.
- **`$B80E`** uses `$BB80/$BB05` horizontal
  clearance and adjusted vertical distances
  from `$B97D/$BC08`. Original negative
  vertical subtraction uses `EOR #$FF`
  **without +1**, making the negative branch
  one pixel asymmetric. The pure comparison
  preserves that 6502 behavior.

`$B249/$B258`, their downstream event effects,
`$B80E` scratch stores/flags as a complete
CPU replay, damage, drops, pickups, and
offscreen actor AI are **not** implemented.
This is a decision/state reconstruction, not
complete collision-response parity. Types outside
the previous `$B634` call domain are rejected.
No unauthenticated game state is synthesized.

## Tests and evidence grade

`jp_stage1_activation_response_0817.py` checks
the original SHA-locked `$84EA/$83D1/$8501`,
`$B115/$B18A/$B80E/$80B3` opcode windows
and type table `$B0E2`; ROM-free smoke
tests wrap/borrow and the asymmetric vertical compare.
Two native C11 source-specific test targets plus the
existing JP0803 full-world integration test are wired
into owner CMake/CTest and the horizontal native frame
observer. **Tests are source-derived/synthetic until
a new independent Mesen natural-game trace is provided.**

```sh
python3 JP/decomp/tools/jp_stage1_activation_response_0817.py \
   --smoke --rom "/private/Akumajou Densetsu (Japan).nes"
cmake --build <owner-native-build> --target \
  jp_horizontal_activation_test_0817 jp_collision_response_test_0817 \
  jp_level1_world_test_0803
ctest --test-dir <owner-native-build> --output-on-failure -R JP0817
```

**Next proof requirement:** native/original side-by-side event
frames at the `$84EA->$8501->$83D1` boundary
and actual `$B115/$B18A->$B249/$B258` effects,
then natural horizontal offscreen object activation
and collision acceptance. **No strict PRG/VPP increase**.
