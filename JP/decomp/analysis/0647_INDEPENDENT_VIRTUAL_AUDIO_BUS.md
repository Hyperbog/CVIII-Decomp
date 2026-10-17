# JP0647 — Independent virtual Music/SFX PCM foundation

## Boundary: baseline remains unchanged

This checkpoint adds a bounded host-side **virtual audio mixer**, not an
authentic Japanese-game audio replacement. The original game retains its
existing 2A03/VRC6 emulation and original PCM. The Enhanced Master control
continues to attenuate that output; **Music and SFX are still preference
sliders, not live independent gains on the retail game**.

The original Japanese driver can suppress sounds before hardware writes.
JP0610–JP0617 and JP0646 establish sound request/branch research, but
complete original records, notes, envelopes, voice ownership and effects
are not decoded. A synthetic virtual voice is not a reconstructed
original soundtrack. Enabling it as the default game audio would be wrong.

## Production implementation

Files: JP/recomp/native/enhanced/cviii_virtual_audio_0647.h/.c.
The native Enhanced host compiles the module and stores its own dormant
mixer state. On power-on and guest state load it clears all virtual
voices. The native audio_mix callback does NOT call its renderer, since
there is no authentic original producer yet.

- 8 music and 24 independent SFX PCM voices. A full pool refuses new
  voices rather than stealing an existing song/effect.
- Caller-supplied signed-16 mono sample callbacks, with separate
  real samples (even silent ones) and end-of-voice signals.
- Unique monotonic 64-bit voice IDs, explicit stop and stop-bus,
  bounded sample blocks and fail-closed invalid settings.
- Individual Music and SFX gain (0..100) followed by Master gain
  (0..100). Sum in signed 64-bit, scale before clipping once to
  signed-16. Muted voices advance rather than freezing their timing.
- Power-on/load cleanup preserves ID progression to reject old
  references. The virtual state is host-only; no NES savestate or
  CPU/APU/PPU/mapper data changes are made.
- The API is synchronous and must be driven by one serialized audio
  owner. Callbacks must not reenter the mixer. A synchronized
  event queue will be required for later game-thread and SDL-audio
  thread integration.

## Test evidence

cviii_virtual_audio_test_0647.c exercises the production C11 mixer:
overlapping music/effect tails, independent gains, saturation after
scaling, 8+24 simultaneous notes, no voice stealing, per-voice and
per-bus shutdown, reset and stale token rejection, ID overflow, invalid
inputs, and Windows Release assertions enabled.

cviii_virtual_scene_test_0647.c simulates a five-segment 10,000-sample
scene with two continuous song voices, three overlapping synthetic
effects, mid-scene audio slider changes and output mute. The PCM must
match exactly for blocks of 2000, 257 and 1 sample. These are invented
fixtures, **not** original music, genuine gameplay or PCM parity proof.

Both tests are wired into the Windows Alpha CMake and Linux NESRecomp
integration workflows. No original ROM, music or proprietary runtime
code is included in these fixtures.

## Next authentic-Japanese milestones

1. Acquire actual owner-local JP0646 sound decision/JP0612 request
   observations and matched independent-Mesen reference frames.
2. Decode original Japanese song and effect program semantics, sound
   register ownership, loops, frequencies, durations, envelopes and
   sample playback.
3. Produce one song and competing effects from authenticated original
   sound events; run them against this virtual mixer without forcing
   the game to use the experimental output.
4. Add safe event-queue and save/load/pause clock boundaries.
5. Only after playback and timing verification, switch Enhanced output
   to independent Music/SFX buses behind a reversible option and
   exercise real volume sliders in owner Windows game sessions.

Current completion claim is **working independent virtual PCM
infrastructure using synthetic sources**, not complete independent
Japanese-game music or effects.

User-requested modding work remains deferred until Enhanced completion.
The owner-resolved graphics issue #1 remains closed. Strict semantic
PRG 49,504/262,144 (18.8843%), VPP27/100, certified checkpoint0508,
frontier $FB96 and R-002 OPEN are unchanged. Audio investigation
R-007 remains OPEN.
