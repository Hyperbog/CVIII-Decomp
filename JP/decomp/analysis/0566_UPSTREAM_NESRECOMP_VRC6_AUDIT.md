# JP 0566 — StarFox method transfer and NESRecomp VRC6 audit

**Upstream implementation reference:**
[mstan/StarFoxSNESRecomp](https://github.com/mstan/StarFoxSNESRecomp)
uses a separately pinned `snesrecomp` framework and generated C with
an interpreter fallback, plus console/runtime hardware and a game's
specific host hooks. The corresponding NES framework is
[mstan/nesrecomp](https://github.com/mstan/nesrecomp), which documents
its C11 cycle-accurate backend and CPU/PPU/APU/DMA model.

The public NESRecomp game/mapper support table currently lists
0/1/4/66 as supported and **does not qualify mapper24 as a playable
game**. However current upstream `runner/cyc/hw_vrc6.inc`
explicitly recognizes `mapper == 24 || mapper == 26` and includes
VRC6 bank switch, CHR, mirroring, WRAM, IRQ and pulse/saw audio
handling. `runner/cyc/vrc6_test.inc` contains ROM-free VRC6 register,
bank pin, IRQ and audio tests for mapper24/26. This is encouraging,
**not proof of Castlevania III game integration or cycle parity**.
The existing JP is mapper24 (original header `NES 1A 10 10 80 10`).

**Licensing:** upstream NESRecomp declares
PolyForm Noncommercial 1.0.0. Do not silently copy, vendor, relicence
or distribute that implementation under a different license. The
0562–0565 original CVIII C11 source is independently authored.
If we select NESRecomp runtime as an external dependency, review
licensing, project use and external pins first.

## Optional real generator probe

```sh
python3 JP/decomp/tools/probe_nesrecomp_cycle_0566.py \
  --rom "$ORIGINAL_JP_ROM" \
  --tool /absolute/path/to/nesrecomp \
  --out /tmp/jp-nesrecomp-probe
```

The probe verifies Japanese ROM SHA-256, size, original header mapper24;
invokes `nesrecomp build --backend cycle` with output **outside**
the repository; requires actual `*_cyc*.c` generated files;
then records a provenance report marked as **not compiled / not tested
against gameplay**. It fails rather than declaring unsupported
mapper24 generation a success. Public CI tests only synthetic
header validation and fails if spoofed media is presented.

## Recommended next gate

1. Run upstream CLI on the private original-JP mapper24 ROM.
2. If generator succeeds, compile the generated C with its own
   pinned, license-reviewed runner in a private build.
3. Compare physical PRG views and instruction execution against
   0562–0565 independent C path and original 6502 reference.
4. Prove real VRC6 audio/mirroring/IRQ and PPU/DMA behavior; only
   then choose upstream runtime or merge adapters for full game.
5. Keep the prior audited 4,261 sites and PRG/VPP certificate
   independently measured.

Nothing here adds game frames, new strict PRG coverage or VPP:
27/100; 49,504/262,144 strict; 4,261 existing sites.
