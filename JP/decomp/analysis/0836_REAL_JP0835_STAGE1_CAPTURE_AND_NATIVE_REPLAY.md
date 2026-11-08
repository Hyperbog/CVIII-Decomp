# JP0836 — New owner-private Stage 1-02 Mesen -> NESRecomp replay bridge

**Verified source ZIP:** owner-uploaded original JP0835 capture, authenticated against original Japanese Mapper24 ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` and SHA-1 `a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f`. Original ROM and private capture are **not** committed.

## Actual observations

- Original source capture ZIP integrity passed. Its own SHA-256 is `bd41c9c241d100e112c166ee8d0cf0928d39840399c3e28e854d58609ea4e46d`.
- `JP0835INPUT\t1\t...\t1`: 3,900 consecutive frame-indexed controller intentions, source-local frames 1..3900, footer `END COMPLETE 3900 3901`. This is not the old 17,562-poll JP0718 input archive.
- `JP0835RAM\t1\t...\t1`: 1,206 consecutive 2KiB post-frame RAM snapshots, frames 2695..3900; all have selector `00/01/00`.
- The original source-linked actors occupy slot 1/type `$3D`/parent source 3 and slot 2/type `$3D`/parent source 4 at **each sampled post-frame from 3091 to 3900**, exactly 810 frames each. Before frame 3091, the two designated slots do not simultaneously have this source provenance.
- Locally executed original ZIP validation, deterministic native schedule generation, repeat-output check, Python compilation, synthetic smoke and adversarial input/actor-corruption checks all passed.
- **No native NESRecomp run was available in this task environment.** These results prove original-Mesen snapshots, not synchronized gameplay parity.

## Run on Windows, using your actual ROM path

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
python .\JP\recomp\tools\jp0836_stage1_fresh_replay.py --smoke

python .\JP\recomp\tools\jp0836_stage1_fresh_replay.py `
  --rom "C:\Tools\Mesen2\Akumajou Densetsu (Japan).nes" `
  --owner-capture "C:\path\to\jp0835_capture_20261108.zip" `
  --out-dir "$env:USERPROFILE\Documents\jp0836-private"
```

Preparation validates all original input masks against the known JP0835 natural-gameplay sequence and creates a private `native-local.input` file (with native frame 0 empty) plus `jp0836-provenance.json`. On a second invocation with the **same** arguments and additionally `--native-exe "C:\path\to\actual-nesrecomp.exe"`, it runs the native original-edition runtime from power-on through frame 3900, produces `native.cycframe` over 3090..3900 and compares 811 aligned snapshots using the JP0834 CYCFRAME decoder and JP0833 actor RAM differential. It fails nonzero on mismatches.

The optional `--native-frame-log` mode is **diagnostic-only**: an existing CYCFRAME contains no authenticated controller input hash, so it cannot certify replay provenance. No existing private outputs are overwritten.

## Scope limit

`P\t<frame>\t<mask>\t00` records the per-frame **button intent** in the JP0835 Mesen Lua callback, not every CPU read of $4016/$4017. The native replay receives the matching local-frame schedule, but equivalent serial bus phase, exact CPU-cycle parity, intra-frame actor writers, physical collision, offscreen policy, and full PPU/APU/VRC6 fidelity are **not** proved by this conversion. VPP and strict original PRG certification remain unchanged.
