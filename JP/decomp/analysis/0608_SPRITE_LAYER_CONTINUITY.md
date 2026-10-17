# JP0608 — Independent PC sprite history layer

The owner confirmed that -UnlimitedSprites did not stop Trevor/torch
and doorway flicker in the retail Japanese Windows port. The pinned
NESRecomp compositor already draws all currently OAM-present entries;
its frame-end OAM/CHR snapshots cannot restore game-omitted objects
or represent every mid-frame CHR register update.

JP0608 adds an opt-in single-frame sprite-history compositor:
* Capture color-index pixels of all valid OAM 8x8/8x16 entries at frame end
* Draw each sprite in its own transparent host-only presentation layer
* Keep an unmatched previous sprite piece for one additional frame
* Respect NES OAM priority, background mask, left-edge clipping and display flags
* Expire history immediately, clear on power and state loads, and inhibit
  ghosts after a substantial scene-related drop in sprite population

The -StableSprites option is independent of -UnlimitedSprites and
defaults off. This experimental feature can produce transient ghosts
if animation/ordering changes fool the matching heuristic, and cannot
recreate sprites never emitted to OAM or correctly track all raster
CHR/palette changes. No gameplay behavior or PPU simulation changes.

ROM-free C11 tests cover priorities, transparency, one-frame dropout
repair, left clipping, large scene change, and state reset. Actual
retail-JP Stage 1 and doorway scene tests remain necessary.

Shared Stage A-01 tile corruption remains a separate open problem.
PRG 49,504/262,144 and VPP27/100 are unchanged.


## JP0609 — Stabilize sprite priority using original PRG26 object order

The original Japanese PRG26 NMI sprite renderer advances $22 by
$44 (17 hardware OAM slots) each frame, then places emitted sprites
at consecutive byte positions spaced by $C4 (-15 physical slots).
Because the NES gives lower physical OAM slots higher priority,
two overlapping pieces can repeatedly exchange foreground/background
priority even when neither is missing. Increasing OAM capacity or
holding last-frame sprite pixels does not remove that priority swap.

JP0609 changes only the optional Enhanced -StableSprites compositor:
it reverses the original physical OAM permutation, draws sprites in
stable logical emission order, then overlays current sprites above
any one-frame rescued pieces. There are NO changes to NES OAM, IRQ,
DMA, sprite zero, CPU state, collisions or gameplay. This is a
hypothesis-driven change, with a synthetic reproducer but NOT yet
a proven retail-JP Trevor/torch fix.

An optional -SpriteTrace captures read-only per-frame $0400-$04C3
game-object arrays and actual 64 PPU OAM slots. The tracer and
analyzer can show whether physical priority swaps while logical
order remains stable, or whether the game drops sprite entries.
The report files are CVIII-Sprite-Objects.csv and .json, private.

After building the newest private Windows AlphaCandidate, run:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -StableSprites -SpriteTrace

Play the first village torch overlap for 5-10 seconds, close the game.
Compare against the same scene with -StableSprites omitted. The
original known A-01 background corruption is a SEPARATE issue.
No HD art, widescreen, gameplay changes or public Original edition
is included in this milestone.
