# 0525 — PRG interval recovery and literal recompilation scaffold

The project had a numeric 49,504-byte strict PRG certificate without a complete
machine-readable physical mask for its pre-0500 ancestry. This checkpoint
does not reinterpret it as 49,504 rebuilt/recompiled bytes and does not
promote unverifiable new bytes.

## Recoverable certified intervals

| Checkpoint | Original physical PRG bytes | Region count |
|---|---:|---:|
| 0500 corrected historic graph | 982 | 6 |
| 0501 fixed + raw 09/0A/0B | 4,364 | 31 |
| 0502 raw0B B394-B395 table | 2 | 1 |
| 0504 raw0B + fixed graph/data | 576 | 16 |
| 0507 raw0A B4CC-B4D0 | 5 | 1 |
| 0508 original Mesen code fragments | 100 | 4 |
| **Disjoint interval union** | **6,029** | **59** |

Exact 0500 physical intervals and per-interval SHA-256 fingerprints were
recovered from historical Git commit
`75545a83604f512695f88c4479d38271baec678e`. The other 53 intervals
come from the repository's 0501 manifest, 0502 original source proof,
0504 audit's 16 regions, 0507 original ROM source, and 0508 RESUME_STATE
certificate. These 59 regions are mutually disjoint.

**43,475 earlier bytes remain an opaque historical certificate**, not a
reconstructed occupancy bitmap. 6,029 + 43,475 = 49,504; this arithmetic
does not prove source-to-source disjointness for later regions outside the
recoverable incremental map.

## Corrected 0510–0517 source accounting

The 0518 inventory contains 25 independent physical windows totaling 1,365
unique bytes. Against the **full recovered 0500–0508 incremental union**:

- Already in 0501: 546 bytes
- Already in 0502: **2 bytes**
- Already in 0508: 78 bytes
- Other known incremental intervals: 0 bytes
- **739 bytes** outside the recoverable incremental union

The old partial audit counted 741 outside only 0501 and 0508. That
overstated the unresolved pool by two previously certified 0502 table bytes.

**None of 739 can be promoted until the physical byte mask of the missing
43,475-byte pre-0500 baseline is reconstructed and the original source
instruction/data dependency rules are satisfied.**

## Recompilation output, explicitly scoped

`tools/audit_prg_recomp_0525.py` verifies every known certificate and all
25 0518 source windows against the exact original Japanese ROM when supplied.
It can emit **59 original-source `.asm` literal fragments**, one for each
certified interval, and independently roundtrip the emitted `.byte` stream.
These are byte-exact **recompilation scaffolds**, NOT automatically recovered
6502 instructions or proof of native gameplay equivalence. ROM-derived output
is generated locally and is not committed.

```sh
python3 JP/decomp/tools/audit_prg_recomp_0525.py
python3 JP/decomp/tools/audit_prg_recomp_0525.py --rom "$ORIGINAL_JP_ROM" \
  --report /tmp/0525_prg_union.json \
  --emit-literal-fragments /tmp/0525_prg_fragments
```

Strict PRG remains 49,504/262,144, VPP 27/100, certified semantic 0508,
fixed physical investigation frontier FB96. **Next**: recover the oldest
pre-0500 physical certificate from git history and use the unified bitmap to
classify/promote genuinely novel executable or bounded data ranges.