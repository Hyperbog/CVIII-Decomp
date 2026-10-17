# JP / Recomp — functioning native Japanese Castlevania III

**This directory name is now reserved for the real C11/SDL2
NESRecomp Enhanced game product**, not the historical hand-assembled
6502 fragments. Those four mnemonic modules moved to
[JP/decomp/asm](../decomp/asm/).

The playable owner-tested program is documented and built from the
following currently stable paths:

- [Native NESRecomp/CMake backend](native/nesrecomp_cycle/)
- [Enhanced SDL/host source](native/enhanced/)
- [Windows ROM-free build-and-play distribution](release/alpha/)
- [Product workstream and feature QA](workstreams/native-recompilation/)
- [Current Enhanced product status](docs/ENHANCED_CURRENT_STATUS.md)

**The real game remains where existing builders expect it.** JP0662
clears the obsolete assembly naming collision and archives three
superseded native experiments. A later atomic, test-gated migration
can move production code here; moving 100+ linked native source files
without updating generated SDL overlays and owner tools would break
the current functioning product. Native gameplay does not depend on
completing the [partial semantic source-recovery score](../decomp/).
