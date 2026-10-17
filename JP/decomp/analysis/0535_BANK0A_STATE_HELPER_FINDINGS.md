# 0535 — Original JP bank0A state-machine and bank0C helper source

## Original ROM evidence
Japanese *Akumajou Densetsu* retail ROM, VRC6 mapper 24, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

The preexisting 0506 `audit_bank0a_state_chain_0506.py` proves the 12-word
state jump table at CPU `$B4D1`, `$B4CC`'s original E7FB dispatch caller,
the `$B689` selector and the `$B7F7` loader bytes. The 0535 lift follows
these **12 pointer-defined entries**, plus producer/loader roots, through
official NMOS 6502 control flow. It does NOT follow arbitrary ROM bytes
after `JSR $E7FB` (inline selector call), and it stops at return/jump edges.
The result is **244 instructions / 502 opcode+operand bytes** in six
physical source intervals: `$B49A–$B4B0`, `$B4CC–$B4D0`,
`$B4E9–$B4ED`, `$B4FA–$B501`, `$B570–$B68D`, `$B7F7–$B8A5`.
The original 12 `.word` state entries at `$B4D1–$B4E8` account for
another **24 typed bytes**. The concatenated instruction-byte SHA-256
and pointer SHA-256 are checked independently.

Bank `$0C` original source has two literal `JSR $A992` encodings at
raw `$01:$AB88/$AB93`, plus a fixed-side `JSR $A9D5` encoding at
`$E39C`; bounded decoding of the corresponding physical raw0C
`$A992–$A9E0` source recovers **42 structurally consistent instructions
/ 79 bytes**. The decoded `$A9C8` indexed consumer loads from
`$A9E7`, where an additional **nine 16-bit values / 18 bytes** are
represented as a typed lookup table. **Active VRC6 bank mapping at the
cross-bank call sites and lookup index domains remain unproven**;
these 97 bytes are source candidates, NOT original runtime reachability
claims or new strict semantic credit.

## Source accounting and boundary

| 0535 newly classified source | Bytes |
|---|---:|
| Bank0A original 0506 state-rooted 6502 instructions | 502 |
| Bank0A 12-word state table | 24 |
| Bank0C conditional helper 6502 instructions | 79 |
| Bank0C 9-word lookup (index domain open) | 18 |
| **Total** | **623** |

Cumulative classified PRG source increases **50,223 → 50,846**.
Cumulative 6502 opcode/operand source increases **14,397 → 14,978**.
Typed original pointers/tables increase **2,484 → 2,526**.
Bank04/05 certified script data stays **28,200**;
bank0C rooted sound pool stays **3,523**;
bank0C secondary structurally bounded phrases stay **1,619**.
Remaining unclassified original PRG is **211,298 bytes**.

Strict semantically credited PRG remains **49,504 / 262,144 (18.88%)**.
VPP stays **27/100**, completed checkpoint 0508 and fixed frontier
`$FB96` remain unchanged. No claim of playable native recompilation,
new instruction-execution parity, or closed dynamic mapper domains.

## Reproduction

Run from the repository root with *your own Japanese retail ROM*:

```sh
python3 JP/decomp/tools/test_bank0a_state_0535.py
python3 JP/decomp/tools/test_bank0a_state_0535.py --rom "$ORIGINAL_JP_ROM"
python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp-0535-banks
```

ROM-backed tests include ten source corruption negatives over the state graph,
state jump table, helper entry opcode, lookup table and cross-bank encoded
calls. All 25 bank sources independently reassemble every byte of the
original **393,232-byte iNES image**. ROM-free CI checks the assembler and
static root/accounting contracts; the original commercial ROM is never
committed.
