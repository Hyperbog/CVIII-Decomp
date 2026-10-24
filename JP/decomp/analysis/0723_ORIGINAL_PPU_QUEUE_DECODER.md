# JP0723 — Original JP fixed-bank PPU queue

Scope: bounded, read-only interpretation of the original PRG31 $ED46–$EF6C CPU RAM $0300 queue. This does not re-execute PPU bus cycles, change native gameplay or establish a complete Stage 1 map.

## Source-authenticated command grammar

- The source queue contains commands 1–10 and a zero terminator. RAM $001E is the cursor AFTER the terminator.
- Source VRAM addresses are low/high in the queue and written high/low to $2006.
- 1 and 2: literal bytes until FF terminator; 2 uses VRAM increment 32.
- 3: repeat one value N times with increment 32.
- 4 and 5: respectively 4 or 2 groups of four literals at specified addresses, then one single write.
- 6: 32 literals; 7: 32 literals and 8 more at a second address.
- 8: 22 literals with increment 32; 9: same, then six single-address writes.
- 10: N literals. Source 6502 DEX/BNE loops make zero N mean 256 for 3 and 10.
- Original PPUCTRL mode table $EC7A,X selects increment 32 for 2,3,8,9 and increment 1 for other commands. It restores RAM[$FF] afterward.

## Evidence

Original Mapper24 Japanese cartridge SHA256: 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
Local offline independent Python and C11 queue decoders accepted 256/256 original JP0718 Mesen CPU RAM snapshots. They matched on 534 commands and 1,306 ordered, predicted $2007 write events, including address/value/command. These are reconstructed from the saved queue bytes; they are not direct PPU-bus instrumentation.
Observed queue command types were 1,4,5,6; ROM-free invented input regression additionally exercises all ten command types, count zero, malformed buffers and 14-bit PPU wrapping. GCC C11, ASan and UBSan passed locally.

## Producer findings

- Fixed original PRG31:$E08F contains a direct call to $ED46.
- Original raw PRG16 bank $0A:$B873–$B8A5 constructs zero-fill queue entries from a triple table beginning $B8A6. Nine table entries target $24C0, $2500, $2540, $2580, $25C0, $2600, $2640, $2680 and $26C0; all lengths are $40. It is a clear producer, not authentic nonzero room geometry.
- Raw bank $0A:$B75D builds a nametable text update from RAM $07F8 at original PPU address $2622. This is not a world tilemap decoder.

## Integration boundary

These new source files are dormant. The JP0720–JP0722 persistent world prototype and owner-private preloaded tile evidence are not in this public branch. The dynamic room-background producer-to-ROM resource stream still needs semantic closure; source-code byte patterns alone cannot establish liveness.
No original retail bytes, CHR artwork, compiled game or private geometry packs are committed. VPP remains 31/100; strict semantic PRG 49,504/262,144.

To test: compile JP/recomp/native/enhanced/cviii_ppu_queue_0723.c and cviii_ppu_queue_test_0723.c with C11 and run the binary, or build CMake target jp_ppu_queue_test_0723.
