# JP0820 — Original $B727 contact effects and horizontal source-reuse-safe lifetime observations

**Scope:** Source-qualified Japanese VRC6 ROM interaction prefix, stacked on the original PR #13 resident-world runtime and draft PR #16. No ROM, private savestate, graphics or raw Mesen trace shipped.

## Original contact-effects, physical raw0B

The owner-provided Japanese cartridge SHA-256 is
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`;
raw0B bank SHA-256
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
Verified CPU source windows:

| Original source | SHA-256 | Control/effect |
| --- | --- | --- |
| `$B727-$B739` | `cba0bb3bb196bba95ab64ee80cb78f408f273fa978472b74bd469455422e257c` | Conditionally increment original counter `$0099`, except player `$054E,0=$02` and partner `$054E,$9B=$08` |
| `$B2B5-$B316` | `8c04be37a562747e49c4edd5feeed46858ad803a80cdde0804744b62fe5fbe33` | First partner-contact state writes and subsequent special-handler dispatch |
| `$B32D-$B338` | `fd2a07970cb44e6ddeb400cb1984159f9b06f90de83ba8306b7fb5ad2e767a6b` | Test original `$0657,X & $0F == $03` and partner type `$02` |

The previously authenticated JP0819 `$B29D-$B31F` loop finds an
occupied partner slot **20, 21, or 22**, skips original
`$068D,X` contact mask `$02/$04/$08` as appropriate, and checks
`$B447`. Only **after original carry-clear proximity** does
`$B2B5 JSR $B727` run. The new pure
`cviii_b727_predict_0820()` requires an explicit confirmed-near
precondition and returns these **predicted original CPU write
postconditions**, without applying them:

- `$0099` increments modulo 256 unless the player/partner type
  pair is `$02/$08`.
- `$068D,X` ORs the original partner mask bit.
- `$0606,partner & $F0` plus `$0669,X` uses actual
  byte `ADC` carry; on carry, the original code instead uses
  `$0669,X | $F0`. Its resulting high nibble is combined with
  `$0606,partner & $0F` in `$0669,X`.
- `$061D,partner` receives `$0657,X`.
- `$B32D` checks original source low-nibble 3 and partner type2;
  only in that case `$0669,partner |= $03` and
  `$0669,X = ($0669,X & $F0) | $03`.
- Partner type `$06` goes to **`$B30B JSR $B6CE`**;
  all other types go to **`$B311 JSR $B5DF`**,
  followed by the unresolved `$B486`.
  The pure function **stops before** all those helpers.

This source reconstruction clarifies the original contact masks and
event-counter/partner writes. It is not yet an independently
authorized native offscreen hitbox, collision, drop, pickup, damage
event or original CPU side-effect implementation. The original
NESRecomp game remains authoritative for guest RAM and interaction.

The existing private-ROM auditor
`JP/decomp/tools/jp_stage1_interaction_lifetime_0819.py`
was extended to authenticate all three source windows and the
critical `$B727` / `$B2B5` / `$B32D` opcode sequences.

## Natural evidence: what is actually proved

There **is** independent **natural controller-reached Mesen 2.1.1**
evidence: [JP0509](0509_MESEN_ACTOR_LIVE_FINDINGS.md) replayed
the unmodified original Japanese cartridge from cold boot to
**Stage 1-02 frame 3092**, original raw0A `$84F3`
scheduler with source `X=$03`, row `$32`, and entered the
actual `$8B2C` handler. An authenticated **600-instruction
source trace** produced original actor slots **1 and 2**
with `$054E,X=$3D`, and source event indices progressed
to `$07CB=$11` and `$07CC=$21`.
The bounded original source writer `$8B50` stores the source
index `$69` into child `$0645,X` and ORs bit `$04`
into child `$0470,X`. The natural report proves
**creation**, but does **not** separately record a
new `$0645` source-parent poststate, original `$B727`
execution, or the later natural **deallocation frame**.
No fresh Mesen runtime exists in this execution environment.
Accordingly, **no new original natural lifetime replay or
fully working extended-viewport collision is claimed**.

## Source-slot reuse and offscreen lifetime consistency

Original six-slot row sources `$07C2,X` may clear
while the associated allocated actor `$054E,Y=$3D`
persists. Once the source slot is later reused, numerically
equal `$0645,Y` is **not proof the child came from the
new row**. The resident-world JP0820 observer now retains
a 12-bit actor-slot ambiguity marker:
- If original allocated child remains but parent source row
  ceases to equal `$32`, mark child parent source
  association unresolved.
- If the source slot later returns to row `$32`
  while that actor remains allocated, keep the unresolved marker
  and record a source-reuse warning.
- Clear on original `$054E,Y=0` actual slot disappearance,
  room discontinuity, or reset. Unknown offscreen lifetime is
  not a verified despawn.
- This affects **only native metadata**. Original CPU
  scheduler, actor lifetime, OAM, collision and weapons are
  untouched. Slot reuse between observed frames cannot be
  resolved without an original execution/writer trace.

The native world regression exercises a current child,
hidden-but-allocated child, parent source row clearing,
new row-`$32` occupancy and actual actor slot removal.
No virtual actor is spawned or kept alive.

## Tests and proof boundary

- Strict C11 and ASan/UBSan original-contact prefix fixture
  passes locally with artificial original RAM.
- JP0820 standalone native CTest
  `jp_b727_contact_test_0820` covers special
  `$02/$08` counter suppression, `$0099` wrap,
  three contact bits, normal and overflow ADC,
  special `$B32D` partner state, dispatch to
  `$B30B/$B311`, no guest RAM mutation and no
  unconfirmed contact.
- Windows CI explicitly executes the JP0820 CTest
  and existing full JP0803 persistent-world test.
  Run results must be read for the **current commit**;
  this note does not claim future builds in advance.

### Remaining original CPU and natural acceptance
To enable actual gameplay interactions beyond the 256-pixel
guest camera requires original trace-level proof of:
`$B447` proximity and `$B727` side-effect poststates
during controller-reached gameplay;
`$B6CE/$B5DF/$B486` effect semantics;
real `$8B50` source-to-child identity and later
`$054E,Y=0` removal across scrolling, including
CPU/PPU/OAM, audio and pickup parity.
No PRG-byte or VPP certification change:
**49,504/262,144 strictly certified PRG bytes, 31/100 VPP**.
