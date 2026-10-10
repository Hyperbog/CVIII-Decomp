# 0508 — Independent Mesen gameplay proves 100 fixed PRG31 code bytes

**Certification scope:** 100 **genuinely new, physically nonoverlapping Japanese PRG31 instruction/operand bytes** in two previously uncredited fixed-bank gaps. This is **not** whole-game completeness, code-data certification for other banks, or proof that original state `$18=$0C/$0D` is live. Source ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. CPU address `$E000-$FFFF` is permanently mapped to physical PRG31 on JP VRC6a.

## Four exact regions — admitted code and operands

| Phys PRG31 CPU inclusive | Bytes | ROM SHA-256 | Actual original-Mesen context |
|---|---:|---|---|
| `$FBA5-$FBAF` | 11 | `096871e75eb8f81b8bfd99da6f781473d40b5453325f8b8e4df00b003325ea62` | original intro/name route, breakpoint **frame 314** |
| `$FBB0-$FBBA` | 11 | `355f9853ac905aa90b52482b798e6d9603649b745ba6bb1db579d0a723f79c06` | original name-completion/prayer route, breakpoint **frame 605** |
| `$FF06-$FF11` | 12 | `c75f2332e11e13763245741d3f4ddb690f63dce3930c946cae3160090ac1488c` | original Stage 1-02 gameplay, breakpoint **frame 2030** |
| `$FF14-$FF55` | 66 | `9f4374fdf490e30015a28e44abdc20c87259b501064c1d8eb9f4fee353d40d1a` | original Stage 1 gameplay via object slot/clear calls |

**Total 100 distinct bytes**, represented by **4 + 4 + 6 + 25 = 39 instruction starts**. Each range is byte-complete and instruction-aligned in independent Mesen2 decoding. All 100 byte positions have the Mesen PRG CDL **CODE bit** set and **DATA bit clear** on the named source trajectory. Physical address = `31*8192 + (CPU-$E000)`. No instruction/raw game-byte listing or CDLv2 image is stored in Git.

Original debugger breakpoints and saved state validate three direct entries in the independent machine, without changing RAM or PC: `$FBA5` during original frame 314, `$FBB0` at 605 and `$FF06` at 2030. Mesen stepping from both intro breakpoints observes fixed `$E2CA` save/mapper-bank-$00 selection, genuine bank-$00 text/stream walker at `$8AB6/$8ABA`, an actual return to `$FBAD/$FBB8`, fixed `$E62D: LDA $24; JMP $E2D0`, then the real `STA $23; STA $8000` bank restore. The code path is **observed**, not synthetic-return-assisted. Mesen source trace SHA-256 for respective 3,000-instruction local samples:

- Intro: `ccf457e86d56f9d83ad9a164e7798c827c50a7f2d400ecbdafe8f5e0ee4d26fc`.
- Prayer: `44c604c8a1353526a8a45c5f98957ce8a2bd6c78fe34140f7e3ba223d8c66ba5`.

The live fixed `$FF06` branch scans `$054E,X` from `X=$01` toward `$0C`, exits early via `BEQ $FF14`, and has an as-yet-unobserved `$FF12-$FF13: LDA #$01` alternative. **Those two bytes are not admitted.** `$FF14` returns, `$FF15-$FF23` zero four `$04F2/$0509/$0520/$0537,X` fields; fixed `$FF24` invokes that initializer and zeros fourteen more indexed object-state fields, followed by `RTS` at `$FF55`. An actual 160-instruction Mesen trace following the `$FF06` debugger breakpoint executes `$FF06,$FF14,$FF15,$FF24,$FF55`; its private log SHA-256 is `3af9ae952852a7f44c78c91c7ddf39f39709c28d60f1d1e18e52389c47347a32`. Future stage/actor interpretations must retain the observed caller and bank context.

## Strict physical accounting / recovery

The **last completed checkpoint 0507** explicitly reserved `$FB96-$FBF5` (96 bytes) and `$FEEA-$FF55` (108 bytes) as unclaimed fixed PRG31 regions. New entry fragments fit strictly inside these two unclaimed gaps. Therefore no previously credited fixed or raw-bank bytes are duplicated. The 0507 raw-bank-$0A five-byte entry, 0501's 4,364-byte scheduler batch and all older coverage remain unchanged.

```text
prior verified PRG (0507)        49,404 / 262,144 = 18.8461%
0508 new live fixed code               100
new verified PRG total             49,504 / 262,144 = 18.8843%
overall fixed VPP rubric                26 / 100 (unchanged)
fixed physical investigation frontier   $FB96 (unchanged)
```

The unfinished fixed gaps become `$FB96-$FBA4` (15), `$FBBB-$FBF5` (59), `$FEEA-$FF05` (28), and `$FF12-$FF13` (2), plus the previously separate `$FAA0-$FAA9`, `$FC17-$FC1E`, `$FD59-$FDE3`, `$FF7A-$FFFF`. Although `$FF56-$FF5F` also executes during the observed Stage 1 path, **0501 already credited that region**. This is not a duplicate promotion.

## Reproduce

`JP/tools/audit_mesen_fixed_live_0508.py` checks original ROM SHA, all new fixed-code regions, 0507 gap boundaries and local bank-control opcode contract. When passed `--reference-emulator` and `--private-evidence`, it additionally checks the exact SHA-pinned independent Mesen executable/core, original-CDL physical code bits, Mesen's independent decoded opcode/operand boundaries, three debugger breakpoints and the stepped source traces.

```sh
python3 JP/tools/audit_mesen_fixed_live_0508.py "$JP_ROM" /tmp/fixed_0508.json \
  --reference-emulator "$PRIVATE_MESEN_BIN_DIR" \
  --private-evidence "$PRIVATE_MESEN_RUNS_DIR"
python3 JP/tests/test_mesen_fixed_live_0508.py
```

The private directory contains files `play520.cdl,stage220.cdl,right_jump_1200.cdl`, break logs `FBA5_break.jsonl,FBB0_break.jsonl,FF06_break.jsonl`, and `FBA5_3000.trace,FBB0_3000.trace,FF06_160.trace`. No ROM, raw code/data logger mask, state, screenshot, external binary or copied developer material is committed.

**Remaining open:** live room-$0C/$0D producers, unbounded AI/weapon alternatives, global object-slot producer domain, exact all-checkpoint strict overlap for *other* observed Stage 1 bytes, native vs reference CPU/PPU/APU parity. This narrow new code-credit is not permission to promote the other 16,672 observed code positions or 3,165 JP↔US exact-window candidates.
