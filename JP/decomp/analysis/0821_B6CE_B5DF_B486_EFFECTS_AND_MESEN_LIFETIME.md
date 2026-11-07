# JP0821 — Authentic $B6CE/$B5DF/$B486 contact effects and natural Mesen lifetime boundary

**Branch:** `jp0813-level1-source-world-lifetime`, draft PR #16 stacked on PR #13's functioning owner-tested NESRecomp Enhanced baseline. The historical 256×240 guest viewport and game CPU simulation remain authoritative, even when PR #13's host draws authentic original actors in wider margins.

## 1. Authenticated physical original Japanese code

Owner-supplied Japanese mapper24 Konami VRC6 cartridge SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, 393232 bytes.

Physical raw PRG bank0B SHA-256:
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.

| CPU source span | SHA-256 | Authenticated effect |
| --- | --- | --- |
| `$B6CE-$B706` | `4923f2a5a6945b606c806e8cc720a5a38403c5e19a7b5caee65de19088e0c9e2` | Type-based actor flag update; type `$49` sweeps slots1–8 |
| `$B5DF-$B628` | `2639dc4d86d077f566c9c1a77da7eb351aed7109f4855744e9bce21d703758d7` | Allocates a **visual effect in slot23** only when its frame `$0400,23` is zero |
| `$B486-$B4D4` | `8f303c18bf0e9ce793d147cbcfaed74b9f65bb2f76d06f5282e0a1388a16df67` | Branches by actor type and `$0669` reaction nibble, may subtract `$067B` vitality before external effects |

The source-window SHA and critical instruction sequences are independently checked by `JP/decomp/tools/jp_stage1_contact_effects_0821.py` using **only the owner's private ROM**. No ROM data, sprites, licensed sound or raw savestates are committed.

### `$B6CE` actor-attribute reaction

For ordinary type `$30..$57` other than `$49`, if `$0470,X & 2=0` the original code ORs bit2 into `$0470,X` and clears upper two bits in `$0565,X` via `AND #$3F`. Type `$49` instead loops actual actor slots **1 through 8** and performs the `$B6E4` update on every slot not already marked bit2. No broad `$054E` type filter is applied inside that loop. Type `<$30` or `>=$58` and already bit2-marked ordinary types return without those writes. The new helper predicts these states without applying them.

### `$B5DF` special visual-effect installation

Original routine first checks **`$0400+$17`**, not `$054E+$17`. If slot23's frame is zero, it copies original current actor X position `$0438,X` and partner Y position `$041C,$9B`, sets:
- `$0470,23=$20`
- `$0400,23=$12`
- `$048C,23=$0E`
- `$0438,23` and `$041C,23` to those original source positions
- `$89=$08`, and restores X from `$69`.

**It does not assign `$054E,23` in this routine.** The authentic JP0803/0807 native host therefore observes the original visual frame/selector signature and records its lifetime independently from the actor type allocator. That is a real Enhanced runtime observation of the existing original game, **not** a synthetic effect spawned in widened margins. The source-address values are internal provenance, not published mod-resource IDs.

### `$B486` reaction gate

Type `<$30` immediately returns, and type `>=$58` diverts to the older `$B47B` branch. For type `$30..$57`, a zero high nibble of `$0669,X` returns. A nonzero high nibble produces a proposed low-nibble-only `$0669,X`; if original `$0470,X & 2`, processing branches to **`$B4D7 JSR $E75A`**. Otherwise it subtracts the original high nibble from `$067B,X` as an 8-bit SBC; when zero or negative it branches to **`$B525`**. A positive remainder reaches sound/event code beginning at `$B4BC JSR $E249`. The native function stops there.

Original `$E75A/$E249/$B5C4/$8282/$B525/$A32F` sound, destruction, item/drop and tile conversion side effects **are not implemented as a parallel native collision engine**. Those effects continue to be performed only by the original NESRecomp guest.

## 2. Real controller-reached Mesen evidence vs missing proof

The prior independently reproduced [JP0509](0509_MESEN_ACTOR_LIVE_FINDINGS.md) natural Mesen2 2.1.1 trace is strong but bounded:
- Original unmodified ROM and controller input only, no RAM/PC/bank injection.
- Frame **3092**, original raw0A `$84F3` selects source row `$32`, original event source slot X=3.
- The live 600-instruction trace enters `$8B2C` twice and produces actual original type `$3D` actor slots **1 and 2**.
- That replay does **not** report a later original `$054E` free-slot writer, natural `$B727` hit, or `$B6CE/$B5DF/$B486` natural effect poststates.

The authenticated Mesen agent and MesenCore.so from that report were **not available in the current local runtime**; public GitHub access is unavailable from this container. An actual new natural-game trace therefore **could not be run**. The optional owner-only `jp_stage1_natural_contact_lifetime_0821.py` reuses the exact legacy controller-only bootstrap and 600-instruction source trace. It follows a bounded number of additional original game frames and independently tries a mapped-raw0B `$B727` execute breakpoint. The output is a local **time series of original snapshot observations**, with honest interval boundaries for original type or source-parent changes. An absent event remains unverified. A bank-qualified B727 hit would prove that entry was reached, **not** all downstream effects. The private states and trace never enter the repository.

```sh
# ROM-free tests
python3 JP/decomp/tools/jp_stage1_contact_effects_0821.py --smoke
python3 JP/decomp/tools/jp_stage1_natural_contact_lifetime_0821.py --smoke

# Owner-private original media and Mesen-agent2.1.1/core:
python3 JP/decomp/tools/jp_stage1_contact_effects_0821.py \
    --rom "/private/Akumajou Densetsu (Japan).nes"
python3 JP/decomp/tools/jp_stage1_natural_contact_lifetime_0821.py \
    --mesen "/private/mesen-agent" \
    --rom "/private/Akumajou Densetsu (Japan).nes" \
    --follow-frames 360 --sample-frames 30 > /private/jp0821-natural.json

# Owner native ROM-free build/test:
cmake --build <owner-native-build> --target \
    jp_contact_effects_test_0821 jp_level1_world_test_0803
ctest --test-dir <owner-native-build> --output-on-failure -R JP0821_
```

## 3. Observability and evidence grade

JP0821 native `cviii_contact_effects_0821.h` is **pure, fail-closed** and ROM-free: it predicts original $B6CE actor flags/state, the original $B5DF slot23 visual installation, and the first $B486 vitality/sound/cleanup boundary. The live world tests now separately observe original `$0400,23=$12`, `$048C,23=$0E`, `$0470,23=$20` without requiring `$054E,23` to be nonzero. **Even matching this RAM signature is not proof that the original PC executed `$B5DF` in that exact frame.**

Source-parent lifetime attribution remains guarded against six-slot scheduler recycling (JP0820). Neither marker is permission to resurrect original actors beyond their native simulation range.

The native Windows workflow explicitly executes the JP0821 CTest target and the full resident-world regression. The JP Native Regression Gate validates the Python ROM-free audit; CI status is assessed separately for the latest branch head.

**Acceptance still open:** actual independently reached Mesen `$B727` and `$B486` response frames, natural created-child `$054E` deallocation PC/cycle, downstream original E7xx/B5xx changes, original vs widescreen extended-interaction parity. No claim of fully working native offscreen enemies or drops. Strict historical accounting **49,504/262,144 PRG bytes**, **31/100 VPP**, unchanged.
