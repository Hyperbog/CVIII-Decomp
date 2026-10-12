# JP checkpoint 0544 — Native VRC6 video bank setup on the integrated room path

## Scope

This is a **source-backed native implementation of original bank-$00 script ID 2**, entered at CPU `$8013` from the existing bank-$0A six-dispatch room-initialization caller. The independent original NMOS-6502 reference interpreter executes `$8013-$805E`, then the original fixed-bank `$E32B-$E35B` video register helpers through `$E331/$E33C/$E347` (with `JSR`/`JMP`/`RTS` stack semantics). The native C++ implementation performs the decoded pointer lookup and emits all eight hardware register writes in CPU order. This is not a full PPU/video renderer, and it is not live frame parity.

Original ROM: Japanese Akumajō Densetsu, SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Original script `$8013-$805E`: 76 bytes, SHA256 `fac711e72403bbd550e757e1df11c9cc66f3304892b785aa6913c6483b65c125`. Original fixed video helper `$E32B-$E35B`: 49 bytes, SHA256 `6b6b36abca16621ba14dd7f681e3c0ad16957894e37d6e2ac3e20a1b7de90f9f`.

## Authentic memory data flow

The input selector registers `$34/$35/$36` are set by the already-replayed bounded bank-$0E room stream. Script 2:

1. Loads a little-endian root pointer `word[$805F + 2*$34]` into ZP `$08/$09`.
2. Loads `word[($08/$09) + 4*$35]` into ZP `$0A/$0B`, then `word[($0A/$0B) + 2*$36]` into ZP `$3D/$3E`.
3. Loads `word[($08/$09) + 4*$35 + 2]` into ZP `$0A/$0B`, then `word[($0A/$0B) + 2*$36]` into ZP `$3A/$3B`.
4. Executes `$E32B` (`JSR $E331`; `JMP $E33C`) then `$E347`, writing the original hardware register sequence:

| Original write instruction | CPU register | Source RAM |
|---|---|---|
| `$E333` | `$D002` | `$3A` |
| `$E338` | `$D003` | `$3B` |
| `$E33E` | `$D000` | `$38` |
| `$E343` | `$D001` | `$39` |
| `$E349` | `$E000` | `$3C` |
| `$E34E` | `$E003` | `$3F` |
| `$E353` | `$E001` | `$3D` |
| `$E358` | `$E002` | `$3E` |

The reference CPU records each address, original PC, and value. The native model independently calculates the pointer words from the original bank bytes, updates the actual ZP values, and generates the same eight chronological register events. All pointer traversals are mapped-bank-checked; no arbitrary host pointer dereference occurs.

## Verification and CI

`python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx g++`

`python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx clang++`

Both compilers: **1,280/1,280 exact original-vs-native integrated cases**, covering five bounded room streams and 256 seed configurations each. JSONL diff additionally compares the resulting `$3A/$3B/$3D/$3E`, original CPU PCs and ordered hardware-register writes, all prior mapper transitions, and original return state. ROM-free smoke covers 1,280 synthetic cases with an independently specified two-tier pointer fixture and **8 corruption/invalid-input cases** (including a null pointer). Earlier authentic 0540–0542 6502/native comparisons, 0538 exact bank and 25-bank full-cartridge roundtrip still pass.

The existing `jp-native-regressions.yml` invokes `test_postdispatch_0543.py --smoke` through `run_native_regressions.sh`; modifications of the native code and test paths trigger its workflow. The retail ROM is never uploaded to GitHub.

## Remaining genuine work

The current full caller calls six scripts, in order **0,1,2,6,3,4**. **Scripts 1,2,6** now execute real original 6502 and have independent matching native C++ translations. **Scripts 0,3,4** remain explicitly zero-effect *test doubles* on both sides and are NOT reconstructed. Script 0 starts at original bank `$00:$84A0` and calls `$EC54/$8480/$852F`; script 3 begins in fixed PRG30 `$D03C`, with further calls `$C900/$D449/$C905`; script 4 starts at `$D0CD`. Neither original frame activation nor arbitrary VRAM/PPU effects, cycle timing, APU nor IRQ parity are implied by these tests.

Bank-$0A classified/candidate/unresolved census and strict PRG certification remain unchanged: **49,504/262,144 strict**, VPP **27/100**. Progress here is **native executable behavior and hardware-effect event parity**, not code-byte inflation.
