# JP0666 — Original CHR glyph evidence and safe replacement boundary

## Current source evidence

The original Japanese iNES cartridge is SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
The observed `$EC47 -> bank00:$966A -> $0300` formatter command
buffer can yield bounded nametable rows of **tile IDs**. The editor
already displays unknown tile codes as raw `<XX>` and recognizes only
the previously source-audited Latin `$C0-$D9` tile sequence as A-Z.
No Japanese Unicode decoding, punctuation semantics or complete font
map is asserted.

`JP/decomp/tools/audit_original_chr_glyphs_0666.py --rom <private ROM>`
inspects all 16 original 8 KiB CHR banks. Its report contains only
counts of unique and blank patterns among tile indices `$C0-$D9`;
the glyph/pixel patterns and original ROM bytes are not exported.
**CHR tiles with the same index differ between banks.** Until the
actual VRC6 CHR bank registers are traced at the source-rendered
PPU frame, a tile ID alone does not prove its visible glyph.
The tool deliberately leaves all Unicode mappings unverified.

## Safe replacement architecture

Source-side readonly capture -> original bank+PC-qualified completed
`$EC47` event -> original `$0300` bounded byte snapshot -> parser
that rejects ambiguous control bytes and non-nametable/attribute
writes -> original source SHA-256 -> editor-authored text -> ASCII
A-Z/space encoder with identical row width/destination/count ->
**offline-only** candidate digest / review.

`OriginalDialogueSafetyGate.Validate` now rejects a draft unless:

1. Room and authoring trigger match the same completed, original
   bank `$0A:$B8FF -> $EC47` call, stage and source message byte.
2. Command-buffer extent exactly matches the bytes parsed; no ring
   wrap or inferred overrun is allowed.
3. Independently parsed original bytes reproduce the source SHA-256.
   A previously bound hash must still match, preventing stale drafts.
4. Every source tile in the affected rows is mapped within the
   restricted Latin subset, every authored character is representable,
   and the original row geometry is unchanged.

Any unverified glyph or control code, mismatched source event,
changed source hash, non-text command, changed length, or truncation
**blocks** the preview. Only the authoring trigger and source hash
may be saved to a `.nestudio` project: no ROM code, source tile
images, original queue bytes, or patched machine state.

This is a safety architecture, **not a completed guest replacement
pipeline**. There is no native command to write original CPU/PPU
memory or replace game text. The next proof requirement is
per-command `$0300` consumer provenance and actual VRC6 CHR bank
selection/visible tile parity against Mesen on an owner-private ROM,
before enabling non-Latin/japanese glyphs or live replacement.
