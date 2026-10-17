# Checkpoint 0507 — NMI dispatcher physical bank proof and candidate room-state graph

**Authoritative source:** JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. This checkpoint intentionally separates one **newly admitted code range** from hundreds of **conditional structural candidates**. The US disassembly is not used as proof.

## Fixed NMI evidence establishes raw bank $0A

The first-level $E7FB inline table following fixed $E360 contains slot $0D -> $E526. The already verified code at $E526 is:

```asm
E526  A9 0A       LDA #$0A
E528  20 D0 E2    JSR $E2D0
E52B  4C CC B4    JMP $B4CC
```

Fixed E2D0 is `85 23 8D 00 80 60`: `STA $23; STA $8000; RTS`. The VRC6 $8000-$BFFF window is therefore definitively **raw bank $0A when this transfer occurs**. This resolves the mapping for a previously opaque 04FE fixed-to-switched PRG exit. It does not establish the global producer domain for first-level selector $18 or claim index 0D executes during every run.

The direct, byte-complete entry is raw bank $0A CPU `$B4CC-$B4D0`:

```asm
B4CC  A5 19       LDA $19
B4CE  20 FB E7    JSR $E7FB
```

Its five bytes are physical 8-KiB PRG bank 21, physical PRG offsets `$2B4CC-$2B4D0`, ROM file offsets `$2B4DC-$2B4E0`; SHA-256 `0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7`. **Exactly five genuinely new bytes are credited**, never the already admitted fixed E526/E2D0/E7FB code.

## Twelve encoded room-state pointers: conditional classification, NOT live proof

The word pairs immediately after $B4CE, $B4D1-$B4E8, encode:

| State | Target | State | Target | State | Target |
|---|---|---|---|---|---|
| $00 | $B570 | $04 | $B5CC | $08 | $B64E |
| $01 | $B58C | $05 | $B5DA | $09 | $B5CC |
| $02 | $B597 | $06 | $B614 | $0A | $B5DA |
| $03 | $B5A3 | $07 | $B622 | $0B | $B662 |

Recursive official-6502 decoder: **281 candidate instruction starts**, **582 code/operand bytes**, **six noncontiguous ranges**, zero unknown opcodes, zero overlapping instructions, and **11 candidate JSR $FB96** sites. Candidate range classification:

```text
B49A-B4B0  23 bytes   provisional
B4CC-B4D0   5 bytes   independently verified entry
B4E9-B501  25 bytes   provisional
B570-B68D 286 bytes   provisional
B6A4-B6E7  68 bytes   provisional
B7F7-B8A5 175 bytes   provisional
```

Candidate fingerprint SHA-256 `807363d09368f7ae6ceaeae000df0fc50f56bba5bd2871ca749d7236ec9f3828`. **The 582 is not a strict coverage increment.** The decoder treats E7FB as a terminal inline dispatch, not a normal returning JSR, so pointer pairs are not misinterpreted as 6502 instructions. In particular, the width of the encoded table is **not** a proof that selector $19 can only be $00-$0B.

The preceding 0506 state protocol is mechanically corroborated: conditional state 1 at B58C invokes B4E9 (`LDA #0; STA $68`) and increments $19; conditional state 2 at B597 calls B689, whose secondary selector 0 points to B6A4; that branch can call B7F7 after a carry precheck. The loader has eleven JSR FB96 reads that temporarily map raw bank $0E and restore $0A. **Cross-frame mutation, $B6A4 carry precondition, helper PRG return contexts, and $07A0-indexed B8C2 pointer extent are unresolved.** $FB96 and $FC17 remain unclaimed.

## Negative AI-script producer findings

The tempting immediate bytes $24/$25/$26 in raw bank $0B do **not** establish direct scripts $24/$25/$26:

- `$863B: LDA #$24; STA $0606,X`: different object field
- `$9234: LDA #$25; STA $05C1,X`: subscript index, not script ID
- `$9531: LDA #$26; JSR $E249`: call to a helper, not direct script-ID assignment
- `$B4BC: LDA #$24; JSR $E249`: helper call, not direct script-ID assignment

This does not rule out indirect or table-driven script IDs, but avoids four false direct-producer claims. The action-handler links ID $24/$25/$26 from 0506 remain **structural only**.

## Native address/flag lift and reproducibility

`JP/decomp/src/room_state_dispatch.hpp` accepts a mapped CPU-bus reader, models 8-bit ASL selector doubling, and preserves the incoming Y/6502 final C/Z/N flags. The E7FB ABI's final `LDY $03` sets Z/N from **saved Y**, not the 16-bit target high byte. The model returns pointer and register results but does **not** execute stack pops, writes to zero page $00-$03, or handler instructions.

`JP/decomp/tests/room_state_dispatch_test.cpp`: **65,536** combinations (256 selectors × 256 incoming-Y values) against authoritative JP raw-bank $0A bytes, checking pointer values, aliasing of selector values differing by $80, carry differences, and flags. `JP/decomp/tools/audit_nmi_room_dispatch_0507.py` independently validates the NMI dispatcher slot, mapper code and physical entry, exact new-byte hash, candidate graph/fingerprint, and four non-producer cases.

```sh
python3 JP/decomp/tools/audit_nmi_room_dispatch_0507.py '/path/to/Akumajou Densetsu (Japan).nes' 0507_report.json
g++ -std=c++17 -Wall -Wextra -Werror -pedantic JP/decomp/tests/room_state_dispatch_test.cpp -o /tmp/room_dispatch_test
/tmp/room_dispatch_test '/path/to/Akumajou Densetsu (Japan).nes'
```

**Strict PRG floor: 49,399 → 49,404 / 262,144 = 18.8461%. VPP remains 24/100.** Since all newly admitted bytes are raw bank $0A and not the physical fixed tail, the raw fixed PRG31 investigation frontier stays $FB96 and **all six outstanding fixed-bank gaps remain unclaimed**.

## Next checkpoint 0508

Prove live $18=0D and $19/68 producer/value domains across frame boundaries; resolve B6A4's carry gate, external callee bank restoration, $07A0-selected room pointer table; then promote more of the conditional 582-byte graph and fixed FB96 when justified. Separately trace actual producers for script IDs $24/$25/$26 and any qualifying fixed FC17 calls. Continue FD62,Y domain and transitive shared ZP $10 last-writer proof without inventing bounds.
