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
