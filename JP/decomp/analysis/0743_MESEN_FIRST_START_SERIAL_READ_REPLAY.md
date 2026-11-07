# JP0743 — MesenCE first START interval replay investigation

**Observed result:** Original ROM re-execution is functional but still does **not** match original recorded RAM at local frame 416; therefore there is no admissible original-vs-native first incorrect CPU writer yet. No game code patched.

## Input evidence

- Archived original JP0718 local input frames **393–398** record controller 1 mask **0x10**, converted in the earlier authenticated JP0719 native schedule to **START**, with release at local **399**.
- At local frame 393, MesenCE `InputPolled` callback in newly replayed emulator occurred at exact archived absolute input frame 394 CPU cycle **11,701,349**.
- The new Lua probe used `emu.setInput({start=true}, 0)` for that interval, and `emu.getInput(0)` immediately after the setter confirmed `start=true`.
- Independently recorded CPU bus reads of $4016 during local frame **393**:
  `40 40 40 41 40 40 40 40 | 40 40 40 41 40 40 40 40`. That has bit 0 set on the fourth serial read of each group, matching the NES START read slot (separate high/open-bus bits masked off). Frame 394 reproduces the same 16-read pattern. Thus the button is delivered to the emulated 6502 serial controller bus; the failure is not simply a missing Lua setInput invocation.
- Replays injecting identical historical input at `InputPolled`, `startFrame`, or the $4016 write callback produced the same sampled RAM and CPU-cycle values at 264, 392–400, 416, 450 and 500 in these probes. This does not prove all versions' controller bus timing identical, but a one-event callback relocation does **not** recover the old gameplay.

## First failing historical checkpoint

| Local frame | Historical original JP0718 | New MesenCE replay |
| --- | --- | --- |
| 24 | CPU 742,011; selected RAM fields agree | CPU 742,011; selected RAM fields agree |
| 264 | CPU 7,889,331; selected RAM fields agree | CPU 7,889,331; selected RAM fields agree |
| 416 | CPU **12,415,968**; RAM $19=**04**, player Y $041C=**AC** | CPU **12,415,967**; RAM $19=**01**, player Y $041C=**A0** |

Historical frames 392–400 were *not* present as exact original RAM snapshots, so a first incorrect **write** within them is not proved. The saved controller-log poll cycle sequence agrees at the start of the START interval; the bus read phase from the original historical run is absent.

## Internal execution environment

New original replay probe ran with the recovered official MesenCE Linux NativeAOT build, `--testRunner`, `--debug.scriptWindow.allowIoOsAccess=true`, and the retail JP Mapper24 ROM. The private replay generated real internal controller bus read observations but not a historical-source reference bus trace. Input is injected only in the local environment; it is **not** committed.

**Next causal gate:** compare original MesenCE build version / emulation settings, controller mapping and console selection with historical JP0718 capture metadata, and inspect the original RAM bank and game-state producers immediately following serial START reads around local frame 393, before treating a frame shift as an input fix. Source and newly replayed emulator were not proven configuration-identical.

The already completed native JP0742 mapped-instruction trace remains valid as a native run but cannot be admitted as original/native instruction parity until the independently replayed source hits all historical RAM/cycle anchors.

**Certification unchanged:** VPP 31/100; 49,504/262,144 strict PRG bytes. Last owner-tested checkpoint remains JP0722.
