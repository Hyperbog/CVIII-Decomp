# Japanese native decompilation — continuous improvement operating loop

**Purpose:** Make each verified source reconstruction easier to reproduce, easier to audit, and quicker to extend. The model is not retraining its weights. Durable improvement comes from **committed source, executable audits, checklists, and lessons** in this repository.

## The default source-to-native loop

1. **Target one original-ROM control-flow boundary.** Name CPU entry, raw/fixed physical PRG bank, exact instruction ranges and first unsupported exit. Avoid claiming a whole actor frame when a subroutine is all that has been reconstructed.
2. **Record an immutable original oracle.** Validate the original Japanese ROM SHA-256; independent Mesen agent/core; mapped physical PRG addresses; original 6502 PC/A/X/Y/P and cycle count; full 2 KiB RAM before and after; instruction count and stop reason. Treat bank inferred solely from zero-page `$23` as insufficient.
3. **Label input provenance per test.** Natural execution requires controller-only original game state. If the test injects ROM, RAM, PC, mapper state or synthetic coordinates, explicitly mark the row **synthetic**. Two nested CPU instruction windows from one actor are not two independently reached actor events.
4. **Lift bounded source semantics to C++**, not an emulator or screenshot demo. Preserve 8-bit wraparound, signed arithmetic, 6502 N/Z/C/V flags, scratch writes and original branch priority. Return an exact unsupported original CPU PC instead of inventing the unimplemented callee.
5. **Run three layers of validation:** ROM-free exhaustive/property tests for arithmetic and branch boundaries; independent original-Mesen entry/exit CPU/RAM differential; and compositional testing from the previously authenticated upstream routine. Use ASan/UBSan, then CMake/CTest and preservation CI.
6. **Promote only supported progress.** The source behavior, natural liveness, comparison windows, independent natural actor events, certified PRG bytes, and VPP rubric points are six different metrics. Follow the strict byte ledger and rubric before changing either numeric certificate.
7. **Publish a checkpoint receipt** comprising native source/header, unit test, Mesen replay tool or minimal step instructions, report JSON, technical findings and original recovery continuation. Re-run `python3 JP/tools/audit_native_evidence_ledger.py` after adding the new manifest row.

## Repeated failures converted into operating rules

| Previous issue | Permanent remedy |
|---|---|
| Windows demo crashed from nearly 1 MiB of automatic graphics arrays | Use bounded heap/static graphics storage; real Windows GUI CI and correct MSVC runtime linkage. Keep this separate from source-decomp completeness. |
| Bash `set -u` interpreted `$80E3` in a double-quoted status string as positional `$8` | Single-quote literal 6502 `$` addresses in shell messages, or escape them. |
| Mesen `--frames 0`/state export may leave PC one instruction ahead | Assert exact PC, CPU registers, original cycle, mapped PRG and RAM fingerprint after every snapshot operation. Never assume a saved state resumes at the stated PC. |
| Two semantically identical Mesen savestates can serialize to different compressed byte hashes | Hash and verify **original RAM, PC, registers, cycle and source mapping** at derived breakpoints. Use a fixed private input state SHA when available; do not treat a compressed derived save hash as gameplay identity. |
| Natural and RAM-injected trials were conflated or nested natural windows were counted twice | Use `natural_windows`, `synthetic_windows` and `independent_natural_events` as separate counts; validate them through [evidence ledger](../analysis/NATIVE_EVIDENCE_LEDGER.json). Compared RAM byte totals are **comparisons**, not unique ROM or RAM coverage. |
| PRG code was newly lifted although its physical bytes were previously certified | Apply [physical-source overlap audit](../tools/audit_native_coverage_0518.py). The 0501 and 0508 references are not the complete historical 49,504-byte union, so 'outside these two manifests' never means 'newly certified'. |
| CI results were described as green before completion | Check both native regression and preservation workflows on the **exact branch HEAD SHA** and require `completed/success`. Distinguish original-ROM private replay from ROM-free public CI. |
| Placeholder desktop demo looked playable but lacked source parity | Give priority to CPU/PPU/OAM/actor state equivalence and actual original game frame integration, not visual static screenshots. |

## Fast checkpoint command paths

With no ROM, run from repository root:

```sh
python3 JP/tools/audit_native_evidence_ledger.py --json
python3 JP/tools/audit_native_coverage_0518.py
bash JP/tools/run_native_regressions.sh
cmake -S JP/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
```

With the **private original Japanese ROM**, additionally validate physical hashes using `python3 JP/tools/audit_native_coverage_0518.py --rom /path/to/rom.nes`; run the corresponding Mesen source differential with its privately saved authentic input and the built native replay executable. Do not commit ROM bytes, original-ROM-derived image assets, private RAM snapshots, debugger traces or savestates.

## Update rule for next checkpoints

Append a new row to `analysis/NATIVE_EVIDENCE_LEDGER.json` only after the original source report and replay pass. The row must reference exact source/test/replay paths, original comparison-window count, natural/synthetic provenance, independently reached actor events, compared RAM bytes, and a caveat. If the report uses a new field name, specify it through `case_key` / `ram_key` / `natural_key` / `synthetic_key`; don't hand-edit claimed totals without a verified JSON source. If a source PRG or VPP certificate truly changes, update the dedicated strict byte audit, scoring rubric, and recovery state together with a machine-readable decision.

**Current verified frontier:** research 0520; naturally reached original `$FDFE→$BD11→$FE34→$FE60` actor gate; next original call `$FE60 JSR $EF93`. Certified semantic checkpoint 0508, strict PRG 49,504/262,144, VPP 27/100, fixed frontier `$FB96` until independently promoted.
