# JP0816 — Horizontal Level 1 source census; original `$B162/$B634` contact gate

**Delivery:** stacked on PR #16 / PR #13 resident Japanese Enhanced world.
Original ROM SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
(Mapper24 Konami VRC6, 393,232 bytes).
Original physical PRG16 raw0A SHA-256
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`;
raw0B SHA-256
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.

## 1. Authenticated horizontal source code, not an inferred spawn list

The original `$801E-$8046` hierarchy resolves *seven horizontal*
Stage0 selectors, with four-byte groups **containing two sequential
event-ID/aux-ID pairs** each. Stage1 `00/01/01` is the separate
seven-byte vertical chapel, not a horizontal pair stream.

| Selector ($34/$35/$36) | Root | Source pairs |
|---|---:|---:|
| 00/00/00 | $93CC | 14 |
| 00/01/00 | $93E8 | 6 |
| 00/01/02 | $93F4 | 14 |
| 00/01/03 | $9410 | 10 |
| 00/02/00 | $9424 | 14 |
| 00/02/01 | $9440 | 14 |
| 00/03/00 | $945C | 14 |

**Total 86 source pairs**, containing **26 nonzero event IDs**
and **45 nonzero auxiliary IDs** across those source cells.
The authentic `$8001` computes a **byte-sized source phase**
from the sixteen-bit `$54:$53` camera (add2 then
`ASL/ROL` twice), and original `$80D1` adds **5**
to that byte when `$62` is nonzero. `$8108` looks up the
six-slot destination `$8410[phase]`; no phase beyond the
48 verified indices is silently accepted.

The original `$8111-$813C` event selection uses the source
ID's `ASL` carry, pointer tables `$9F6E/$A06E`, and
original flag `$07F6` when high-bit IDs are encountered.
Auxiliary sources independently use `$818C-$81E9`,
`$A56B/$A66B`, and the `$F0-$F3` install mask.

**Critical opening-room example:** actual source pair at
`$93D6` (phase5) is event ID **`$D1`** / auxiliary
ID **`$46`**. With original `$07F6=0`, ID `$D1`
resolves to an **empty** row (`$A12E`); with
`$07F6 != 0`, it resolves to **row `$02`**
(`$A520`). Auxiliary source ID `$46` resolves to
type **`$80`** at `$A86B`, but is separately
subject to the original mask/installation condition.
The two `$32` sources in `00/01/00` at phase3/4
remain the bounded earlier independently witnessed Stage1-02
event route (JP0509/0510). **None of these IDs alone
authorizes a permanent offscreen spawned actor.**

`cviii_horizontal_sources_0816.h` imports only typed/source
metadata from the owner-private SHA-authenticated raw0A bank.
`cviii_world_preload_horizontal_0816` stores metadata for
all 7 horizontal rooms alongside existing JP0812 resident
room payloads; no ROM code bank is retained. During verified
horizontal gameplay frames, `cviii_world_observe_horizontal_0816`
chooses the current source phase from actual original
`$53/$54/$62/$07F6`, with exact 8-bit wrap and bounds.
It **never writes guest RAM, forces an original loader,
increments an event script or fabricates an actor**.
The observation epoch resets on savestate while original room
source data remains resident.

## 2. Source correction: type `$80` does NOT reach `$B162`

Original raw0B `$B1F8-$B231` first rejects
`$0470,X & $11 != 0`, zero `$0400,X` and types
`>=$83`. At `$B20B` the original
`CMP #$80; BCS $B258` **bypasses** `$B162`
for `$80-$82`. The independent older natural Mesen Stage1
actor X15/type `$80` had `$0470,X=$81`;
it is rejected even earlier at `$B1F8` on that state.
Prior JP0815 speculative `MAY_ROUTE_B162` for type80
was **wrong and has been explicitly retracted**.

Eligible types `$69-$7F` with `$7E & $F0 == 0`
reach `$B162` through `$B217`.
The original `$B162-$B182` dispatch has five
typed exceptions: `$73->$B227`, `$75->$B1D1`,
`$6A->$B106`, `$6F->$B10C`, `$70->$B109`.
Other supported types call **`$B634`**. This is
*not* proof of a damage/pickup interaction.

`cviii_collision_route_0816.h` faithfully returns the
original entry's first destination PC; it does **not**
execute the branch response. The new bounded pure function
`cviii_b634_gate_0816` reproduces just the first
`$B634-$B672` carry result:

- Original `$80B3` computes absolute 8-bit *linear*
  X difference, not wraparound shortest-path distance.
- `$BB80+type` plus `$BB05+playerGroup`
  is added modulo 256 and compared with that distance;
  far-X returns carry set through `$B632 SEC/RTS`,
  transferring to **`$B115`**.
- When near in X, source `$B673+playerGroup`
  plus player Y forms `$10`; source
  `$BC08+type` subtracts from actor Y to form `$11`.
  Original `$B707` absolute difference, `CMP #$0C`,
  selects carry clear to **`$B18A`** or
  carry set to **`$B115`**.
- Restrict to legitimate `$B1F8->$B162->$B634`
  entry, actor X1..18 and group `$7F<9`.
  No caller may apply these radii to type `$80`.
  Source RAM and original private bank are *read only*.

**Beyond the bounded endpoint:** `$B115/$B18A`
reaction code, the `$B80E` helper, actor interactions,
damage, treasure/pickup behavior, native offscreen AI and
world-wide spawn timing remain independently unproved.

## 3. Verification and release scope

A local independent original-ROM audit checked the complete
commercial image and both physical bank SHA-256 fingerprints,
five original instruction-window hashes
(`$8001-$801D`, `$80D1-$8107`,
`$B1F8-$B231`, `$B162-$B189`,
`$B634-$B672`), seven typed source roots,
**all 86 original event-pointer pairs (both `$07F6` variants)**,
every auxiliary pointer, and the opening-phase5 contrast:
**PASS**. The companion committed owner-local
[`jp_stage1_horizontal_collision_0816.py`](../tools/jp_stage1_horizontal_collision_0816.py)
reproduces this audit and has a ROM-free `--smoke` mode.

Native C11 regression targets added to the existing owner
NESRecomp CMake/CTest configuration:
`jp_horizontal_sources_test_0816` (original phase, high-bit fallback,
out-of-range and transactional failures);
`jp_collision_route_test_0816` (524,288 synthetic route combinations,
plus type80 and B162 special-case guards);
`jp_collision_b634_test_0816` (synthetic near/far X/Y carry and excluded types).
The existing `jp_level1_world_test_0803`
was extended to test all seven resident horizontal resources,
`$07F6` selection and state-load clearing.
**These updated C11 targets and Windows native gameplay were not
executed in this analysis session**. Their cases are test definitions,
not claimed passes; owner-native CTest and original Mesen
controller-reached parity remain required.

```sh
python3 JP/decomp/tools/jp_stage1_horizontal_collision_0816.py --smoke
python3 JP/decomp/tools/jp_stage1_horizontal_collision_0816.py \
  --rom "/private/Akumajou Densetsu (Japan).nes"
cmake --build <owner-native-build> --target \
  jp_horizontal_sources_test_0816 jp_collision_route_test_0816 \
  jp_collision_b634_test_0816 jp_level1_world_test_0803
ctest --test-dir <owner-native-build> --output-on-failure -R JP0816
```

No ROM, sprite artwork or active source table payload is shipped.
Original gameplay/collision remains authoritative; **no actual
offscreen enemy hitboxes, pickups or new actor simulations** are
enabled. Strict PRG certification **49,504/262,144** and
VPP **31/100** unchanged. The next causal task is natural
source-activation sampling across opening/side-scrolling rooms
(especially the actual `$07F6` producer and masked auxiliaries),
then original `$B115/$B18A` reaction classification before
considering offscreen interaction changes.
