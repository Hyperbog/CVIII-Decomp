# JP0668 — Independent original-game vs native audio register captures

## JP0671 owner ORIGINAL vs native C11 result — 100% register/value ORDERED parity, *not* cycle-exact (2026-10-17)

**Significant positive original/native parity milestone.** Owner privately captured the full original Japanese ROM in Mesen2 after fixing Lua `setInput` routing, then independently validated the JP0671 Start CPU-read gate and compared against the already preserved native C11 **Original Edition** JP0614 session. **Every one of 3,401 original audio writes has the same register address and 8-bit value in the SAME order as all 3,401 native C11 writes**. No data was filtered, shifted, reordered or rebased. This supersedes the earlier 2,029 vs 3,401 failed session, whose original Mesen input calls unintentionally cleared player-one Start and the other buttons.

**Owner-private evidence/provenance:**
- Genuine original-ROM Mesen log SHA-256: `5aba434cc9bed36908ef97f63aecf0cd8a4c30b35db2aa4060e367553c3bf5f5`; original ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; corrected observer Lua SHA-256 `b44264fcd13ac15e2a81fc367b6bc3cebdb4841662da2eb55a0996d27b7adbc9`.
- Original Mesen: **1,100 frames, 1,099 observed input polls, 3,401 writes**, end CPU cycle **32,756,052**; strict JP0668-v2 frame/poll/ordering/clock-domain validation and independent JP0671 route/CPU-start validator passed. All **1,099** injected-input route checks passed. During frame 90 first Start, the fourth actual $4016 CPU read returned **$41** twice, both with Start bit 0=1. Mesen process exit remained `-1` despite explicit complete marker; process-termination normality is not separately proven.
- Native C11: **3,401 writes**, 1,100-frame scripted replay requested and native process exit 0; single `power_on` JP0614 epoch and manifest/CSV hashes independently verified. Native register CSV SHA-256 `3d4a32dd8c507119960f17e7a8104d17b492a6ff23eda4c11688eeec38b3eac3`; private diagnostic EXE SHA-256 `9039b9b8bce775249a765a2fad100b286b91168fb6defc5404503f1ab5c9d8ed`; replay SHA-256 `1ae01d6032847d2e37e151e09398c1f6f6765ed1915fe0623069d5d96d40ab3c`. Native sound-request rows: 62. **Do not** infer dropped-sound/SFX-ownership or PCM parity.
- Full address/value sequence: **3,401 of 3,401** matched. Includes **1,933 2A03** writes, **1,468 VRC6** writes and **212 DPCM descriptor ($4010–$4013)** writes in each stream. Unlike the invalid old original capture, DPCM programming is genuinely exercised and *programming values/order* match; DMA fetch/timing and resulting PCM are not attested.
- Unadjusted absolute CPU cycle parity **FAILS**: only **76/3,401** exact cycle timestamps; native-minus-Mesen write-cycle offsets range **−7 to +9 CPU cycles**, with **2,366/3,401 within ±1**, **3,180/3,401 within ±3** (93.5%), **3,347/3,401 within ±5** (98.4%), and **all 3,401 within ±9**. Of the **3,400 adjacent event intervals**, **2,710** match exactly. Earliest write cycle native 57,233 vs Mesen 57,234; final write cycle native 32,731,040 vs original 32,731,042. Offsets vary in sign; **not** explained by a single constant alignment. Existing comparator intentionally reports first strict mismatch at event 1 and refuses cycle parity certification.
- Interpretation: **fully matched ordered 2A03/VRC6 write address/value traffic for one tested deterministic scripted session**, and CPU-confirmed original Start control. **NOT** full cycle-exact parity, proven common frame-to-CPU epoch, equivalent before-write callback phase, DPCM DMA parity, PCM waveform parity, SFX polyphony, or general 1:1 game parity. **No private raw ROM/writes/session CSV are committed.**

**Next engineering investigation without another owner capture:** review the pinned NESRecomp native `hw.cycles` tap in `JP/recomp/tools/patch_cyc_audio_bus_0610.py` against Mesen's `emu.getCpuCycleCount()` during pre-write memory callbacks, to account for ±1..9 CPU-cycle event timing offsets. Preserve strict unshifted comparison and avoid classifying timestamp tolerance as a parity proof. The original game and native traces are now well matched enough to investigate timing in isolation, without sound-engine rewrites.

## JP0670 — root cause of invalid equal-input assumption; JP0671 corrective capture prepared (2026-10-17)

**JP0670 owner-private Mesen2 CPU bus/input probe completed successfully:** 113 frames, 112 polls, 384 total sampled $4016 CPU reads (96 emitted samples), 96 strobes, zero reported probe errors. Original ROM SHA-256 confirmed; raw probe SHA-256 `68e68206c548d13bcbd940f18eae84290e637237499b0727a79cdc741f941e6a` (NOT published in Git). During frame-90..92 intended Start on the first scripted `emu.setInput` call, `getInput(0).start=false` and the fourth serialized $4016 reads were `$40`; intended A similarly failed at frames 96..98. When the probe instead supplied Start through the **second** `emu.setInput` call during frames 102..104, `getInput(0).start=true`, while `getInput(1).start=false`, and the fourth $4016 bus reads became **$41 (Start bit 0=1)**. Both calls were returning success; the first controller was being overwritten.

**Implementation root cause inspected in upstream Mesen2:** `Core/Debugger/LuaApi.cpp` `LuaApi::SetInput` calls `l.ForceParamCount(3)`, `lua_settop(lua,4)` and then reads `subport=l.ReadInteger(0)` and `port=l.ReadInteger()` from the stack top. In the owner's observed test-runner build, the **third Lua argument**, nominally `subPort`, actually chooses the physical controller port, and two-argument `setInput` calls both target physical controller 1. The original JP0668 v2 observer first set pad1 with `setInput(t,0)`, then cleared pad2 with `setInput(neutral,1)`; both calls targeted pad1 and the second removed the requested Start/Right/A/B. **This is a recorder/controller-delivery bug, not evidence of a native audio-engine defect.**

The separately distributed owner-local **JP0671** observer fixes this by clearing physical controller 2 first with `emu.setInput(neutral,0,1)`, then setting physical controller 1 with `emu.setInput(actual,0,0)`. The recorder verifies `emu.getInput(0,0)` and `emu.getInput(1,0)` after **every** actual input poll and **fails closed** unless the original CPU's fourth serialized $4016 read in frame 90 contains the Start bit. It preserves the JP0668 v2 original audio event format for use with the existing native pair comparator; additional `JP0671_ROUTE`, `JP0671_CPU_START`, and `JP0671_GATE` markers certify delivery, not just intended masks. The JP0671 Python validator passed 8 synthetic corruption cases; the older non-delivering JP0668 v2 owner trace correctly fails JP0671 CPU-input-witness validation. **Owner Windows 1,100-frame JP0671 retest is pending.** Previous native C11 3,401-write trace remains valid for subsequent comparison. Do not rerun/rebuild native without a concrete separate reason; do not claim exact parity yet.

## JP0669 first Start press — original game did not receive injected Start (owner capture 2026-10-17)

The owner ran a 130-frame read-only CPU/controller witness in the original Mesen2 against the authentic Japanese ROM, using the JP0668 input-intent timing. The probe completed `JP0669_END frames=130 audio=127 polls=129 reads=512 strobes=128`, with **512 actual 2A03 CPU reads** of `$4016` and **128 actual writes** to `$4016` in the frame-84–115 observation window. The owner private log SHA-256 was `00dd8d8f0d80d4acddbfcb5fca4ea48c93fd462c8728b0071289d460ef35c797`; it is NOT published to Git.

Lua requested Start on controller port 0 at frame labels **90, 91, 92**, and requested release on frame 93. Despite those requests, `emu.getInput(0)` reported `none` during all three active callbacks, and every `$4016` read in the active-frame window returned `0x40` (bit zero clear). The game generated two controller strobe/8-read sequences per frame, so the **fourth read in each train**, where a held NES Start button should serialize a one, was also `0x40`. The CPU did **not** receive the intended Start bit. As a result, the JP0668 Mesen original log (2,029 writes) remains structurally authentic but is **NOT an equal-input gameplay reference for the native run** (3,401 writes). Do not diagnose the original sound engine or claim parity/divergence causation from these mismatched sessions.

The next owner-private diagnostic (JP0670) probes controller availability with `emu.getInput(0,0)` and `(1,0)`, enumerates returned table fields, checks `pcall(emu.setInput, ...)` results, and observes actual first/fourth CPU `$4016` bits for short separate Start/A input windows. It distinguishes absent controller, ineffective API injection and overwritten input. No further native rebuild or full 1,100-frame Mesen capture is warranted until this input source is fixed.

## Owner live cross-capture verdict — FAILED strict parity, 2026-10-17

Both private captures exist; **no private raw register events, proprietary ROM, compiled executable, or audio assets are published**. Reference Mesen2: 1,100 frames and 2,029 original register writes. Newly rebuilt native C11 Original Edition (separate diagnostic EXE SHA-256 `9039b9b8bce775249a765a2fad100b286b91168fb6defc5404503f1ab5c9d8ed`): requested 1,100 frames, completed with process exit code 0, generated 3,401 audio writes and 62 sound-request entries. The native `CVIII-Audio-Session.json` SHA manifest matched all three CSVs, and JP0614 session verification reported **one `power_on` epoch** and complete 3,401/62 rows. Native CSV SHA-256 `3d4a32dd8c507119960f17e7a8104d17b492a6ff23eda4c11688eeec38b3eac3`; Mesen2 owner log SHA-256 `fa09b1a4333ebc642e3099fc9bb6a3397ac115c61c8fe54f251afa2fe94924b3`.

The owner-private **v2-aware comparator was executed against the actual files**, validating the Mesen2 1,100-frame log, the native CSV, the immutable JP0551-derived input replay and the native session hashes/one-epoch boundary. **First strict mismatch: write 1, CPU cycle off by one** (exact unshifted parity fails). **First address/value mismatch: write 85**, around native frame 92 vs original Mesen frame 95. The first **84** writes have the same ordered address/value pairs but cycle offsets vary among -3/-1/+1/+3 (native minus Mesen, not a legitimate single offset). Overall 2,029 vs 3,401 writes strongly diverge. Native logs 212 `$4010–$4013` DPCM descriptor writes while original logs **zero** in the captured session. **No silence/failure of original audio is inferred from DPCM absence; this is different execution/session content, not yet a sound-engine-root-cause diagnosis.**

The first substantive divergence occurs shortly after the first scripted Start press near frame 90. **Input-mask records in the Mesen Lua script prove only the intended injection, NOT that the original CPU latched identical controller bits to the native replay.** The native run log confirms that 26 replay transitions loaded, but likewise does not contain a CPU-side controller-read witness. Next diagnostic `JP0669-Mesen-Controller-Read-Probe.ps1` is a short owner-private 130-frame targeted original-Mesen test logging actual CPU reads/writes at `$4016` and applied controller state near the first Start press. Do not reclassify any 2,029/3,401 difference as a sound engine defect until actual input sampling and CPU-cycle origin/write-callback phase are compared. No cycle-rebasing or stream realignment is allowed when certifying parity.

The native launcher PowerShell stderr workaround (commit `3d558353`) was effective: although the pinned runtime still printed nonfatal `[mods]` stderr, the native wrapper preserved exit code 0 and produced the JP0614 four-file session. Both original and native audio logs remain private.

## Native owner test — installed executable mismatch (2026-10-17)

The first native run rejected a missing replay option in the installed launcher. Replacing only the owner-local launcher allowed the capture runner to start, but the installed private game executable then rejected `--audio-reg-trace` as an unknown argument. These are **two separate version mismatches**, not an actual register-event divergence. The owner ROM and deterministic input replay SHA checks succeeded. The original Mesen2 1,100-frame reference remains valid; native comparison has **zero qualifying registered events** until a trace-capable binary is built.

**Important build-source trap:** `JP/recomp/release/alpha/Build-Alpha.ps1` defaults to pulling the older `decompilation` branch when no `-ProjectRoot` is supplied. A standard rebuild therefore does *not* guarantee the JP0668 PR instrumentation is present. The owner-facing helper `JP0668-Build-And-Capture.ps1` (distributed separately, not committed with any private ROM, executable or events) clones `jp0664-famistudio-reference`, checks out source commit `cd67bb225dbe9b969489a46ac93498b973d96689` into a separate clean source tree, then calls the branch builder with an **explicit** `-ProjectRoot`, a unique private `-OutDir`, and the existing JP0668 native input/audio runner. It does not replace the working AlphaCandidate, saves or original reference. Windows execution of this new helper is still pending.

## Owner-observed original Japanese Mesen2 run — v2 (2026-10-17)

**LIVE ORIGINAL Mesen2 trace obtained and independently validated from owner-uploaded private files.** The original remains owner-private and is never committed. This corrects the older v1 tool assumptions and historical status below; no native comparison run has yet been received.

- Original retail Japanese ROM: SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, independently checked against owner ROM.
- Owner Mesen binary SHA-256 `8ef403d6b9af32075416193914d7993ce8480b347fe1f20a0cfd9815374933e7`. Source of executable bytes remains owner-private.
- Executed v2 Lua observer SHA-256 `f2855b678957882107bf4eeb382d54c363588a36559042f246edee0db2a9af39`; owner log SHA-256 `fa09b1a4333ebc642e3099fc9bb6a3397ac115c61c8fe54f251afa2fe94924b3`. Neither log nor copyrighted original register values are present in Git.
- Real original Mesen2 callback support established: `emu.getCpuCycleCount()`, flat `state["cpu.cycleCount"]`, hardware-write callbacks, frame and controller poll callbacks. The earlier nested `state.cpu.cycleCount`, `emu.log` redirected-to-stdout, reset-callback-at-start and one-poll-per-frame assumptions are wrong for this owner build.
- Observed original v2 results: `JP0668_BEGIN` at CPU cycle **7**; **1,100 / 1,100 continuous end-frame callbacks**, **1,099 actual controller polls** (frame-1 poll is absent; each remaining poll labels its upcoming frame), **2,029 original hardware register writes**, final CPU cycle **32,756,049**. Consecutive NTSC frame-cycle deltas are 29,780 cycles (548) and 29,781 cycles (551). Native zero-based input schedule is intended to match these observed masks, but cannot prove actual native input sampling until its own capture is obtained.
- VRC6 register writes: **1,320**; 2A03 `$4000–$4013` writes: **705**; `$4015/$4017` writes: **4**. **No `$4010–$4013` DPCM descriptor write occurred in the captured 1,100 frames**. Do not claim DPCM register or DMA parity from this test.
- The v2 original-capture parser from the owner-private JP0668 v2 kit and its **eight synthetic corrupt-case tests passed locally**. Real log has no invalid/truncated markers; counts, ordering, cycle monotonicity, input masks and END record all pass. Emulator returned **exit code -1** despite a completed end marker, so independent process-exit normality is NOT certified; trace structural acceptance does not imply correct emulator shutdown.
- Boot attach at cycle 7 is compatible with an early original-ROM testRunner session, but does not independently prove identical power-on boundary to the compiled C11 Alpha. Music-program selection, exact original *Beginning* liveness, SFX ownership, and full register/CPU-cycle/PCM parity are NOT inferred.

**Required next:** run privately compiled **Original Edition** Alpha using the same 1,100-frame replay with `-AudioTrace -InputReplayPath <path> -ExitAfterFrames 1100`, capture all three original JP0614 session CSVs plus session JSON, retain compiled EXE/launcher hashes, then use a **v2-aware** (not the older v1-only) pair checker to compare unshifted register address/value/order/cycles. Do not turn on independent audio or promote R-007 based on the source-only trace.

## Owner recovery result — genuine private binary built, native stderr interrupted launcher (2026-10-17)

Owner's separate pinned `cd67bb2` build **compiled successfully** and generated executable SHA-256 `9039b9b8bce775249a765a2fad100b286b91168fb6defc5404503f1ab5c9d8ed`; 29 helper files were restored to the isolated diagnostic AlphaCandidate after packaging path repair (`b71d07f`). No audio CSVs were collected. The exact native capture failure in the uploaded private run was the NESRecomp stderr line `[mods] this program is built without mod support; .../mods is not read`.

Pinned upstream `runner/cyc/cyc_session.c` actually **returns true** after this informational stderr message when mod support is compiled out, so it is not evidence of failed emulator startup. The Alpha PowerShell wrapper's global `$ErrorActionPreference='Stop'` can promote stderr to a terminating `NativeCommandError` before writing the JP0614 manifest. The source launcher fix (commit `3d558353`) temporarily applies `Continue` **only during native execution**, restores the previous preference and enforces the process's numeric `$LASTEXITCODE`. This does not suppress or forgive a nonzero program exit. A separate owner-private patch-and-capture helper applies only this narrow edit to the existing diagnostic launcher after authenticating its old SHA-256, ROM/replay/executable SHA values, and backing it up. **Windows capture retest pending.** Original-Mesen reference 2,029 writes unchanged; cross-CPU-cycle parity still NOT VERIFIED.

### Historical v1 plan (superseded for Mesen capture protocol)

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
 --repo-root /private/CVIII-Decomp \
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