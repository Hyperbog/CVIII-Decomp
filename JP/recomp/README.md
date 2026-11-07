# Recomp — functioning native Japanese Castlevania III

This is the **active owner-tested C11/SDL2 NESRecomp product** for Japanese *Akumajou Densetsu*, with optional Enhanced Edition presentation and interface features. It is not the partial semantic decompilation.

| Directory | Contents |
| --- | --- |
| [native/nesrecomp_cycle/](native/nesrecomp_cycle/) | External NESRecomp CMake integration, Mapper24 and VRC6 host |
| [native/enhanced/](native/enhanced/) | Native Enhanced host modules and optional presentation/research helpers |
| [tools/](tools/) | Original-ROM authenticated native builder, SDL overlays, assets and packaging |
| [release/alpha/](release/alpha/) | ROM-free Windows builder, launcher, save-state and controls tools |
| [release/product/](release/product/) | Private product-candidate staging contract and owner controller/DMA QA instructions |
| [scenarios/](scenarios/) | Native/reference input replay scenarios |
| [docs/](docs/) | Current release milestones, product features and QA |
| [workstreams/native-recompilation/](workstreams/native-recompilation/) | Product-owned feature status and evidence |

To build/play on Windows, begin with [release/alpha/README_ALPHA.md](release/alpha/README_ALPHA.md); the [release index](release/README.md) also explains the non-destructive private product-candidate layout and privately supply the original authenticated Japanese cartridge. Current owner-tested features, limitations and acceptance items are in [docs/ENHANCED_CURRENT_STATUS.md](docs/ENHANCED_CURRENT_STATUS.md).

The upstream NESRecomp dependency stays external and is not copied into this repository. Do not commit retail ROMs, generated proprietary C source, save states or owner-local controls.

**Independent original-source recovery is under [../decomp/](../decomp/).** Its VPP and strict PRG scores are not percentages of playable game completion. A helper compiled into the build does not become an active gameplay feature without host integration and appropriate acceptance tests.

## Stage 1 source-backed presentation (JP0832)

The original Japanese Stage 1 world/actor-source presenter is now **compiled into the native NESRecomp game**, but remains **disabled by default**. To enable the presentation-only module for an owner-local build, pass `--edition enhanced --stage1-world 1 --stage1-world-rom "<path-to-original-JP-ROM>"` to the native executable. `--stage1-resource-cache "<private-cache-path>"` is optional. The chosen original cartridge must pass runtime SHA authentication; failures retain the unmodified stock picture. `Stage1World = 0/1` persists the enable choice, but never writes a private ROM path to config.

This layer observes the original RAM, PPU nametables/scroll, and authenticated raw0A/0B source+actor bytes. It only paints additional widescreen pixels and models bounded actor-source lifetimes in **private** state. No guest CPU/PPU writes, new enemy damage, loot, sound, or unconditional offscreen AI activation are authorized. The older `--room-preview` comparison remains available when Stage 1 world mode is disabled. ROM-free synthetic presenter tests and compiled host-option tests cover the boundary; full original-game scene parity and interactive wide-world actors remain unverified.
