# 0505 — fixed tile probe lift and whole-ROM caller/script-seed shortlist

ROM SHA-256: 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28. The source of truth is this Japanese ROM, not the US assembly or a general-purpose hardware table.

## Two different index producers, different bounds

Previously verified fixed PRG31 includes:

- **$FD0A-$FD10**: Y is the 8-bit result of RAM[$54] + the low-coordinate carry.
- **$FC76-$FC7A → $FD0E**: Y is the 8-bit result of RAM[$54] + RAM[$14] + carry. RAM[$14] itself is computed upstream from object coordinates.
- **$FD11-$FD18**: A = ($13 >> 5) OR cpu_read($FD62 + Y).
- **$FD1B-$FD24**: repeated CMP #$0C / SBC #$0C reduces A modulo 12.
- **$FD25-$FD2B**: read cpu_read($FD4D + reduced A), CLC, ADC $11 and TAY.

The **12-byte $FD4D-$FD58 table** is genuinely index-bounded and was already counted in 0504. The **$FD62,Y read has no proven live Y domain**. Until its RAM[$54]/RAM[$14] producer bounds are established, conservative addresses are $FD62-$FE61 (256 indices); this includes bytes also classified as executable code. It would be wrong to clamp Y to 12 or 16 or invent a fixed FD62 table length. No new data bytes are promoted.

The native partial lift \`src/fixed_tile_probe.hpp\` takes the low byte, high-index byte, fine offset, and a **mapped CPU-bus reader**, reproducing the OR/modulo/table/ADC arithmetic without a fabricated index limit. It does not execute the full fixed collision routine or prove rendering parity. \`tests/fixed_tile_probe_test.cpp\` uses authoritative JP fixed-bank bytes to verify **524,288 input combinations** (8 low-index classes × 256 high-index bytes × 256 fine offsets), including Y=$FF which reads $FE61. Tests are algorithm-level regression, not a reference-emulator trace.

Run:
\`\`\`sh
g++ -std=c++17 -Wall -Wextra -Werror -pedantic JP/decomp/tests/fixed_tile_probe_test.cpp -o /tmp/fixed_tile_test
/tmp/fixed_tile_test "/path/to/Akumajou Densetsu (Japan).nes"
python3 JP/decomp/tools/audit_fixed_tile_probe_0505.py "/path/to/Akumajou Densetsu (Japan).nes" optional_report.json
\`\`\`

## Whole-ROM candidate shortlists

The independent ROM-locked audit scans all 16 raw VRC6 banks and outputs reproducible **raw byte-pattern** locations:

| Fixed target | JSR-pattern matches |
|---|---:|
| $FB96 | 11 |
| $FBA5 | 4 |
| $FC17 | 6 |
| $FC1F | 43 |
| $FCDE | 92 |
| **Total** | **156** |

A second pattern \`LDA #imm ; STA $05EF,X\` finds **37 candidate immediate script-ID initializations** in raw banks $02, $03, $09, $0A, $0B and $0C. This includes the already verified $B503 ID $1B producer. The other patterns remain candidates because a raw opcode sequence can occur inside data; runtime mapper bank, valid instruction start and object-index liveness are not established by a string match.

In particular, six raw-bank candidate calls point to the eight-byte fixed **$FC17-$FC1E alternate entry** (STY $10, TAY, LDA $10, JMP $FCEE). The ROM bytes are known, but no live mapper-backed caller has been proved, so those eight bytes are **not newly credited**.

## Historical data accounting and recovery

Checkpoint 0505 contributes **zero additional semantically verified PRG bytes**. Previously tracked floor stays **49,399 / 262,144 = 18.8442%** and VPP stays **24/100**. This is a native/tooling/provenance-index checkpoint, not a falsely padded byte-coverage checkpoint.

The raw fixed investigation frontier remains PRG31:$FB96. The pending $FB96-$FBF5, $FC17-$FC1E and $FD59-$FDE3 gaps remain explicitly unclaimed. The mapped-read abstraction and opcode/flag behavior are consistent with the MOS MCS6500 instruction manual and the NES 2A03 CPU distinction (no BCD arithmetic). Hardware references are secondary authority only.

Next: establish concrete JP callers into $FB96/$FC17 from verified bank contexts, trace $54/$14 assignments to close the FD62,Y index domain, and expand confirmed $05EF script-ID producers into live action handler graphs.
