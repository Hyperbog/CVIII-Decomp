# JP 0576 — verify our actual NESRecomp C11 build wrapper end-to-end

Prior public synthetic mapper24 integration CI built upstream NESRecomp's
example project `runner/cyc/project`, not the actual original-JP
integration wrapper `JP/native/nesrecomp_cycle/CMakeLists.txt`.
Consequently upstream VRC6 compilation did not establish that our
retail-game CMake target was correctly wired.

The wrapper now has a **default-off**
`JP_CYCLE_SYNTHETIC_MEDIA` switch, with an exact-cartridge policy:
- Default: only authenticate original Japanese mapper24 ROM's
  SHA-256 and iNES shape.
- Test switch ON: accept either the exact original or the
  *byte-for-byte generated* 0569 synthetic fixture. Any altered
  fixture is rejected even if the header and vectors remain valid.

The new `tools/validate_cycle_media_0576.py` implements the gate.
The pinned external CI now configures
`cmake -S JP/native/nesrecomp_cycle` using its real
`nesrecomp_add_cycle_game(jp_akumajou_densetsu ...)` target,
compiles it, and executes `jp_akumajou_densetsu` for exactly
three artificial VRC6 frames. CI requires ≥99% native cycles
and zero ROM/RAM interpreter fallbacks using 0571's parser.

The commercial JP original remains private and never runs in
public CI. A synthetic-only integration build demonstrates that
our CMake wrapper links successfully, **not** that the real
Castlevania III title is playable or matches its original hardware.
VPP27/100; strict PRG49,504/262,144; original compiled starts4,261.
