# 0523 — Original Japanese raw0B $8193 actor-reset branch

## Original source provenance

The original Akumajou Densetsu iNES file has SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (VRC6 mapper 24). With raw bank $0B mapped into $8000-$BFFF, physical PRG offset `0x02C193..0x02C1A8` is the 22-byte `$8193-$81A8` source block; its SHA-256 is `0b9f9559ee19ffcdb30d51a70bb887aa7f5430b648f886eb5a261987e3989ed2`.

At `$826C`, type `$30..$65` with `$041C,X >= $F8` jumps to `$8193`. The original `$8193 LDA $054E,X / CMP #$4D / BEQ $81B2` rejects the type-$4D special branch from this lift. For other types, original `$819A LDA #$00`, four `STA absolute,X` instructions and `$81A8 RTS` clear `$054E,X`, `$0470,X`, `$0400,X`, `$05EF,X`. This overwrites the earlier `$8161` attribute edit. Original `$FE6E INX / CPX #$13` selects the next boundary, `$FDEC` or `$FE75`.

The 0523 wrapper reuses the existing 0522 native source for all other supported paths. Index X must be `$0D..$12`. Type `$4D` with high position is rejected **before mapper/RAM writes**; `$81B2/$B56B` remains unsupported.

## Verification and limits

- Native C++20 `-O2 -DNDEBUG -Wall -Wextra -Werror -pedantic`: **PASS** with assertions enabled explicitly in the test.
- ROM-free exhaustive bounded matrix: **147,456** configurations, **138,240** supported outcomes, **9,216** intentionally rejected `$4D` states, plus 5 index guards. Among successful cases, **18,432** exercise the newly lifted reset branch.
- AddressSanitizer and UndefinedBehaviorSanitizer: **PASS**.
- New original-ROM physical source auditor: **PASS** against the uploaded Japanese ROM.
- New replay comparator: **PASS** on one explicitly synthetic smoke fixture (1,792 nonstack RAM bytes and CPU/mapper output); an intentionally wrong expected flag is rejected. This synthetic fixture is **not original-Mesen evidence**.
- Original independent Mesen CPU/state differential: **NOT RUN**. The SHA-locked private natural actor-15 savestate and Mesen runner are not present. Do **not** enter a 0523 row in `NATIVE_EVIDENCE_LEDGER.json` or claim parity/new strict PRG/VPP credit.

Last certified semantic checkpoint **0508**, strict PRG **49,504/262,144**, VPP **27/100**, fixed physical frontier `$FB96` remain unchanged. Next work: original `$81B2` bank0B helper `$B56B` or lower-index `$8161` paths, preceded by full original-Mesen parity of 0522-0523.
