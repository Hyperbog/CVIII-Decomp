# Akumajou Densetsu JP — native PC title-to-Stage-1 preview (0510)

**Status: playable technical prototype, not a finished game or faithful Castlevania III port.**

This is **real native C++20 execution**. The executable does not use Mesen,
6502 instruction interpretation, a NES emulator, PRG-to-native dynamic binary
translation, or the Japanese `.nes` ROM at runtime.

## What you can play

- Interactive title → short visual introduction → first-stage sample scene.
- Keyboard movement, one provisional jump arc, attack against one scripted
  sample enemy, a local stage exit and restart.
- A demonstration of the Japanese source-authenticated **first available
  actor slot search** (`$FF06`, slots 1..12) and **18-field indexed actor reset**
  (`$FF24`) in the native object's temporary state array.
- An independent native framebuffer, keyboard/input loop, X11 (Linux) and
  Win32 (Windows source branch) window front ends, and deterministic headless
  test mode.

## Controls

**Enter** advances from title to intro and skips the intro; intro also advances
itself. **Left/Right** (or A/D) move. **Z / Up** jumps. **X** attacks. **R**
restarts, **Esc** exits. Reach the far-right edge for the demo-complete state.

## Linux: run the packaged build

From the extracted package directory:

```sh
./run_linux.sh
```

Requires Linux x86_64 with X11/XWayland (`libX11.so.6`). A 768x720 window
opens with a 3x NES-resolution frame buffer. Run on a desktop session; SSH
sessions need `DISPLAY`/X forwarding. There is no SDL or emulator dependency.

## Build native source (Linux)

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
./build/cviii-jp-native-demo --assets assets
```

Requires CMake 3.16+, a C++20 compiler and X11 development headers.

A native Windows x64 executable was compiled on GitHub Actions' Windows
Server 2025 / Visual Studio 2026 runner. Its ROM-free state-machine CTest
passed; interactive Windows GUI behavior has **not** been manually exercised.
With an installed Visual Studio toolchain, use `cmake -S . -B build-windows -G "Visual Studio 17 2022"` then
`cmake --build build-windows --config Release`, and start the resulting
`cviii-jp-native-demo.exe --assets assets` from this folder.
**The separate user-specific downloadable bundle includes native Windows and Linux binaries, private reference art, and source. Public Git intentionally contains no retail art.**

## Launch the prebuilt Windows download

Extract the complete user-specific ZIP, keep the `assets` directory next to
the `.exe`, and double-click `run_windows.bat`. The app is native Win32/GDI and
does not run a NES emulator. The Windows CI validated build and self-test,
but a real user's GUI/keyboard compatibility test remains pending.

## Automated test mode

```sh
./cviii-jp-native-demo --self-test
./cviii-jp-native-demo --assets assets --headless --scene stage \
  --frames 75 --script r --output /tmp/stage-demo.ppm
```

The first test executes scene transitions, host movement, jump, attack, actor
slot cleanup and the local stage-exit state. Headless screenshot output is
binary PPM (256x240), suitable for pixel-golden regression.

## Source authenticity and remaining work

Source-verified: 6502 fixed-bank `$FF06` **first-free slot** and `$FF24` indexed
RAM field-clear semantics (see JP project `0509_ROM_FREE_ACTOR_PIPELINE.md`).
Everything else in this new demo is explicitly **preview-only**:

- Title/intro and first-stage art are offline stills captured from the
  user-provided original Japanese game through independent Mesen2. They are
  deliberately local/private derived reference assets, not a reconstructed
  native PPU scene decoder or dynamically rendered original NES CHR/nametable.
- The first-stage snapshot covers **one static scene**. Some background scenery
  is screenshot-retouched to remove frozen characters. No actual room scrolling,
  tile collision map, stage script, route selection or world transitions exist.
- Host-created player movement, jump, attack, hit test, single enemy and stage
  exit are **not source-authenticated Trevor Belmont physics/combat/AI**.
  There is no NES APU/VRC6 sound output, password/menu, bosses or alternate
  character gameplay.
- The old `JP/decomp/legacy/standalone0509` ROM-free actor/OAM technical demonstration is
  still the project's separate vetted proof of the actual OAM assembler; this
  title/stage preview uses a host bitmap presenter, **not** that verified OAM
  pipeline. Porting actor/OAM and original stage rendering into the native
  interactive runtime is the next major milestone.

No authored commercial game asset is intended to be committed to Git. The
asset PPMs/RGBA in this user-specific download were generated from the supplied
ROM's reference-emulator screenshots; the C++ code itself contains no retail
ROM or image data. For a code-only public repository, exclude `assets/*.ppm`,
`assets/*.rgba`, reference screenshots, ROM files and emulator savestates.

**Accounting:** completion evidence for original gameplay parity remains
strict PRG 49,504/262,144 (18.8843%), VPP 26/100, completed checkpoint 0508;
this provisional native demo does not earn additional strict bytes or VPP.

## Alpha 1.1 Windows startup/CTD mitigation

The first Windows ZIP used the MSVC dynamic runtime (MSVCP140/VCRUNTIME140 family), which was **not bundled** and could prevent startup on systems without the Microsoft C++ Redistributable. The rebuilt Windows x64 executable uses a static MSVC runtime (`/MT`) to remove that package dependency. CI now generates original-ROM-free fixture art and runs the actual Win32/GDI window for 120 frames, not merely the game-state unit tests. The launcher logs both its self-check and windowed failure codes to `demo_log.txt`, and retains a console on an error. This is a mitigation for the plausible CTD startup cause, **not** a confirmed diagnosis of the original user's crash. Remaining graphics driver/platform differences may require user machine logs.
