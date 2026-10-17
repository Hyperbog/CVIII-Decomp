# Verified ROM identity and physical PRG bank map

Authoritative target analyzed on 2026-10-03.

## File identity

- Source filename: `Akumajou Densetsu (Japan).nes`
- File size: `393232` bytes (`0x60010`)
- Full-file CRC32: `2E93CE72`
- Full-file SHA-1: `a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f`
- Full-file SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`

## iNES header

Raw 16-byte header:

`4E 45 53 1A 10 10 80 10 00 00 00 00 00 00 00 00`

Interpretation:

- 16 × 16 KiB PRG = 256 KiB
- 16 × 8 KiB CHR = 128 KiB
- Mapper 24 / VRC6a
- PRG CRC32: `BA6BDD6A`
- PRG SHA-1: `f6a2e1080fc1badf751fe48492ce3c513fd7ba91`
- CHR CRC32: `BF15255C`
- CHR SHA-1: `3d69816bd9502680b6ec48334808f9355da3a175`
- Combined PRG+CHR CRC32: `E349AF38`
- Combined PRG+CHR SHA-1: `beb7e005bcbac031ce61613fa47df24ad151e9ab`

## Physical 8 KiB PRG banks

| Bank | PRG offset | CRC32 | SHA-1 prefix |
|---|---:|---:|---|
| PRG00 | `00000` | `BE82EEB2` | `6957afc80c47` |
| PRG01 | `02000` | `BD3E9E40` | `28d0322b3d04` |
| PRG02 | `04000` | `EF81F012` | `f75799af1542` |
| PRG03 | `06000` | `691AB768` | `751bd2a7eeb8` |
| PRG04 | `08000` | `21F93DFA` | `ff80fbda88cb` |
| PRG05 | `0A000` | `73353E65` | `395647197af6` |
| PRG06 | `0C000` | `B61C9495` | `5601e4c69063` |
| PRG07 | `0E000` | `20D33AC1` | `03def938e519` |
| PRG08 | `10000` | `64FF3BE6` | `0d8df4187002` |
| PRG09 | `12000` | `78FB0E13` | `11fbc49ea5cb` |
| PRG10 | `14000` | `A87C4346` | `01a352393538` |
| PRG11 | `16000` | `98B49F07` | `9bdd0e98b454` |
| PRG12 | `18000` | `EC73FBB3` | `9c16ae8c5fdb` |
| PRG13 | `1A000` | `7F9F184B` | `c9a845b3a11a` |
| PRG14 | `1C000` | `5C467386` | `40d3a3bf9cb6` |
| PRG15 | `1E000` | `DC16F610` | `05cc37710f70` |
| PRG16 | `20000` | `50D28270` | `243513f2572d` |
| PRG17 | `22000` | `97CACF8E` | `c596400064a8` |
| PRG18 | `24000` | `609AC660` | `07fc950442d3` |
| PRG19 | `26000` | `FFC01F9C` | `f69b642a02c5` |
| PRG20 | `28000` | `72582976` | `fd34708a24ba` |
| PRG21 | `2A000` | `750A44AD` | `69286f7379b8` |
| PRG22 | `2C000` | `46E32CB7` | `4bca7c367862` |
| PRG23 | `2E000` | `1489EAF7` | `dbb13c81aab9` |
| PRG24 | `30000` | `4985614E` | `4dd0e14baa93` |
| PRG25 | `32000` | `43874E5A` | `20a58f9b04d3` |
| PRG26 | `34000` | `68558C94` | `d54034e2aaeb` |
| PRG27 | `36000` | `16E5F628` | `bfa24f4e9773` |
| PRG28 | `38000` | `9D54A396` | `551de476733a` |
| PRG29 | `3A000` | `CE8ABD85` | `244de57f6a7c` |
| PRG30 | `3C000` | `FDA54907` | `e8842b0ef4ed` |
| PRG31 | `3E000` | `EF76CA99` | `15fb6c0c4cc3` |

## CPU vectors in fixed PRG31

- NMI: `$E057`
- RESET: `$E00B`
- IRQ/BRK: `$E0F5`

## Proven boot banking facts

`PRG31:$E2D0` stores the requested 16 KiB bank value into zero-page `$23`; `PRG31:$E2D2` writes it to VRC6 register `$8000`.

At reset, RAM is cleared, so `$23` initially contains zero. `PRG31:$E211` temporarily selects VRC6 16 KiB bank `$0C`, calls `$87AE`, then restores the prior bank. VRC6 bank `$0C` maps physical `PRG24/PRG25` into `$8000-$BFFF`.

`PRG31:$E2C4` writes `$1E` to `$C000`, mapping physical `PRG30` at `$C000-$DFFF`. `PRG31` remains fixed at `$E000-$FFFF`.

Do not infer a physical target for a banked `$8000-$DFFF` call without establishing the active VRC6 register state on that path.
