# JP0819 — Original `$B3EC` player preflight, `$B29D–$B31F` partner contacts, and horizontal child lifetime census

**Delivery branch:** `jp0813-level1-source-world-lifetime`, draft PR #16 stacked on PR #13's original-ROM-authenticated persistent Level 1 Enhanced world.

## Primary Japanese ROM evidence

Owner-supplied Japanese Akumajou Densetsu mapper24 VRC6 ROM SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
(393,232 bytes). Physical PRG raw0A SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`,
raw0B SHA-256
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
The original `$B3EC-$B446`, `$B29D-$B31F`,
`$B323-$B338`, `$B447-$B47A`, `$80B3-$80D4`
are original **raw0B** code (not raw0A); original source
`$8B2C-$8B72` is **raw0A**. Instruction-window SHA-256
fingerprints and key branch operands are independently checked by
`JP/decomp/tools/jp_stage1_interaction_lifetime_0819.py`.
No original ROM bytes or copyrighted graphics/savestates are committed.

## 1. Source-faithful `$B3EC` preflight

The original raw0B `$B3EC: JSR $80B3` computes the **absolute
linear** unsigned-byte X distance between original actor and player
`$0438,X` and `$0438`. `CMP #$80; BCS $B446` immediately
returns carry set if distance is >=128. For smaller differences:

- `$0561` indexes four entries each of `$BB17` and
  `$BB1B`, the additional original clearance offsets.
- `2*$0561 + $04A8` indexes the eight-entry `$BB1F`
  player X offset; original `$0438` is added modulo 256
  to form scratch `$10`.
- Original `$042F + $BB27[$7F]` forms scratch `$11`.
  The nine `$7F` entries are individually bounded.
- **When `$B7 != 0`**, `JSR $E5BE` may select the
  `$B767` alternate path. That helper's carry and its
  side effects have **not** been reconstructed: the new
  function reports `UNKNOWN`, stopping at `$B41F`,
  not inventing a hitbox/contact event.
- With `$B7=0`, compare `abs($0438,X-$10)` against
  byte-wrapped `$BB80[type]+$BB17[$0561]`.
  An X distance equal to or above clearance yields
  carry set at `$B446`.
- Otherwise compare `abs($041C,X-$11)` against
  byte-wrapped `$BC08[type]+$BB1B[$0561]`;
  equal-or-above yields carry set, below yields carry clear.

`cviii_b3ec_preflight_0819()` is a pure decision model over
original RAM and the caller's already-authenticated private raw0B
bank. It rejects unsupported table indices and cannot update
original CPU, OAM, collision flags, AI, pickups or damage.
It is **not** an independently scheduled offscreen collision.

## 2. `$B29D–$B31F`: three special partner slots

Original `$B29D` sets `$9B=$14` and loops
through original actor slots **20, 21, 22** until `$9B=$17`.
Each pass:

1. `$054E,Y=0`: skip the empty slot through `$B317`.
2. `JSR $B323` takes current actor `$068D,X` and
   maps partner slot 20/21/22 to index 0/1/2. Its original
   `$B320` mask table is **`$02, $04, $08`**.
   Already-contacted masks skip this partner.
3. `JSR $B447` checks proximity between original X actor and
   special partner. The ordinary partner-type path reads two
   original radius tables `$BB60[partnerType]` and
   `$BB6B[partnerType]`, combined with current actor
   `$BB80[type]` and `$BC08[type]`. Original
   `$80CB/$80C1` return absolute byte differences.
   **Partner type `$05`** instead reads `$0593,X`
   and table `$BB76`: model refuses that branch.
   `$B7!=0` also defers to the unverified `$E5BE` path.
4. When an unmasked partner is near, original execution calls
   `$B727` at **`$B2B5`**, then merges contact bits
   into `$068D,X`, combines `$0606,Y/$0669,X`,
   propagates `$0657,X` to `$061D,Y`, and may call
   `$B6CE`, `$B5DF` or `$B486`.
   These are **interaction-producing original guest-code paths**,
   not pure proximity checks.

`cviii_partner_scan_0819()` reports which original partner
slot/mask would be examined and where it would first reach a
side-effecting path. It stops before `$B727` and does not
reproduce or invent any of those effects; all-three-skip yields
`$B31F RTS`. Unsupported partner types/helpers report
`UNKNOWN`, not an invented collision.

## 3. Authentic horizontal source/actor lifetime snapshot

Earlier JP0818 source proof:
original raw0A `$8B50` sets `$0470,X & $04` and copies
original source slot `$69` into `$0645,X`.
Together with original actor type `$054E,X=$3D`,
this witnesses current row32-associated ordinary actor slots
1..12; it does **not** prove exact historical spawn time.

`cviii_parent_census_0819()` groups up to twelve current
original row32 children by the exact six `$0645,X`
source indices. Each source reports original actor-slot
bitmask, number of currently allocated children, eligible
visible sprites, original source row `$07C2`, event byte
`$07C8`, and whether a child still exists after its
original source row ceases to equal `$32`.

The already-existing native Stage1 horizontal observer invokes
this snapshot alongside JP0818's original child identity
checks. World metadata retains counts of only **sampled
slot-mask additions/removals** and sampled source-row releases
while a child is still allocated. Differences across room
switches are NOT counted as definite deaths or spawns;
actor slot and parent source slot reuse remain possible.
Savestate/Enhanced mode resets clear these volatile counters
while leaving authenticated source tables resident.

This source-to-child consistency supports later native
offscreen world work but does **not** extend the game's
original actor lifetime, create an extra actor, wake enemy
AI, add hitboxes or enable outside-viewport pickups.

## 4. Verification and bounded acceptance

Owner-ROM audit confirms raw0A and raw0B hashes, six original
source-window SHA-256 ranges and original branch bytes for
`$B3EC`, `$B7/$E5BE`, the `$B29D` scan,
`$B320` mask bits, special `$B447` dispatch and
the `$B2B5` first side-effect boundary.
ROM-free `--smoke` compares 65,536 byte-pair absolute
differences and all three mask bits.

Native C11 tests added:
`jp_interaction_preflight_test_0819` exercises original
near/far X/Y paths, high-distance rejection, `$B7`
unresolved helper, unknown pose/group and three
empty/masked/near/far partner branches.
`jp_horizontal_lineage_test_0819` checks source-linked
siblings, hidden actor visibility, cleared original source
and actual allocator slot removal. The existing native
`jp_level1_world_test_0803` also checks per-source
retention, observed release and save-state reset.
Windows CI explicitly runs both JP0819 CTest targets.

```sh
python3 JP/decomp/tools/jp_stage1_interaction_lifetime_0819.py \
  --smoke --rom "/private/Akumajou Densetsu (Japan).nes"
cmake --build <owner-native-build> --target \
  jp_interaction_preflight_test_0819 jp_horizontal_lineage_test_0819 \
  jp_level1_world_test_0803
ctest --test-dir <owner-native-build> --output-on-failure -R JP0819_
```

**Not verified:** fresh natural controller-input Mesen samples at
`$B3EC`, `$B727`, source-to-child creation/despawn
through horizontal camera scroll, special `$B7/$E5BE`
logic, partner-type-5 `$0593` handling,
complete `$B6CE/$B5DF/$B486` response effects,
actual cross-viewport enemy AI and pickups, original-vs-Enhanced
visual/damage parity. The PR remains draft until those are proved.
No new strict PRG byte certification or VPP credit
(**49,504/262,144**, **31/100**).
