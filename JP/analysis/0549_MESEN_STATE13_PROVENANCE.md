# 0549 — Passive Mesen original-state provenance and automatic build authorization

## Objective and evidence boundary

Connect the *existing, original-ROM-playable* 0508 Mesen2 reference route to the 0547/0548 reconstructed scheduler without injecting game RAM `$18=0D`. Report writes to `$18`, execution of fixed-bank `$E35C` and `$E526`, and the bank-qualified entry of room routines `$B873`/`$B7F7`. This is an original-emulator **instrumentation and audit gate**, not a claim that state 13 or an entire playable native frame has been observed.

- Original Japanese iNES SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- Source witness: 0508 1,100-frame Mesen2 route in `JP/SharedNES/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE.md`; earlier sampled `$18` values did **not** include `$0D`.
- New Lua script: `JP/tools/mesen_0549_state13_provenance.lua` logs live RAM writes and execution callbacks without changing CPU memory or input; `emu.convertAddress` qualifies banked code by physical PRG offset.
- **No new Mesen frames were captured in the development environment for this checkpoint:** the pinned emulator executable and core are not installed here. No live entry, reset-to-state-13 progression, or frame parity is claimed.
- 0548 original-6502 reset/NMI path: original ROM plus explicitly scripted PPU/NMI inputs; this remains separate from the original Mesen gameplay witness.

## Run against original ROM and Mesen build

Install or supply the original verified `mesen-agent v0.1.0` executable and `MesenCore.so` from the 0508 reference. The executable and original ROM **must remain local/private**; the runner authenticates all three SHA-256 values.

```bash
bash JP/tools/run_mesen_state13_0549.sh \
  "$ORIGINAL_JP_ROM" "$MESEN_AGENT_DIR" /tmp/mesen0549_private
```

The script reproduces the same 520+220+360 frame title/name-entry/prayer/Stage-1 input route as 0508, with three linked Mesen savestates and separate emulator homes. It writes full private logs and `state13_evidence.json` to the given private output folder.

The evidence validator rejects incomplete runs, Lua callback errors, missing frames, unexpected runtime instrumented addresses, truncation, unauthenticated binaries, and disconnected savestate frame ranges. A logged CPU address alone does not qualify a room-code hit because other VRC6 banks can be mapped to `$B873`/`$B7F7`. `physical_prg_offset` is checked against the canonical bank `$0A` and fixed bank 31 positions.

**ROM-free CI:**

```bash
python3 JP/tools/test_mesen_state13_0549.py
python3 JP/tools/test_reset_0548.py
```

The ROM-free tests use *explicit synthetic JSONL fixtures*, never count them as original gameplay, and include tampering cases for physical-ROM offsets, run counts, truncation, and Lua failures. Authenticated original-ROM regression still works with `python3 JP/tools/test_reset_0548.py --rom "$ORIGINAL_JP_ROM"`.

## Current unanswered question

No natural `$18=0D` transition or `$E526` execution in state 13 has been captured by this new logger yet. The test does not fabricate one. Once real Mesen logs are available, compare any actual `$E526` entry (and bank `$0A` room code) to the compiled 0546/0547 native counterpart, without an injected selector. If 1,100 frames never reach state 13, preserve that negative result and extend real input routes, not synthetic IRQs.

## Build policy

Both connected repositories are public as of this checkpoint. Manual owner-authorization for initiating build/tests is lifted at the user's express request. ROM-free CI can run automatically on push and via workflow dispatch. This permission change does **not** authorize committing original commercial game media or relabeling source smoke tests as gameplay parity.

## Hosted CI limitation

The preceding 0548 GitHub Actions run `38192909220` has a failed job with no step summaries and its job-log endpoint returns `BlobNotFound`. There is no supported root-cause diagnosis. New CI runs must be reported according to their actual conclusion, not assumed green because local tests pass.
