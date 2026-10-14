# JP0618 — Enhanced-only audio level foundation (Master + future Music/SFX buses)

**Product contract:** The **shipping port is Enhanced only**, but reproduces original *Akumajou Densetsu* movement, physics, combat, enemy timing, input, world layout and progression as its behavioral baseline. Intentional fixes, presentation/audio improvements and quality-of-life features may diverge from original presentation while game-mechanical changes must be separately documented and tested. The internal Original option stays available solely for A/B engineering diagnostics; it is **not** a second shipping edition.

## Confirmed 3-slider user specification

| Row | Values | Left/right | Baseline | Final visual |
|---|---:|---:|---:|---|
| MASTER | 0–100 | 1 percent | 100 | Authentic in-game health-bar tiles + original font number |
| MUSIC | 0–100 | 1 percent | 100 | Same |
| SOUND EFFECTS | 0–100 | 1 percent | 100 | Same |

Navigation will select the row with Up/Down and adjust with Left/Right, clamping to 0/100; the numeric value is a true 0–100 integer in the in-game font. **This final graphical menu is not yet implemented**. Reusing the original health bar graphics/font correctly requires authenticated CHR/tile palette and layout mapping instead of inventing substitute art. The existing generic host menu slider does not meet this visual contract.

## Implementation in this bounded step

[Native C11 host level state](../native/enhanced/cviii_audio_levels_0618.c) stores separate `master`, `music`, `sfx` 8-bit integers. All default to 100, accept only exact decimal 0–100, and the dedicated step helper moves exactly 1 at a time with endpoint clamps. The host config.ini [Game] save/load callbacks use the keys `MasterVolume`, `MusicVolume`, `SoundEffectsVolume`. Save-state load and game power-on **do not reset player preferences**.

The game's host `audio_mix` callback (declared by the pinned NESRecomp `cyc_host_extras.h`) is executed **after the emulation thread produced a mixed 16-bit PCM block** and before SDL queues it. In Enhanced mode, [the callback](../native/enhanced/cviii_edition.c) scales the whole PCM buffer by `MasterVolume/100` with 32-bit intermediate arithmetic: 100% is bit-exact unchanged, 0% is silent, and the signed 16-bit extremes stay within range. It does not modify emulated APU/VRC6 registers, clocks, sound-driver data, CPU, controller input, physics or save-state serialization. Legacy internal Original diagnostic mode bypasses the enhanced master scaler for source comparison only.

**Crucial limitation:** The existing 2A03 and VRC6 channels have already been mixed together at this point. `MusicVolume` and `SoundEffectsVolume` are **stored but deliberately not applied** to this shared signal. Applying either to the whole signal would mislabel and corrupt the intended separation. Actual music/effect mixing requires independent software voice ownership/streams (JP0610–JP0617 investigations), then an individual gain for each bus and the final Master gain.

For developer testing before the UI is implemented, launch Enhanced using `Launch-Alpha.ps1 -MasterVolume 73` to override Master only. Passing no override respects previously saved config instead of forcing 100 at every launch. The CLI accepts `--master-volume`, `--music-volume`, `--sfx-volume` as strict 0–100 developer values; Music/SFX are **settings only**, not live audio controls. The pinned host's own global volume setting may also attenuate the final output, so testing should leave the existing host global control at 100 to isolate JP0618 behavior.

## Tests and evidence boundary

- Standalone [strict C11 regression](../native/enhanced/cviii_audio_levels_test_0618.c) compiles with GCC `-std=c11 -O2 -Wall -Wextra -Werror -pedantic`, PASS. Tests 1% adjustments and endpoint clamping, out-of-range/rejected decimals, persisted read/write keys, unchanged 100% PCM, silent 0% PCM, signed minimum and maximum at 50%, and Music/SFX remaining independent of the master-only attenuation.
- The implementation, header and test source Git blob hashes match the locally compiled copies. Linux isolated enhanced-host test source list was updated to link the new component; CMake creates `jp_audio_levels_test_0618`; Windows Alpha CI includes its ROM-free target.
- The isolated full host integration and private native Windows GUI gameplay were **not rebuilt/executed here**. Actual GitHub Actions results have **not** been checked. No new video/menu screenshot, authentic health bar/font placement, user music/SFX mixer or gameplay parity is claimed.
- Original JP ROM SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28 remains owner-local and unmodified.

**Next bounded work:** (1) Authenticate the game's actual health-bar segment graphics, palette and numeric font; (2) present an Enhanced options overlay with three original-art 1% sliders and input isolation; (3) implement actual independent music and SFX source buses with their respective gains, preserving baseline gameplay timing and making enhancements explicit.

**Progress accounting unchanged:** 49,504 / 262,144 semantic PRG bytes (18.8843%), VPP 27 / 100, last certified checkpoint 0508, fixed frontier $FB96. `RESUME_STATE.json` unchanged. This native *presentation* enhancement does not certify new semantic ROM bytes or game/music parity.
