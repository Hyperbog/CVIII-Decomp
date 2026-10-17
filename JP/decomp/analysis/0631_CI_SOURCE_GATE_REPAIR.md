# JP0631 — Repair reproducible native regression and pinned SDL patch-source gates

**Scope:** test/patcher contract repair only. No game ROM, mapper, guest CPU, PPU, save-state representation or progression logic changed.

1. `test_nesrecomp_cycle_0568.py` had an outdated assumption that
   `-DJP_CYCLE_HEADLESS=ON` was the final argument. The actual adapter
   includes a required final `-DJP_PPU_IMPLEMENTATION=LLE` switch.
   The updated test checks unique HEADLESS and PPU arguments, explicit
   HLE, and rejection of unsupported backends.
2. `patch_cyc_audio_menu_0620.py` searched an unanchored eight-space
   substring `        open = menu_open() || cviii_stage_open;`.
   Its JP0594 predecessor inserts both a deeply-indented nested
   assignment and a later eight-space host-loop assignment, so the
   JP0620 unique-anchor check rejected correct pinned source. The
   corrected needle begins with a newline and preserves the newline
   in its replacement. It still fails closed on missing/duplicated
   full-line host-loop assignments; no source identity gates changed.

These faults were observed in JP0630-head GitHub Actions
native-regression run 38826112351 and alpha/cycle runs 38826112366 /
38826112369. The revisions are source-level maintenance; fresh CI
must determine whether subsequent tests pass, and cannot substitute
for authentic Mesen gameplay or CPU/PPU/VRC6 replay.

**Certification:** strict semantic PRG 49,504/262,144 (18.8843%),
VPP 27/100; checkpoint 0508; frontier FB96; R-002 OPEN.
