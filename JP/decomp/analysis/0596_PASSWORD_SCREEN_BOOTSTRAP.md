# JP 0596 — One-password-screen native stage bootstrap

The Japanese retail ROM's password handler is at mapper24 PRG bank 03
CPU $B531, with its decode call at $B548 (JSR $B886). Decoder $B886
calls the original name hash at $B8F8 and reads original password
input cells via $0790,Y. Name hash reads $07F8..$07FF; decoded
checkpoint is RAM $0030. Native Windows synthetic builds do not use
the retail cartridge, so static ROM evidence plus table-byte identity
do **not** constitute a complete end-to-end emulation acceptance test.

## Functional design

- F10 / F6 while the actual game's password-entry mode $0019==08:
  capture the complete native machine, including correct player name.
- F10 Up/Down: one of the 18 original save-point checkpoints.
- F10 Left/Right: None, Alucard, Sypha or Grant.
- F10 Tab: Normal/Hard; original route validity for Normal.
- F10 Enter: load existing stage-specific checkpoint if present.
  Otherwise back up the running machine, restore password-screen state,
  calculate its name hash and the original stage/partner/mode password,
  then fill all 16 authentic packed $0790..$079F input bytes.
- Close F10 and **confirm on the game's ordinary password screen**.
  Its actual code will validate the password and initialize stage/route.
  No direct control-flow jump or synthetic PPU state is performed.
- If restored state is not password-entry or any RAM write fails,
  restore the full previous machine and report error; disabled netplay
  uses the upstream state loader restrictions.

The password checksum, scrambled symbol locations, name-hash seeds,
selector/leader bytes, and normal partner-availability bits are grounded
in the authenticated original Japanese mapper24 ROM. Generated C host
code is development-only. No copyrighted game code or compiled ROM
program is committed; original gameplay semantics remain unchanged
when the debug feature is inactive. Stage UI labels are hypotheses
from related documented Castlevania III password routes until all are
confirmed through JP play.

## Evidence gates

JP0596 patch smoke proves pinned host interface anchors, build gating
requires a real SDL2 Windows C11 target and synthetic mapper24 smoke;
**independent Japanese retail acceptance and game-screen presentation
are not yet proven**. Original/new Enhanced modes and natural password
play remain the existing source of truth. Strict PRG 49,504/262,144,
VPP 27/100, checkpoint 0508 and PRG31 FB96 frontier unchanged.
