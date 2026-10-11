# Whole-bank raw0A recovery: JP Akumajō Densetsu VRC6 (0538)

## Scope and reproducibility

**This is a single 16,384-byte bank workstream, not a completed bank decompilation.**
The original Japanese bank is physical raw VRC6 bank `0A`, PRG byte offset
`0A * 0x4000`, mapped to CPU `$8000-$BFFF`. The source tree represents every
original byte and regenerates the exact bank:

- Original retail JP iNES SHA-256:
  `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- Raw0A physical 16KiB SHA-256:
  `1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`
- Independent assembly: 16,384/16,384 bytes exact.
- The complete cartridge from 17 PRG plus eight CHR `.asm` modules remains
  exactly 393,232 bytes, with original SHA-256 unchanged. The original ROM
  is not stored in the GitHub repository.

To reproduce from a checkout with an original JP ROM:

```bash
python3 JP/tools/build_fullbank_0a_source.py --smoke
python3 JP/tools/test_fullbank_raw0a_0538.py --smoke
python3 JP/tools/build_fullbank_0a_source.py \
  --rom "$ORIGINAL_JP_ROM" --out /tmp/cviii-jp-raw0a
python3 JP/tools/test_fullbank_raw0a_0538.py --rom "$ORIGINAL_JP_ROM"
```

Output under `/tmp/cviii-jp-raw0a/banked/prg_raw0a.asm` is the whole-bank
readable 6502/data source. `fullbank_manifest.json` and
`raw0a_hierarchy_atlas.json` preserve the full byte partition and evidence
quality. `raw0a_bounded_selector_cases.json` contains all 135 locally tested
selector paths.

## Full 16KiB accounting — not interchangeable evidence levels

| Classification | Original bytes | Status |
| --- | ---: | --- |
| Historical authenticated original 6502 instructions | 2,162 | Code source; previously counted |
| Historical authenticated pointer/room data | 168 | Data source; previously counted |
| Additional possible aligned 6502 code from 0537 | 2,910 | **Candidate only, NOT certified**, no proven live entry |
| 0537 bounded pointer arrays and 4-/5-byte records | 3,023 | Structural, not globally live |
| 0538 pointer hierarchy and record data | 4,391 | Structural, not globally live |
| 0538 conditionally indexed room-message tables/data | 46 | Conditional source |
| **Unresolved (still emitted as `.byte`)** | **3,684** | Unknown code/data classification |
| **Bank total** | **16,384** | Byte-exact source |

Thus raw0A currently has 2,330 historically audited bytes of instruction or
local data, 2,910 *unverified* static code candidates, 7,460 structurally
classified game-data bytes, and 3,684 completely unresolved bytes.

These values are **not** additional strict semantic PRG certification. The
historical global strict total remains 49,504/262,144, VPP remains 27/100.
The previous whole-cart 0536 classified-PRG source census remains unchanged
unless it is explicitly reported as a broader *structural/candidate* metric.

## Actual three-stage pointer interpreter: `$801E-$8046`

The original contiguous 6502 routine uses the in-RAM selectors and intermediate
zero-page pointers below:

```
$34 -> 2*x -> word[$92AE+2*x] -> $06/$07
$35 -> 2*y -> word[($06)+2*y] -> $04/$05
$36 -> 2*z -> word[($04)+2*z] -> $95/$96
```

The actual original opcode sequence (not a Python translation of the control
flow) executes in `test_raw0a_lookup_cpu.py` for **all 135 structurally valid
(x,y,z) triples**, with the extracted 16KiB bank mapped at CPU `$8000`.
Each execution verifies the CPU-generated stage, middle, and leaf pointers
against the independently parsed pointer hierarchy.

Authenticated *local* hierarchy layout:

- `$92AE-$92CB`: 15 top-level little-endian pointers.
- `$92CC-$931F` and `$9AF4-$9B1F`: 64 second-level pointer words.
- `$9320-$93CB` and `$9B20-$9B81`: 135 third-level pointer words.
- `$93CC-$9AF3` and `$9B82-$9F6D`: 113 distinct leaf roots, 709 complete
  four-byte payload cells. The actual meaning of individual cell bytes
  is **not yet proven**.
- `$AB1F-$AFA3`: 16 distinct pointer-rooted streams, 163 seven-byte
  records whose first field is consistently `00..03`, followed by one `FF`
  terminal byte per stream. **Seven-byte fields are not assigned unsupported
  gameplay meanings**.

No global proof constrains actual gameplay writes to `$34/$35/$36` to just
those extracted valid indices. The local execution set is intentionally
producer-bounded and does not claim original Mesen frame parity or universal
selector safety.

## Additional original `$B8CC` conditional room-message lookup

The earlier audited branch selects `$B909` or `$B90B`, each containing a
pointer to one of two 5-word arrays at `$B90D-$B920`; those words address
10 messages at `$B921-$B936`. The ten messages terminate in `FF` and occupy
22 bytes; the two pointer levels occupy 24 bytes. The lookup uses RAM `$07A0`
and `$07A5`, whose full live domains are not yet proven.

**Do not** interpret `$B937-$BFFF` as an extension of the message format:
that region remains unresolved.

## Test and failure gates

- Original ROM SHA and raw0A SHA locked.
- Full independent `assemble()` of 16KiB bank and entire 25-bank ROM.
- 135 actual CPU instruction-path tests for three-level indexed lookup.
- Ten negative tests corrupt nested pointers, leaf record type, stream and
  message terminators, source words, and original ROM identity.
- ROM-free smoke in GitHub CI; full ROM-backed checks are local only because
  copyrighted game ROM is never committed.

## What must happen before bank `$0A` is called **finished**

1. Confirm or reject all 2,910 static code candidates using grounded entry
   addresses, bank register history, and execution trace evidence.
2. Decode the remaining 3,684 bytes, especially `$B937-$BFFF` and code gaps.
3. Recover precise 4- and 7-byte field formats and game-state producers.
4. Verify caller mapper state and selector limits on real original gameplay,
   then port the complete room loader to native C++ and verify identical
   object/room behavior, not merely a correct original-ROM assembler.

**No full decompilation, complete bank semantics, native recompilation, or
playable-game parity is claimed here.**
