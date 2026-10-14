# JP0610 — Independent music and SFX: architecture and evidence

**Owner objective:** Music plays continuously while multiple overlapping
effects each retain their own voices, timing and tails. Enhanced should
have independently mixed Music, SFX and Master gains.

## Current sound path

Japanese mapper24 hardware has 2A03 pulse1/pulse2/triangle/noise/DMC,
plus VRC6 pulse1/pulse2/saw. Pinned NESRecomp clocks these eight
channels and outputs a single mixed mono PCM stream. Once original
game code chooses to interrupt a voice, splitting the resulting PCM
into two volume controls cannot recover the missing note or effect.

JP0533 authenticated 125 original bank0C indexed sound records and
source-addressed script roots; JP0534 authenticated the bounds of
candidate phrase pointers at $A304..$A956. Their full command
semantics, original sound request callers, and music-versus-SFX
ownership remain unproved. These cannot be guessed safely.

## JP0610 implemented: read-only hardware traffic

Private generated overlays of pinned hw_apu.c and hw_mapper.c call a
single diagnostic on original CPU writes to 2A03 $4000..$4013,
$4015/$4017 and VRC6 $9000..$9003/$A000..$A002/$B000..$B002.
All original CPU hardware effects, APU/VRC6 synthesizers, timing,
registers and PCM mixing run unchanged. The owner-local CSV includes
CPU cycle, register, previous and new value, voice and rapid changes.
A strict synthetic analyzer validates channel, delta and rewrite flags.
Rapid rewrites are only observations: a sound suppressed by the
original software before reaching the hardware will not appear.
Neither music/SFX isolation nor greater polyphony is claimed yet.

## Next sound milestones

1. Reconstruct each effect trigger/request and song selection at
   bank0C scheduler entry. Confirm real per-request ownership.
2. Decode original program notes, envelopes, durations, loop points,
   voice control and VRC6 expansion-wave programming accurately.
3. Run the music score in a virtual music set of 2A03/VRC6 voices
   unaffected by effect requests.
4. Run each triggered effect in an independently allocated host
   voice pool. No automatic hardware-channel stealing; apply a
   bounded overall software voice count and explicit lifecycle.
5. Mix virtual music + effect buses into SDL with configurable
   Music, SFX and Master volumes and an anti-clipping output stage.
6. Preserve original machine audio hardware internally for DMA,
   input-visible timing, save-state and CPU parity; once the
   virtual voices are validated, suppress duplicated original PCM
   only at the presentation boundary.
7. Compare original Japanese event timing in MesenCE. Check song
   transitions, simultaneous whip/enemy/door events, pause and
   quick-state load. A/B test before enabling new output by default.

## Private owner test for JP0610

After rebuilding the Windows private AlphaCandidate:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -StableSprites -AudioTrace

Trigger two effects together, close the native window normally.
CVIII-Audio-Registers.csv and CVIII-Audio-Registers.json remain local.
Only chip-level CPU writes are captured; a future sound-request trace
will be needed to recover effects discarded prior to hardware output.

No commercial audio or game bytes are committed to public GitHub.
Strict semantic PRG coverage remains 49,504/262,144 and VPP 27/100.
JP0609 sprite-layer logic and its successful owner tests are preserved.
