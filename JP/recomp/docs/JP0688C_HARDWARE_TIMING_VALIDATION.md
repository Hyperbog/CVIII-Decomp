# JP0688c — Pinned public NES hardware timing validation

Status: **OWNER EXECUTION REPORTED; EVIDENCE CHECKED: 16/16 PASS.** See [verified results](JP0688C_HARDWARE_TIMING_RESULTS.md). This is internal evidence agreement, not an independently rerun emulator or hardware laboratory test.

## Scope and provenance

- NESRecomp standalone `cyc_interp` revision: `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`.
- Blargg public tests from `christopherpow/nes-test-roms`: `95d8f621ae55cee0d09b91519a8989ae0e64753b`.
- Four ROMs: `02-vbl_set_time`, `04-nmi_control`, `05-nmi_timing`, and `5-branch_delays_irq`. Each is tested at CPU/PPU alignment `0,1,2,3`; `900` frames, snapshot after frame `899`.
- The original public test ROMs have NROM iNES headers without declared PRG RAM. Pinned NESRecomp does not enable WRAM for this arrangement, making the standard Blargg `$6000` status protocol unavailable. The harness writes a **private header-only copy** with iNES header byte 8 set to `1` (8 KiB PRG RAM). Test source, program and graphics bytes are unchanged; no original file is overwritten.
- JP0688b already demonstrated `04-nmi_control` alignment `0` returns `$6000=00`, valid `$6001-$6003=DE B0 61`, exit `0`. It is a single control case, not a complete matrix.

## Owner execution (Windows PowerShell)

1. Keep the pinned NESRecomp and test ROM clones under `C:\Tools\Mesen2\Private\JP0688-Hardware-Validation\` and the existing JP0684 working folder.
2. Run [`jp0688c_run_hardware_matrix.ps1`](../tools/jp0688c_run_hardware_matrix.ps1) from a Windows PowerShell session. It validates both Git pins, builds the standalone host, checks public ROM geometry and records all 16 results. Only private public-test header copies, WRAM dumps and stdout logs are written under `Private\JP0688-Hardware-Validation\JP0688c\`.
3. Upload **both** `JP0688c-hardware-matrix.json` and `JP0688c-wram-evidence.txt` from `C:\Tools\Mesen2\JP0684-Native-Clock-Logging-Fix\` for independent review.
4. Independently check `python JP/recomp/tools/jp0688c_validate_evidence.py JP0688c-hardware-matrix.json JP0688c-wram-evidence.txt`. This cross-checks 16 unique `(test, alignment)` cases, expected pins, $6000 signatures and reported codes against the captured WRAM excerpts. It does **not** independently execute the hardware core or compare output with real hardware.

## Result interpretation and release gate

- `PASS`: test's own status code `00`, correct signature, normal process exit. The PPU timing and IRQ observational tests also contain an internal printed-output CRC gate; a correct `00` indicates that each test reached its own accepted terminal result.
- `TEST_FAILURE_CODE`: a reproducible nonzero final test code. Capture the exact code and failure text, determine alignment dependence and compare original hardware/independent Mesen. A lone alignment-specific failure is not by itself proof of an emulator defect.
- `STILL_RUNNING`, `RESET_REQUIRED`, `NO_DUMP`, `NO_WRAM_RESULT`, `INVALID_TEST_SIGNATURE`, `RUNTIME_ERROR`, `INVALID_RESULT_CODE`: inconclusive or harness failure; they must never be counted as core timing failures.
- **No NESRecomp core or Castlevania III/Enhanced Edition changes until failure is independently reproduced and localized.**
- Keep committed artifacts limited to ROM-free harness (`.ps1`, `.py`), this procedure and an honest compact result table to the existing `jp0664-famistudio-reference` development branch. Keep ROMs, `.mem.txt`, `*.log`, original/derived commercial game data and private Windows binaries out of Git. Do not merge draft PR #11 or modify the playable baseline merely because these standalone tests pass.

References: [NESRecomp cycle runner](https://github.com/mstan/nesrecomp/tree/2b4fcdb98c9e702be3fb365cfc645003c50b5fc1/runner/cyc) and [Blargg test readmes](https://github.com/christopherpow/nes-test-roms/tree/95d8f621ae55cee0d09b91519a8989ae0e64753b/ppu_vbl_nmi).