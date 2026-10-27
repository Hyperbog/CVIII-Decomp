# JP0665 — Fixed-bank $EC47 original room-message formatter checkpoint

## Source authentication (private original retail Japanese ROM)

Verified against SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Use `python JP/decomp/tools/audit_original_ec47_0665.py --rom <private-JP-ROM>`
to independently recheck 15 instruction windows. The `--smoke` mode
does not open a ROM and runs in public Windows CI.

Original raw 16 KiB bank **$0A**, CPU `$B8F4`: `LDY $07A5`, next
`LDA ($0A),Y`, `CMP #$FF`; nonterminal data reaches
`$B8FF: JSR $EC47` with `X=$08` and the message byte in A.
This original room-message stream contains bounded per-stage byte
choices; a source byte is not itself a Unicode character or NES glyph.

Actual original fixed-PRG control flow:

1. `$EC47` pushes A, sets A=$00 and JSRs `$E2CA`.
2. `$E2CA` saves the previous mapped 16 KiB bank (`$23` to `$24`),
   switches to bank $00 through $8000, and returns.
3. `$EC4D` restores the message byte; `$EC4E` calls
   original bank00 `$966A` (which preserves the X argument).
4. Bank00 `$9675` shifts the input byte for a 16-bit pointer-table
   lookup at `$96B9`, uses `$EC61` to load a table byte and
   `$EC72/$EC74` to append bytes to the original CPU
   command buffer beginning at `$0300`. `$1E` is the producer cursor.
   Distinct $FF and $FE control values are handled by the original
   bank00 formatter. Their full semantics and character mapping
   are not asserted without further replay.
5. After bank00 returns, `$EC51` jumps to `$E62D`, which loads
   the previous bank `$24` and restores mapping at `$E2D0`.

The original fixed-bank path beginning `$EC85` also reads bytes from
the `$0300` command stream and issues `STA $2006` for VRAM
addressing and `STA $2007` for tiles. Three verified $2007 writers
are at `$EC99`, `$ECB1` and `$ECC9`. Thus **$EC47 queues an
original formatting command; its immediate body does not directly
write glyphs to PPU**.

## Native implementation and proof boundaries

The pinned NESRecomp read callback observes an **actual original
instruction at $E2CB: LDA $23**. It only reports an EC47 formatter
invocation when the original bank selector equals $0A, the mapped
opcode signatures match, source $B8F4's token and X=$08 match, and the
6502 stack contains the nested return EC4C, saved original A, and
caller B901. A true completed invocation additionally requires
original `$E62D: LDA $24 / JMP $E2D0`, previous bank value $0A and
the original B901 return still on the stack.

The observer counts genuine `$EC72` output-cursor reads and records
the $1E producer cursor before/after the formatter. PPU correlation
accepts only original nametable $2007 writes whose executing site
(or next PC after executing) contains the original `8D 07 20`
opcode in the `$EC85-$ED80` command flush region, and which occur
within two source frames after a completed invocation. This is
**temporally correlated with an authenticated buffer writer**,
not proof that a given PPU tile belongs to the last EC47 call.

The v4 native/editor shared mapping extends v3 without moving any
previous ABI field; editor-side dialogue can bind an authored record
to a completed, original `B8FF -> EC47` source invocation. The
guest CPU, PPU, RAM, mapper and ROM are not changed.

## Still unproven

- Complete data model of the $96B9 table and all control bytes / glyph
  identities; no complete Japanese font/encoding map
- Per-command consumer ownership when several producers share the
  original $0300 buffer
- Exact PPU tile/glyph provenance over the full flush lifecycle, including
  frame carryover, NMI and all original message sources
- Safe guest text replacement or layout override

Do **not** enable original guest-text replacement until the command
stream and consumer parity are independently proven with real Mesen
and privately built native-game traces.
