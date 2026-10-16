# JP0637 — Six-stage F4 slot-picker source gate whitespace correction

The exact pinned JP0621 four-stage source checks and JP0623 five-stage
source verification now pass after JP0636. GitHub Actions 38828682463
and 38828682579 then failed in JP0625's six-stage gate because the
source checker searched for `if(sc==SDL_SCANCODE_F4)`, but the
authentic JP0623 F4 handler spells this `if (sc==SDL_SCANCODE_F4) {`.
JP0625 injects its slot handler after that F4 clause; its child
Escape branch still precedes the parent Escape clause.

JP0637 changes only the checked F4 substring to match the
existing original patch source and adds a ROM-free ordering fixture.
The physical upstream SDL blob pin, patched C, event ordering,
save-slot serialization and gameplay inputs are not changed. Full
six/seven-layer pinned-source GitHub CI and owner Windows SDL
execution still require separate confirmation.

No original PRG source bytes, emulator-trace parity, VPP score or
R-002 producer liveness are advanced: 49,504 / 262,144,
VPP 27/100, checkpoint 0508, fixed frontier $FB96.
