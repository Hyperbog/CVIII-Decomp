# Recomp — functioning native Japanese Castlevania III

This is the **active owner-tested C11/SDL2 NESRecomp product** for Japanese *Akumajou Densetsu*, with optional Enhanced Edition presentation and interface features. It is not the partial semantic decompilation.

| Directory | Contents |
| --- | --- |
| [native/nesrecomp_cycle/](native/nesrecomp_cycle/) | External NESRecomp CMake integration, Mapper24 and VRC6 host |
| [native/enhanced/](native/enhanced/) | Native Enhanced host modules and optional presentation/research helpers |
| [tools/](tools/) | Original-ROM authenticated native builder, SDL overlays, assets and packaging |
| [release/alpha/](release/alpha/) | ROM-free Windows builder, launcher, save-state and controls tools |
| [scenarios/](scenarios/) | Native/reference input replay scenarios |
| [docs/](docs/) | Current release milestones, product features and QA |
| [workstreams/native-recompilation/](workstreams/native-recompilation/) | Product-owned feature status and evidence |

To build/play on Windows, begin with [release/alpha/README_ALPHA.md](release/alpha/README_ALPHA.md) and privately supply the original authenticated Japanese cartridge. Current owner-tested features, limitations and acceptance items are in [docs/ENHANCED_CURRENT_STATUS.md](docs/ENHANCED_CURRENT_STATUS.md).

The upstream NESRecomp dependency stays external and is not copied into this repository. Do not commit retail ROMs, generated proprietary C source, save states or owner-local controls.

**Independent original-source recovery is under [../decomp/](../decomp/).** Its VPP and strict PRG scores are not percentages of playable game completion. A helper compiled into the build does not become an active gameplay feature without host integration and appropriate acceptance tests.
