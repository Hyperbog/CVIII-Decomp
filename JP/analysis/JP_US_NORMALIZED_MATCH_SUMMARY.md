# JP ↔ US relocation-normalized structural baseline

Acceleration-only classification. This does **not** promote semantic verification.

- 16-instruction unique normalized signature matches: **24,014**
- JP bytes covered by normalized candidates: **68,009 / 262,144 = 25.94%**
- JP bytes covered by exact-or-normalized correspondence: **149,607 / 262,144 = 57.07%**
- Calibration against exact baseline: **13,232/13,232** normalized starts agree on the US offset; **0** disagree.

Normalization preserves opcode bytes, immediates, RAM/I/O operands; it zeros branch displacements, JSR/JMP absolute targets, and ROM absolute operands >= `$8000`. This makes relocation-equivalent instruction sequences match while retaining most game-state constants and RAM structure.

## Per-bank exact-or-normalized structural coverage

| JP PRG | structural candidate bytes | coverage |
|---:|---:|---:|
| PRG00 | 3,618 | 44.17% |
| PRG01 | 6,300 | 76.90% |
| PRG02 | 5,193 | 63.39% |
| PRG03 | 5,198 | 63.45% |
| PRG04 | 6,369 | 77.75% |
| PRG05 | 5,492 | 67.04% |
| PRG06 | 5,275 | 64.39% |
| PRG07 | 5,942 | 72.53% |
| PRG08 | 313 | 3.82% |
| PRG09 | 686 | 8.37% |
| PRG10 | 254 | 3.10% |
| PRG11 | 722 | 8.81% |
| PRG12 | 8,033 | 98.06% |
| PRG13 | 8,013 | 97.81% |
| PRG14 | 6,823 | 83.29% |
| PRG15 | 7,306 | 89.18% |
| PRG16 | 8,180 | 99.85% |
| PRG17 | 7,677 | 93.71% |
| PRG18 | 5,626 | 68.68% |
| PRG19 | 4,189 | 51.14% |
| PRG20 | 4,389 | 53.58% |
| PRG21 | 2,582 | 31.52% |
| PRG22 | 5,571 | 68.01% |
| PRG23 | 4,365 | 53.28% |
| PRG24 | 397 | 4.85% |
| PRG25 | 4,165 | 50.84% |
| PRG26 | 5,882 | 71.80% |
| PRG27 | 5,661 | 69.10% |
| PRG28 | 4,900 | 59.81% |
| PRG29 | 6,545 | 79.90% |
| PRG30 | 921 | 11.24% |
| PRG31 | 3,020 | 36.87% |

Use `tools/match_jp_us_normalized.py` to regenerate and `tools/audit_jp_us_normalized_match.py` to lock the baseline. Candidate correspondence still requires JP control-flow/mapper/producer evidence before becoming verified decompilation.
