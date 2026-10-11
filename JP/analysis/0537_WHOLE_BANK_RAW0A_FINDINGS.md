# Bank-scale recovery: Japanese PRG raw bank `$0A` (16 KiB)

## Scope and honest status

Target: original Japanese *Akumajō Densetsu* iNES, VRC6 mapper 24. The unit of
work is the entire physical 16-KiB PRG bank `$0A`, CPU `$8000-$BFFF`, physical
PRG `$028000-$02BFFF`. Work is **not complete semantic decompilation** and is
**not a native recompilation**. This bank remains the active bank-wide work unit;
no 100-byte progress checkpoint is being declared a completed milestone.

Original ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Physical raw bank `$0A` SHA-256:
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.

## Whole-bank coverage (16,384 physical bytes, mutually exclusive)

| Classification | Bytes | Evidence quality |
| --- | ---: | --- |
| Existing 0536 audited 6502 instruction/operand source | 2,162 | Previously authenticated graph, not new strict credit |
| Existing audited dispatch and room table source | 168 | Previously source-lifted |
| Additional 6502-looking static CFG candidates | 2,910 | **Not certified**: opcode-pattern/possible-entry evidence only |
| Pointer arrays (15 + 224 + 244 original words) | 966 | Full in-bank pointer/root structural checks; caller runtime liveness unknown |
| Pointer-rooted fixed-width game data | 2,057 | 217 × 5-byte records + 243 × 4-byte records; all starts exactly enumerated |
| **Unresolved original bytes** | **8,121** | No validated code/data semantics or alignment |
| **Entire bank accounted for** | **16,384** | Independent mnemonic and byte-source rebuild equals original |

The static candidate set contains 82 nonconflicting discovered roots, with
in-bank boundaries checked against earlier audited code and table bytes.
Those roots are **not** assumed executed and must not be entered into the
historical strict-certified PRG ledger or native gameplay parity tally.

Bank0A memory layout: executable neighborhoods `$8001-$91FF` and
`$B000-$B8FF` are the candidate CFG search windows, not blanket assertions
that those windows consist only of instructions. Data structures are observed
throughout `$9200-$AFFF` and `$B900-$BFFF`. Additional data and executable
islands can still be found inside these broad areas.

### Data layout recovered from original source references

- `$92AE-$92CB`: 15-word pointer array; its first pointer is `$92CC`.
  Variable-length target records are **not** decoded as fixed records.
- `$9F6E-$A12D`: 224 indexed pointers (including repeats), covering exactly
  217 unique 5-byte records in `$A12E-$A56A`.
- `$A56B-$A752`: 244 pointers (including repeats), covering exactly 243 unique
  4-byte records in `$A753-$AB1E`.

The static pointer sources are visible at candidate instruction sites
`$8022`, `$8117`, and `$8197`; the producer *format* is verified, but actual
indices, mapper register history, and reachable gameplay states are not.

## Reproduction

```bash
python3 JP/tools/build_whole_cart_recomp_0529.py \
  --rom "$ORIGINAL_JP_ROM" --out /tmp/jp0536_25banks
python3 JP/tools/recover_raw0a_bank_0537.py \
  --rom "$ORIGINAL_JP_ROM" \
  --baseline /tmp/jp0536_25banks/prg_raw0a.asm \
  --out /tmp/jp_full_raw0a
python3 JP/tools/test_fullbank_raw0a_0537.py --smoke
python3 JP/tools/test_fullbank_raw0a_0537.py --rom "$ORIGINAL_JP_ROM"
```

Generated **full-bank** outputs:
`raw0a_fullbank_0537.asm` and `raw0a_fullbank_0537_atlas.json`.
The latter contains an address-complete partition and 512-byte classification
census so that every unresolved span is tracked rather than hidden.

Local checks: all 16,384 source bytes reassemble to exact physical bank SHA;
substituting the new `raw0a` into the other 24 generated source files
reassembles the **exact complete 393,232-byte original Japanese iNES**.
The ROM-backed test also runs five corruption negatives (three pointer changes,
source `.word` modification, altered original ROM identity).

## Full-bank completion criteria — do not lower the bar

1. Find and classify all unresolved bank0A instructions versus data.
2. Verify all 2,910 candidate opcode/operand bytes by grounded incoming
   execution roots / bank-qualified mapper traces; reject false positives.
3. Recover original table selector bounds, variable-length stream formats,
   memory and actor/room ABI dependencies, and inter-bank call edges.
4. Derive native room-loading/stream behavior from this source and compare
   reset/NMI/gameplay state transitions with the original NES trace.
5. Require source identity and independent assembly tests to remain green.

**No claim:** full Japanese game decompilation, complete raw bank0A semantics,
original-Mesen frame parity, native playable recompilation, or any newly
strict-certified PRG bytes. Historic strict PRG **49,504 / 262,144** and VPP
**27/100** remain unchanged.
