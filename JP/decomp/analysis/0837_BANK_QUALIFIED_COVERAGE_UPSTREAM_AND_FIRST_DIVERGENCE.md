# JP0837 — Bank-qualified coverage, upstream compatibility, first divergence

**Scope:** Original Japanese *Akumajou Densetsu*, iNES mapper 24, original SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Private owner ROM/capture and native traces stay outside Git. Source-only patch; no gameplay parity claimed.

## First executable component

`JP/recomp/tools/jp0837_bank_coverage_firstdiff.py` uses the authenticated JP0835 `input.tsv`/`ram.tsv` ZIP via JP0836, native CYCFRAME via JP0834, and actor watched RAM locations via JP0833. It **does not** reconstruct executed PCs or bank state from static RAM samples.

The pinned NESRecomp engine provides three independently useful diagnostics:

- `--miss-log`: **interpreted ROM instruction starts**, physically qualified as `4k:BB:AAAA count`, where `BB` is a 4KiB physical PRG bank and `AAAA` is the mapped CPU instruction-start address. An empty miss log means no interpreted ROM starts *in that run*, **not** full-game coverage. Mapper24's `E000–FFFF` fixed 8KiB window is checked against the final two 4KiB PRG banks. The diagnostic seed file is safe as a build input only for the same authenticated ROM image and engine specification.
- `--capture-log`: interpreted **RAM** code; this requires separate owner-private snapshot handling and is *not* included in the ROM seed file. This JP0837 component does not collect RAM-code capture variants.
- `--hash-out`: full 0..3900 native and interpreter-only frame trace/memory/CPU/interrupt/cycles/internal-hardware signatures. JP0837 reports the earliest differing frame and fields. Each run also records 3090..3900 post-frame 2KiB CPU RAM via `--frame-log-at mesen`; JP0837 locates earliest full-RAM byte and earliest JP0833 watched-field mismatch against the actual original Mesen archive.

**Important:** JP0835 records controller intentions per local frame, not precise `$4016/$4017` bus read phase. Even an identical 811-frame actor-RAM window does not establish instruction-by-instruction Mesen/native parity. Native versus interpreter equality measures compiler correctness **within the same NESRecomp hardware implementation**. `--trace-frame N --trace-out FILE` is the pinned engine's next diagnostic after an actual first hash-mismatch frame is available.

## Actual checks completed for this patch

- Source archive CRC and original-JP ROM identity: passed. Source ZIP SHA-256 `bd41c9c241d100e112c166ee8d0cf0928d39840399c3e28e854d58609ea4e46d`.
- 3,900 original controller-frame records, 1,206 consecutive post-frame original 2KiB RAM snapshots (frames 2695..3900), 810 successive samples of both parent-linked type-`$3D` actors (3091..3900): passed against actual user-supplied files.
- ROM-free synthetics: 4KiB bank-to-physical offset, fixed-window rejection, empty miss-log acceptance, watched actor RAM first mismatch, native/interpreter hash first mismatch: passed.
- **No NESRecomp executable was available in this execution environment.** Actual compiled/interpreter frame comparison, nonzero interpreted miss counts, and first real diverging frame are **not observed**. Script reports `capture_authenticated_no_native_trace` and both verification fields `false` when only owner inputs are present.

## Upstream compatibility audit

Existing CVIII pin: `mstan/nesrecomp` `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`. Upstream `master` inspected: `466249489898be9f92aa369de4bbc5aad0d8feb2`; **159 later commits**. Verified against GitHub compare API. Mapper 24/VRC6 banking/IRQ/audio support (`ca85b7efa...`) was included **before** the pinned commit. No mapper change is necessary for a valid baseline.

Upstream changes since the pin include `runner/cyc/cyc_host.c`, `cyc_run.c`, `hw_mapper.c`, `hw_ppu.c`, `hw_apu.c`, `cyc_input.c`, `cyc_sdl.c`, `cyc_state.c`, `project.cmake`, and recompiler `cyc_codegen.c`. CVIII `JP/recomp/native/nesrecomp_cycle/CMakeLists.txt` uses pinned-source overlays for these upstream files, particularly controller input, SDL menus/savestates, CHR fetch, nametable writes, audio/DMA, and sound routing. **An untested fast-forward is not safe.** The upstream native/interpreter tests and ROM-independent mapper tests can be studied or separately ported; changing the pinned dependency needs specific overlay rebases and full regression/replay evidence.

The first high-return integration is **not** changing the engine: collect physical-4KiB ROM instruction misses from actual native Stage 1 gameplay, feed validated miss-log rows into the existing engine's `SEED_FILE` support (after an independent seed approval), and compare compiled vs `--interp-only` hashes. `CAPTURE_FILE` must remain separate because its meaning is executed RAM code.

## Windows owner invocation

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
python .\JP\recomp\tools\jp0837_bank_coverage_firstdiff.py --smoke

$rom = 'C:\Tools\Mesen2\Akumajou Densetsu (Japan).nes'
$zip = "$env:USERPROFILE\Documents\MesenCE\LuaScriptData\jp0835_capture_20261108.zip"
$out = "$env:USERPROFILE\Documents\jp0837-private"
$exe = 'C:\REPLACE\WITH\YOUR\ACTUAL\jp_akumajou_densetsu.exe'
Test-Path $rom; Test-Path $zip; Test-Path $exe

python .\JP\recomp\tools\jp0837_bank_coverage_firstdiff.py `
  --rom $rom --owner-capture $zip --out-dir $out --native-exe $exe
```

The first two files and the executable must exist. If the executable is unavailable, omit `--native-exe`: the tool validates the owner archive but produces **no coverage seed and no parity claim**. The actual native/interpreter run creates private `native.misses`, `native.hashes`, `interp.hashes`, `native.cycframe`, `interp.cycframe`, `jp0837-bank-qualified-seeds.txt`, and `jp0837-report.json`. Use a fresh output directory for each experiment; the tool refuses overwrites. `--existing` is a **noncertifying diagnostic** of externally supplied run files and deliberately returns nonzero.

**No automatic commit or CMake seed-file activation.** Any produced seed is a private execution observation until reviewed and replayed. The original Japanese ROM, VRC6 mapper and fixed code/data provenance remain authoritative.