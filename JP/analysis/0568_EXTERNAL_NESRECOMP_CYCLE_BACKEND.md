# JP 0568 — optional external NESRecomp cycle hardware integration

**Status: integrated build interface, not yet a validated Japanese-game run.**

`JP/native/nesrecomp_cycle/CMakeLists.txt` directly uses upstream
`nesrecomp_add_cycle_game()` to generate cycle-accurate native C for the
authenticated Japanese Akumajou Densetsu ROM at **configure time**.
It builds `jp_akumajou_densetsu` against NESRecomp's 2A03 bus, 2C02,
APU, DMA and mapper24 VRC6 hardware. No game-specific copy of NESRecomp
source or generated original-game source is added to this repository.

`JP/tools/nesrecomp_cycle_0568.py` checks original ROM SHA-256,
iNES mapper24, byte size and 256 KiB PRG/128 KiB CHR, checks the
separately obtained NESRecomp checkout and its PolyForm Noncommercial
License 1.0.0, configures/builds the C11 cycle runner, and optionally
executes `--frames 120` headlessly with a bounded timeout and report.
Run logs and generated code are placed **outside** the Git repository.

```sh
# First obtain NESRecomp separately, and review its noncommercial license.
python3 JP/tools/nesrecomp_cycle_0568.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --engine "/private/nesrecomp" --out "/tmp/jp-cycle-0568" --frames 120
```

The `--plan` option validates media and external engine then prints
the exact configure/build/execute commands without running them.
Use `--windowed` to request a GUI build (SDL2 may be required).

Upstream: https://github.com/mstan/nesrecomp
- `runner/cyc/project.cmake` exports `nesrecomp_add_cycle_game`.
- `runner/cyc/MAPPERS.md` lists mapper24 (VRC6a) PRG, CHR,
  nametable pins, WRAM gate, IRQ and expanded audio.
- `runner/cyc/hw_vrc6.inc` and `vrc6_test.inc` implement and test
  VRC6a/b mapper register behavior.
- Upstream PolyForm Noncommercial 1.0.0 imposes noncommercial restrictions;
  use this external backend only consistent with that license.

Public CI runs a *synthetic* command/ROM/license validation test
(`test_nesrecomp_cycle_0568.py`), not upstream source or a retail ROM.
Zero process exit on a real run would prove the engine accepted the
game and completed bounded execution; it would **not** itself prove
correct pixels, sound, input, independent Mesen CPU/frame parity or
total decompilation.

Existing C11 physical-site compiler 0562–0567 and existing C++ proofs
remain unchanged and separately testable. Strict PRG 49,504/262,144,
VPP27/100, previously recorded 4,261 compiled instruction sites are
unchanged until authenticated trace comparisons are available.
