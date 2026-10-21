# JP0684 — First-NMI matched-boundary source-instrumentation preflight

Status: **private read-only source patcher completed and synthetic-tested; owner Windows source builds, replay, full-bus matched-stage comparison and causal verdict PENDING** (2026-10-18).

## Inputs and existing evidence

JP0683 owner-sanitized first-NMI master-clock report was authenticated by its owner-side gates, at the first PPU assertion (scanline 241, dot 1) in both emulators. Relative source-to-edge clocks are **Mesen +7** and **native +12** master ticks, a five-tick difference between *separately rooted* engine clocks. Native last pre-edge ordinary fetch/poll is at +8, edge sample/latch at +12, first promoting poll at +32, discarded opcode fetch at +44. The prior JP0676 private bus witness establishes **one extra fully completed three-cycle native instruction** before the rejected fetch. JP0684's previous logic-only audit ruled out comparing Mesen's `Exec` post-opcode `IRQ()` decision directly with the native post-fetch discard marker. **Physical cross-engine equivalence/root cause is still unproved.**

## Source-grounded diagnostic implementation

A private handoff bundle `JP0684-Matched-Boundary-Source-Probes.zip`, SHA-256 **`237d04219d4e757e4a620b8b4359541cd9bc42fdb67f4a2dc573145a3f6b3b4f`**, provides `jp0684_patch_boundaries.py`, `test_jp0684_patch_boundaries.py`, and `README.md`. Only this description is public; owner-supplied ROM, compiled diagnostic binaries, raw PC/opcode/bus/audio traces and patched third-party source copies must remain private.

The patcher creates **new separate copies** of owner-local, already JP0683-instrumented Mesen2 and NESRecomp source trees. It requires exact textual source anchors and rejects duplicate instrumentation/missing anchors/existing destination; it emits source and output SHA-256 values. It inserts read-only, opt-in CSV logging (no address/value mutators, no CPU/PPU cycle changes):

- Pinned `SourMesen/Mesen2@b9fa69ddc6d0a331fb103fdb5eef6904305703c2`: `Core/NES/NesCpu.cpp`, instruction entry; opcode completed before `IRQ()` test; NMI/IRQ decision; actual read/write bus sites after `StartCpuCycle()`, before memory-manager access.
- Pinned `mstan/nesrecomp@2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`: `runner/cyc/cpu6502.h` poll before/after, opcode bus fetch before read, post-fetch reject/accept decision, read/write bus sites; `cpu6502.c` interrupt entry window; `hw_machine.c` final cycle done with separate entry marker.
- Private six-field CSV: `event,cpu_cycle,local_master_clock,pc,address,aux`. Native clock uses `12*hw.cycles+hw.tick` at CPU bus stages, but JP0683 remains the authoritative probe for PPU source assertions/tick-4 pin sampling.

**Local verification:** 13/13 Python tests pass, including anchor collision/missing-anchor rejection, non-modifying copy contract, opt-in logging, and C11/C++17 standalone diagnostic helper syntax. **No full Mesen2 or NESRecomp Windows build and no owner-original seven-frame replay was run for this JP0684 patcher.** Successful standalone helper compilation is not emulator build validation. JP0683 source copies may have private modifications beyond the checked anchor shapes, and their commit provenance still needs owner-side source authentication.

## Owner-private capture and promotion gates

1. Patch only copies of existing validated JP0683 private source trees, then build both diagnostic targets on Windows. Fail closed on any source-anchor/build mismatch.
2. Run original-JP deterministic neutral first seven frames with separate `JP0684_MESEN_LOG` and `JP0684_NATIVE_LOG` private file paths. The probes log only CPU cycles 85,000–90,000.
3. Revalidate the original-vs-instrumented Mesen JP0673 instruction/selected-bus/audio tuple baseline, native JP0676 three-cycle extra-instruction/discarded-fetch bus signature, JP0683 native frame-3 trace SHA and first 13 ordered audio writes. If changed, **`INCOMPLETE_NOT_PROVEN`**.
4. Match by semantically equivalent actual bus accesses: last completed opcode, NMI admission/first entry dummy access, three ordered stack writes, both NMI-vector reads, first handler fetch. Keep PC/physical bank identity matching and raw logs owner-local. Compare within-engine, source-relative clocks; **do not assume common absolute engine clock origin**.
5. Publish only hashes, relative tick deltas, counts, gate booleans and safe verdict. No CPU/PPU timing patch, VPP credit or strict PRG credit is authorized by instrumentation preflight.

**Next checkpoint:** guarded Windows build/replay scripts and fail-closed private raw-CSV same-stage sanitizer. Until validated owner capture, `NMI_root_cause_proven=false`, `CPU_or_PPU_timing_patch_authorized=false`, and `cross_engine_absolute_master_origin_calibrated=false`.
