# JP ↔ US exact PRG correspondence baseline

This is an acceleration artifact, not a semantic-verification claim.

- JP ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- US ROM SHA-256: `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`
- Method: exact 32-byte anchors that occur exactly once in the US PRG; overlapping bytes with conflicting anchor mappings are excluded.
- Unique exact JP bytes: **115,865 / 262,144 = 44.1990%**
- Exact correspondence runs: **821**
- Ambiguous JP bytes excluded: **73**

Exact correspondence means the bytes are identical; it does not establish identical runtime mapper state, ownership, reachability, or semantics. JP ROM evidence remains authoritative.

## Per-bank correspondence

| JP PRG | exact bytes | coverage | largest US destinations |
|---:|---:|---:|---|
| PRG00 | 3,217 | 39.27% | PRG00: 3100, PRG01: 117 |
| PRG01 | 4,389 | 53.58% | PRG01: 3454, PRG11: 904, PRG09: 31 |
| PRG02 | 3,039 | 37.10% | PRG02: 3038, PRG09: 1 |
| PRG03 | 2,981 | 36.39% | PRG03: 2190, PRG09: 791 |
| PRG04 | 3,605 | 44.01% | PRG04: 3605 |
| PRG05 | 3,471 | 42.37% | PRG05: 3431, PRG09: 40 |
| PRG06 | 2,357 | 28.77% | PRG06: 1157, PRG19: 1097, PRG11: 72, PRG29: 31 |
| PRG07 | 5,942 | 72.53% | PRG07: 5919, PRG30: 23 |
| PRG08 | 313 | 3.82% | PRG08: 313 |
| PRG09 | 686 | 8.37% | PRG09: 686 |
| PRG10 | 254 | 3.10% | PRG10: 254 |
| PRG11 | 660 | 8.06% | PRG11: 660 |
| PRG12 | 8,033 | 98.06% | PRG12: 8033 |
| PRG13 | 7,982 | 97.44% | PRG13: 7965, PRG29: 17 |
| PRG14 | 6,796 | 82.96% | PRG14: 6677, PRG15: 119 |
| PRG15 | 7,306 | 89.18% | PRG15: 7306 |
| PRG16 | 8,180 | 99.85% | PRG16: 8180 |
| PRG17 | 7,622 | 93.04% | PRG17: 7622 |
| PRG18 | 4,023 | 49.11% | PRG18: 3916, PRG19: 107 |
| PRG19 | 2,298 | 28.05% | PRG19: 1530, PRG06: 768 |
| PRG20 | 3,303 | 40.32% | PRG20: 3269, PRG21: 34 |
| PRG21 | 1,894 | 23.12% | PRG21: 1894 |
| PRG22 | 2,549 | 31.12% | PRG22: 2408, PRG09: 141 |
| PRG23 | 3,693 | 45.08% | PRG23: 3638, PRG03: 40, PRG22: 15 |
| PRG24 | 311 | 3.80% | PRG24: 311 |
| PRG25 | 2,950 | 36.01% | PRG25: 2887, PRG24: 63 |
| PRG26 | 5,734 | 70.00% | PRG26: 5734 |
| PRG27 | 5,083 | 62.05% | PRG27: 4715, PRG09: 368 |
| PRG28 | 1,699 | 20.74% | PRG28: 1699 |
| PRG29 | 2,777 | 33.90% | PRG29: 2777 |
| PRG30 | 480 | 5.86% | PRG30: 480 |
| PRG31 | 2,238 | 27.32% | PRG31: 2238 |

## Largest exact runs

| JP PRG offset | US PRG offset | length |
|---:|---:|---:|
| `$0E8E1` | `$0E7E1` | 5,919 |
| `$196AC` | `$196AC` | 5,245 |
| `$20001` | `$20001` | 4,481 |
| `$2132A` | `$2132A` | 3,267 |
| `$21FEE` | `$21FEE` | 3,149 |
| `$1DE04` | `$1DE7B` | 3,082 |
| `$1C001` | `$1C001` | 2,996 |
| `$1B2D8` | `$1B30B` | 2,839 |
| `$18001` | `$18001` | 2,607 |
| `$22C3C` | `$22C3C` | 2,584 |
| `$18A40` | `$18A40` | 2,250 |
| `$1EDE2` | `$1EE59` | 1,622 |
| `$1D1A4` | `$1D21B` | 1,524 |
| `$23655` | `$23655` | 1,316 |
| `$1AB33` | `$1AB33` | 1,304 |
| `$02D7D` | `$02F9A` | 1,100 |
| `$1EA2C` | `$1EAA3` | 942 |

Use `tools/match_jp_us_exact.py` to regenerate the full machine-readable report and `tools/audit_jp_us_exact_match.py` to lock the baseline. The matcher is intentionally conservative and only handles exact unique spans; relocation-normalized routine matching is the next layer.
