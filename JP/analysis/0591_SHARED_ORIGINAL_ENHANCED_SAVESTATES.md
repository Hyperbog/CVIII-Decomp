# JP 0591 — Shared Original/Enhanced 10-slot save states

**Existing feature:** NESRecomp already saves/restores the **complete
emulated game machine** using cyc_state_save_file/load_file:
CPU, RAM, cartridge VRC6 registers and work RAM, PPU, APU, picture,
hardware/trace state and frame counter. The Windows Alpha already
supports **F8 Quick Save** and **F9 Quick Load** in its original single
slot. The snapshot is validated against the compiled program identity
and structure; incompatible ROMs/builds are rejected. No new bespoke
serializers are introduced.

**New feature (for a freshly built windowed version):** the repo's
CMake target now uses JP/tools/patch_cyc_savestates_0591.py to derive a
**private** patched copy of the pinned external NESRecomp SDL host.
The copy lives next to the **external** cyc_sdl.c, retaining relative
includes and leaving the upstream licensed original unmodified.
CMake replaces exactly one SDL host compilation unit; mismatched
upstream source anchors stop the build rather than risk corruption.

- **Ctrl+0–9:** select save slot with an on-screen confirmation.
- **F8:** save the selected slot.
- **F9:** load the selected slot (retaining the normal host frame-count
  reset and session state-loaded callbacks).
- **Slot 0** preserves the Alpha's original unnumbered filename
  (`saves/<ROM name>.cycstate`). Slots 1–9 are
  `saves/<ROM name>.slotN.cycstate`, **not** a different save system.
- Both editions share slots. Enhanced rendering/audio preferences
  belong in config.ini, not in emulated machine state, so the same
  binary's save slots can be loaded with either edition selected.
- On successful load the host resets the cycle frame count and
  notifies the original game session; it does not attempt a partial
  CPU-only restoration.
- Netplay restrictions are inherited from upstream.
- For headless testing upstream `--save-state F:FILE` and
  `--load-state FILE` remain unchanged.

**Compatibility caveat:** NESRecomp ties save-state acceptance to
the original game program identity and machine structure sizes. A
state from the owner's already distributed Alpha might not load in
a later build. This mechanism does **not** guarantee cross-version
state migration. It does ensure slot0 isn't deliberately renamed.

**Tests:** synthetic code/anchor contract plus real pinned external
upstream source patch generation run in CI. Windowed SDL compilation
and real owner user-interface playtest are a separate release gate;
this phase is not advertised as a new playable Alpha package yet.
Do not run full ROM reconstruction for this host-only change.
No VPP, PRG or decompilation score changes.
