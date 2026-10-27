# JP0822 — Actual Mesen + NESRecomp available again; natural actor replay

**2026-10-26, independent re-execution in the current task environment.**

## Why direct git clone failed, and a verified bridge

The execution container's network has no GitHub DNS:
`git ls-remote https://github.com/atonamy/mesen-agent.git HEAD`
and `git ls-remote https://github.com/mstan/nesrecomp.git HEAD`
both returned `Could not resolve host: github.com`.
`curl -IL https://github.com/` failed with curl code 6.
This is **not** evidence that the repositories are inaccessible
on GitHub or that authentication is required: GitHub app API
successfully fetched both public repositories and the owner's
Hyperbog/CVIII-Decomp.

ROM-free `.github/workflows/jp_mesen_nesrecomp_bridge.yml`
uses a GitHub-hosted Ubuntu22.04 runner to clone the original
public tools, verify the pinned Mesen release archive SHA256,
and build the NESRecomp recompiler with CMake/Ninja.
The first bridge GitHub Actions run **40421520709 passed**,
including all clone, checksum, C11 compile and artifact steps.
It publishes only an open-source `mesen-agent` CLI +
`MesenCore.so` and compiled Linux NESRecomp binary, no
ROM, game-specific assets, Mesen state or trace.
GitHub Actions artifact **12697764542** was downloaded
via the GitHub connector directly into the task container.

Verified public upstream identities:
- `atonamy/mesen-agent` clone HEAD:
  `dbc2c744ad52e1c89a8570d22d7fa92507ad4816`.
- `mstan/nesrecomp` clone HEAD:
  `b795ada2127fa3a4ad212f5d8dd494db3339032d`.
- Pinned `mesen-agent` v0.1.0 Linux x64 release TAR SHA256:
  `bff3c1d31a4b5ae5322b075330eccb3e78e96050d7a4e593c02804d8f1de7ae2`.
- Executable `mesen-agent` SHA256:
  `95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0`.
- Extracted matching release `MesenCore.so` SHA256:
  `fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1`.
  This differs from the older pinned-core SHA
  `d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040`,
  but **the original Mesen trace was independently reproduced bit-for-bit**;
  the owner-private replay driver now explicitly permits either
  core hash while requiring the exact original trace fingerprint.
- Built Linux NESRecomp executable SHA256:
  `3b0e3df72448abe9c5bea99beca8937c470d14d852047b14800b4c56af8619f5`.

## Confirmed, newly repeated original natural Stage 1 trace

Owner-supplied *unmodified* Japanese Akumajou Densetsu
Mapper24 ROM SHA256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Mesen agent prints emulator version **2.1.1**; its headless
execution successfully ran original game, CPU RAM inspection,
an original instruction breakpoint, savestates and CPU tracing.

The exact previous JP0509 **controller-only** sequence
was re-executed from cold boot, with no CPU PC, RAM, ROM,
mapper or post-load state edits:

| Checkpoint | Natural Mesen observation |
| --- | --- |
| Boot input | Original frame **1503** |
| Stage1 continued input | Original frame **2603** |
| Bank0A `$84F3` source breakpoint | Original frame **3092**, source row `$32` |
| Subsequent original CPU instructions | **600** |
| SHA256 of exact original CPU trace | `dce02d6ce15c65a4b2dbdeea880b3171206514eeb7d35bb9168fcff56db48d93` |
| `$054F/$0550` after those steps | Both `$3D` |
| `$0471/$0472` after those steps | Both `$04` |
| `$0646/$0647` after those steps | **3 and 4** respectively |
| Original six source rows | `00 00 00 32 32 00` |

This **confirms original natural creation and source-parent
postconditions** beyond a type-only witness, using the
original game and exact original 600-instruction trace.

The same unmodified post-creation saved-state was resumed
with controller inputs preserving the **phase489** original
input epoch, sampling original CPU RAM every **30 frames**
from original frame3092 through **3452**.
All 12 samples remained in original selector `00/01/00`:
both slots 1 and 2 retained type `$3D`, original
parent slots 3/4 and visual flag `$44`, with authentic
sprite animation bytes `$94/$92`.
No deallocation occurred in those samples.

A separate natural replay from that same postcreation state
ran **1,200 original frames through frame4292** with
a bank-qualified original raw0B `$B727` execution
breakpoint. It stopped at the *frame limit*, not at the
contact breakpoint. The final original actor type fields
remained `$3D/$3D` with original flags `$44/$44`
and parent sources `3/4`. Because that second replay
does not record every intermediate actor-slot writer,
**do not claim uninterrupted slot identity for all 1,200
frames solely from the endpoints**. These observations
prove that original `$B727` was *not executed during
this specific input horizon*, not that contact is impossible.

No natural original **contact-to-deallocation sequence**
was observed. No game state was patched to force a hit.
The owner's `jp_stage1_natural_contact_lifetime_0821.py`
remains the canonical private agent/core and source
witness; its core allowlist and creation trace fingerprint
are tightened to reflect this independently reproduced
release binary. Controller-only further interaction
testing still needs a different natural trajectory,
and original writer breakpoints if exact slot deallocation
timing is required.

## NESRecomp locally invoked, with deliberate limit

The newly built NESRecomp CLI successfully identifies this
ROM as `CART 24 0`. It was invoked with the *private*
original ROM, without a game TOML:
```sh
NESRecomp "Akumajou Densetsu (Japan).nes" \
  --proposal-out proposed_game.toml --output-prefix jp_rom_probe
```
It reported original original vector PCs:
`NMI=$E057 RESET=$E00B IRQ=$E0F5`,
recognized **16 x 16KiB PRG ROM banks**, and completed
cycle-accurate 6502 C generation, reporting **719
compiled instructions** split over generated
`jp_rom_probe_cyc.c` and a bank file.
It explicitly said **"No --game config; using empty dispatch
tables"**. That is a successful toolchain/bootstrap test,
**not** a whole-game recompilation, not proof of the
already-owner-tested Windows runner, and not an additional
strict decompilation certificate. The generated files
remain private in the task's scratch directory.

## Acceptance boundary

Live original Mesen replay now works in this task container
via reproducible artifact bridge. Native source-to-actor
lineage **is naturally confirmed at creation**,
and 360 frames of further allocation are observed;
however original `$B727` contact, `$B6CE/$B5DF/$B486`
natural invocation and exact type-zero deallocation
are **not** confirmed in the sampled route.
No synthetic enemies, extra-wide interaction hitboxes
or pickup/damage behavior enabled; strict PRG
**49,504/262,144**, VPP **31/100** remain unchanged.
