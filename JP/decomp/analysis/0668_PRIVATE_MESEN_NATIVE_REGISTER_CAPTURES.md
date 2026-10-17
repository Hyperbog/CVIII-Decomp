# JP0668 — Independent original-game vs native audio register captures

**Status (2026-10-17): Capture tooling completed and synthetic tests passed; actual private Mesen2 and compiled C11 Alpha executables are not present in this environment, so no original/native gameplay trace and NO CPU-cycle parity verdict exists.**

This set never contains or writes ROM, NSF, FamiStudio notes, compiled commercial game, PCM, or raw game audio events to GitHub. The owner-provided source ROM SHA-256 is `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. All capture artifacts stay outside the repo.

## Verification improvements

- New original Mesen2 Lua hook captures exactly the register domains of JP0610 with CPU cycle count, monotonically numbered writes, 1,100 end-frame markers, one deterministic input mask per frame, strict epoch boundaries and explicit completion/truncation. Read-only apart from NES pad 1/2 input override.
- Deterministic input schedule is taken from existing project `mesen_windows_state13_0551.lua`, frames 1–1100. The generator shifts to the pinned NESRecomp **zero-based** `--window-input` notation: `F A+B`, `F -` to release. This conversion is specifically grounded in pinned upstream NESRecomp `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`, `runner/cyc/cyc_host.c` (`input_tick(frame)` before frame execution) and Mesen callback `inputPolled`.
- `Launch-Alpha.ps1` can now accept optional `-InputReplayPath` and `-ExitAfterFrames 1100` alongside `-AudioTrace -Edition Original`. Normal gameplay is unmodified and all options default off.
- Original trace requires READY, reset, **1,100 continuous frames / input polls**, STOP/END, exact sequence/order and monotonic cycle counts. Rejects state-load/save, callback failure, incomplete/truncated logs or altered input schedule.
- Native CSV requires exact JP0610 field schema and per-register previous/delta/rapid rewrite internal consistency. It rejects 200,000+ rows; native instrumentation's one-million row hard cap cannot silently certify partial results under this cap.
- Requires existing **JP0614 native** three-file session verifier (`CVIII-Audio-Session.json`, `CVIII-Audio-Epochs.csv`, `CVIII-Sound-Requests.csv`, `CVIII-Audio-Registers.csv`) to certify one power-on epoch and matching file digests. Rejects savestates.
- Uses a separate owner-local evidence manifest with SHA-256 of original Mesen executable, native compiled executable, Mesen Lua, input replay, both logs and native JP0614 epoch files. **Manual** same-input, CPU-cycle-origin and write-phase checks remain prerequisites; a boolean declaration cannot turn a synthetic trace into real observed gameplay.
- On a divergent sequence, fails with first offending index and recorded cycles; **never** auto-shifts cycles or skips mismatching register writes.

## Preflight (available here, ROM-free)

```sh
python3 jp0668_input_replay.py --smoke
python3 jp0668_capture_pair.py --smoke
python3 jp0668_input_replay.py --out JP0668-window-input.txt
```

The private script is `mesen_jp_audio_capture_0668.lua`; it logs `JP0668_` records to the original Mesen2 log. Its Lua Mesen2 API contract comes from the Mesen2 `LuaDocumentation.json`: `addMemoryCallback` write triggers **before** the write, `getState` fields are version-specific, `eventType.inputPolled` is once/frame, and `emu.stop` ends the test-runner. **This Lua capture remains unexercised** without the independently approved binary; on a missing `cpu.cycleCount`, it emits `JP0668_INVALID` and refuses certification.

### Original Mesen2 capture, owner's Windows PC

Use the exact original Japanese ROM. Load the Lua observer **before cold-booting/resetting**; ensure `JP0668_BOUNDARY reset` is present once, and no savestate/load is used. In the Mesen2 script log, retain all `JP0668_` lines, including READY, reset, INPUT, WRITE, FRAME, END. The script stops after 1,100 frames using `emu.stop(0)` (headless `--testRunner` supported by Mesen2). A fresh profile with NTSC enabled and no other input overrides is needed; any failure to obtain a reset callback is a **blocking issue**, not something to paper over with an artificial reset marker. A full power cycle must be confirmed separately from an ordinary soft reset.

Run its executable under a path whose SHA-256 you record. For example, Mesen2's documented test runner uses this CLI structure, subject to checking the exact installed build:

```powershell
& 'C:\Tools\Mesen2\Mesen.exe' --testRunner 'C:\Private\mesen_jp_audio_capture_0668.lua' 'C:\Private\Akumajou Densetsu (Japan).nes' -enableStdout -noaudio -novideo > 'C:\Private\JP0668-Mesen.log'
```

**Not executed here**; the binary may require syntax/platform adjustments. Do not infer a reset event occurred just because the CLI returned 0.

### Native private C11 capture, owner's Windows PC

Rebuild private AlphaCandidate from PR branch, retaining the original-owner ROM. Generate the exact replay text above. Then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 `
 -Rom 'C:\Private\Akumajou Densetsu (Japan).nes' `
 -Edition Original -AudioTrace -AuditOutDir 'C:\Private\jp0668-native' `
 -InputReplayPath 'C:\Private\JP0668-window-input.txt' -ExitAfterFrames 1100
```

`-AudioTrace` activates the native audio register and request traces, and JP0614 session manifest+epoch integrity check. `--window-input` is supported by the pinned upstream native core and the new optional wrapper. Do not interact with the native game during replay. Verify startup, audio observer and actual power-on in the generated private diagnostic logs.

### Capture-pair verdict

First prepare a private manifest containing hashes (attestation flags default false):

```sh
python3 jp0668_make_manifest.py \
 --rom /private/original-jp.nes \
 --mesen-exe /private/Mesen.exe --native-exe /private/AlphaCandidate/CVIII.exe \
 --mesen-log /private/JP0668-Mesen.log --native-dir /private/jp0668-native \
 --input-replay /private/JP0668-window-input.txt \
 --out /private/JP0668-capture-manifest.json
```

Do not change `same_replay_verified`, `shared_cpu_cycle_origin_verified` or `write_callback_phase_verified` to `true` without corroborating their meanings: identical scripted inputs (including zero/one-based frame relationship and no extra physical inputs), matching power-on/region state and alignment of Mesen write-before CPU bus events with native cycle timestamps. The following comparison **will fail closed** while those gates remain false:

```sh
python3 jp0668_capture_pair.py \
 --original-rom /private/original-jp.nes \
 --mesen-log /private/JP0668-Mesen.log \
 --native-csv /private/jp0668-native/CVIII-Audio-Registers.csv \
 --native-audio-dir /private/jp0668-native \
 --input-replay /private/JP0668-window-input.txt \
 --manifest /private/JP0668-capture-manifest.json \
 --json /private/JP0668-aggregate-verdict.json
```

If the clocks differ, report the first mismatch. Do not shift the entire sequence to force success; debug reset origins and write callback phase first. The verdict only checks CPU register **write intents**; DMC DMA fetch cycles, PCM, volume effects, SFX that never reached hardware, and native independently mixed audio remain unproved.

## This environment's verified result

- JP0668 input replay smoke: PASS (1,100-frame source-consistent masks; four corrupt cases rejected).
- JP0668 register trace parser smoke: PASS (three synthetic matched register events; fourteen corrupt cases rejected, plus original ROM identity guard).
- `python3 -m py_compile` for all three Python tools: PASS.
- **Original Mesen2 game execution: unavailable.** Native game build executable: unavailable. Live captures: zero. Real CPU-cycle parity: NOT TESTED.