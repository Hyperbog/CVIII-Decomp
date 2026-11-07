# CVIII Japanese native release entry points

The single public direction is **Enhanced Edition**, with Japanese VRC6
original gameplay as the reference. These are *source/build tools*, not
redistributable commercial game executables.

| Path | Purpose | State |
| --- | --- | --- |
| [alpha/](alpha/) | Existing supported Windows ROM-free build/launch kit and private `AlphaCandidate` | Owner-tested baseline; active |
| [product/](product/) | Non-destructive candidate staging, integrity checks and private final-release QA instructions | Implemented scaffolding; QA pending |

**Build from original ROM:** use `alpha/Build-And-Play.bat -Rebuild`
after synchronizing `decompilation`. Do not relocate or rename
`alpha/` or its scripts: the private builder, CI and existing users still
depend on those paths.

**Prepare a release candidate:** see [product/README.md](product/README.md).
Only the owner's private Windows build can produce the compiled game. No
ROM, ROM-derived EXE or save states are committed or uploaded to CI.

**Source ownership:** gameplay and host belong under `../native/`;
helper scripts under `../tools/`; permanent original-6502 evidence under
`../../decomp/`. Do not merge research branches merely to populate a
release directory.
