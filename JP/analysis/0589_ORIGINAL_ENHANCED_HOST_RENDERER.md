# JP 0589 — Original/Enhanced host edition layer and experimental OAM sprites

A concrete C11 runtime extension is now available under
`JP/native/enhanced/cviii_edition.c`, using the separately licensed,
pinned external NESRecomp `CycHostExtras` **public game extension API**.
No upstream source, copyrighted ROM or generated game code was copied
into this repository. The existing CMake game target compiles the extension
by default (option `JP_EDITION_HOST_EXTRAS=ON`).

**Original by default:** `cyc_host_extras()->present` returns the engine's
native 256×240 pixels unchanged, without background capture or compositing.
The original $2002/sprite-0/overflow/IRQ/DMA and CPU state are untouched.

**Enhanced opt-in:** `--edition enhanced --unlimited-sprites 1` or
persisted `[Game] Edition = Enhanced` and `UnlimitedSprites = 1`
captures the background image and composites up to 64 **OAM-present**
sprites using NESRecomp's existing `cyc_render_sprites` renderer,
`cyc_frame_bg_opaque` and palette/flip/priority semantics. No
original NES sprite-evaluation logic or hardware/timing registers change.
Game-side sprites never submitted into OAM cannot be recovered.

**Experimental caveat:** Present-frame sprite CHR may differ from CHR
used earlier in that scanline, especially in VRC6 bank-switched rooms.
Enable this only to test flicker relief; mid-frame CHR switching and
multi-stage background bugs (#1) are not solved. It does not expand
the world into widescreen or separate music and SFX yet.

One ROM-free strict-C11 fake-renderer unit test checks saved edition
settings, Original presentation identity, explicit opt-in, 64-OAM
composition callback and fallback. Pinned synthetic VRC6 external CI
also recompiles the *actual* new host C file into the game target.

No source reconstruction tests, ROM-derived assets, Mesen frame parity,
strict PRG or VPP credit are attached. Baselines remain VPP27/100
and 49,504/262,144 strict bytes.

For a windowed build, edit the owner's `config.ini`:

```ini
[Game]
Edition = Enhanced
UnlimitedSprites = 1
```

`Edition = Original` always disables the compositor regardless of the
secondary flag. No original-compatible savestate format is changed.
