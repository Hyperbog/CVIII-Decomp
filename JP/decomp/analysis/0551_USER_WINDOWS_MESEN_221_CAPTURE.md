# Checkpoint 0551 — User-provided Windows Mesen 2.2.1 original-game capture kit

## Machine/binary evidence

- Original uploaded file: `Mesen_2.2.1_Windows.zip` — ZIP containing a single PE executable, `Mesen.exe`.
- Uploaded ZIP SHA-256: `c19e10b3b3865eb0e86e4d01bf09a5027a4452081c04b5bd5b6cbbf76e346fd6`.
- Extracted PE SHA-256: `8ef403d6b9af32075416193914d7993ce8480b347fe1f20a0cfd9815374933e7`, size 70,753,792 bytes.
- Authenticated original JP ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- Current analysis runtime is Linux and has no Wine/.NET; **the uploaded Windows binary was not executed**. It is hashed and structurally inspected, but its release provenance and behavior have not been independently authenticated against an official build.
- Official upstream Mesen2 source documents CLI `--testRunner [lua] [rom]`, `--enableStdout` and `--timeout=...`, plus `emu.addMemoryCallback`, `emu.convertAddress`, `emu.setInput` and `emu.eventType.inputPolled`.
- The native Mesen Windows stdout format **is not** the `mesen-agent` JSONL format used in checkpoints 0549/0550. They are kept separate.

## Deliverables

- `JP/decomp/tools/mesen_windows_state13_0551.lua`: passive original CPU/RAM/mapper read observer, with deterministic controller input emulation over **1,100 continuous original emulator frames** (the documented 0508 520+220+360 input schedule). No writes to original ROM/RAM/PC; only controller input is supplied via `emu.setInput`. Every frame is logged, as are state `$18` writes, fixed `$E35C/$E526` entries and physical-bank-checked `$B873/$B7F7` entries.
- `JP/decomp/tools/run_mesen_windows_0551.ps1`: Windows PowerShell runner. Validates the exact supplied ZIP, exact extracted EXE, and original Japanese ROM; runs Mesen2's native headless test interface; refuses a result if the process exits unsuccessfully or the 1,100-frame proof is incomplete.
- `JP/decomp/tools/audit_mesen_windows_0551.py`: self-contained Windows-native stdout auditor that requires precise Lua event boundaries and all 1,100 consecutive frames, verifies qualified physical PRG offsets, and reports any natural `$18=$0D`/`$E526` observation separately from RAM frame samples.
- `JP/decomp/tools/test_mesen_windows_0551.py`: ROM-free contract and corruption tests. **Synthetic positives are not certified gameplay evidence.**

## Run on Windows

1. Place the user's **unmodified** Mesen ZIP and original Japanese ROM in a private working directory; do not upload either to public GitHub CI.
2. From the repository `JP/decomp/tools` folder, run PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_mesen_windows_0551.ps1 `
  -MesenZip 'C:\path\Mesen_2.2.1_Windows.zip' `
  -OriginalRom 'C:\path\Akumajou Densetsu (Japan).nes' `
  -OutDir 'C:\private\CVIII0551'
```

3. Keep the raw `mesen_native_stdout.txt` private. Review `state13_audit.json` for `verified_e526_state13_hit_count` and unqualified hits. If `--testRunner` or Lua input callbacks have changed in the uploaded 2.2.1 binary, the runner must fail rather than fabricate observations.

**Do not commit** ROM images, savestates, raw CDLs, original screenshots, or private raw logs to the public repository. Only inspect a vetted derived report before committing.

## Verification and limitations

- The 1,100 continuous frames in this kit are a new run design; prior 0508 evidence was three 520/220/360 savestate-connected stages, and equality between the two methods is **not assumed**.
- The local test suite exercises only parser schema, audit rules and failure modes. It does **not** emulate live gameplay.
- An authentic `state13` hit is not proved merely by a frame sample: require original `$E526` execution in state 13 with the expected physical PRG offset and an authenticated run.
- A natural hit proves only that one bounded path is reachable; it does not prove full native recompilation, NMI/frame parity or the remaining bank `$0A` bytes.
- Strict PRG coverage change: **zero**. Existing strict 49,504/262,144 and VPP 27/100 are unaffected.

## Source API references

- https://github.com/SourMesen/Mesen2/blob/master/UI/Utilities/CommandLineHelper.cs
- https://github.com/SourMesen/Mesen2/blob/master/UI/Debugger/Documentation/LuaDocumentation.json
