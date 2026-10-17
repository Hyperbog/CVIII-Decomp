# JP 0573 — original Japanese ROM C11 selector compiled and run

The user-uploaded original Japanese cartridge was authenticated in the
local development runtime: 393,232 bytes, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`,
iNES mapper24 (VRC6a) and CRC32 `2e93ce72`.

A local, stand-alone C11 code generator was compiled with `cc -std=c11
-O2 -Wall -Wextra -Werror -pedantic` using ORIGINAL opcode bytes of
the source-audited raw0A routine $801E–$8046. It generated 24 native
C instruction starts and successfully compared 135/135 original
stage/middle/leaf pointer cases against both source tables and a
separate original 6502 opcode interpreter. **This is one original
game routine, not a playable native Castlevania III executable**.
The private C source, cartridge bank and executable were built outside
GitHub, with no original ROM or generated game-code payload checked in.

`tools/build_original_c11_0573.py` makes the established 0562/0563
pipeline persistent and reproducible, using all 2,357 existing
raw0A statically translated instruction sites rather than the
stand-alone 24-site development subset:

```sh
python3 JP/decomp/tools/build_original_c11_0573.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --out "/tmp/jp0573-compiled"
```

This regenerates the original source, verifies whole-ROM and
bank-specific identities and byte-exact source reassembly,
emits the local C11 bank0A translation, compiles the
`raw0a_driver_0563.c` native test executable, executes 135
producer-bounded cases and checks against an independent 6502
interpreter. Output includes a private C file, executable and
`jp0573_build_report.json`. CI only executes `--smoke` on
synthetic generated C because copyrighted input is not placed
in the public repository.

**Full game build blocker:** a complete NESRecomp C11 cycle backend
cannot be downloaded/compiled in this isolated local environment.
The separately licensed upstream engine *was* built in GitHub CI
using synthetic mapper24 media (0571: 86,951/86,958 native CPU cycles,
zero interpreter fallbacks), but that is not original-ROM gameplay.
Local full-game build command remains
`tools/nesrecomp_cycle_0568.py --rom ... --engine ... --out ...`
with an externally available pinned engine checkout. Neither full
120/600 original-ROM frames nor original-game picture/audio parity
have been tested.

VPP27/100, strict49,504/262,144, previously compiled sites4,261
remain unchanged. This commit adds a reproducible *build gate*,
not new original-game code coverage.
