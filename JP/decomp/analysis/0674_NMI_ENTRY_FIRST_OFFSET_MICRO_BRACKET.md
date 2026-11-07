# JP0674/JP0675 — First native/original CPU-cycle offset at NMI boundary

Status: **JP0674 owner-private aggregate received and validated; JP0675 detailed local trace phase audit pending.** This is **not** cycle-exact emulation parity, DMA parity, or a CPU patch justification. Owner-private original ROM, instruction traces, bus accesses, audio-register event CSV, and compiled binaries remain off GitHub.

## Independent original/native parity preserved

The corrected JP0671 original Mesen2 capture and prior native C11 Enhanced Original Edition session produced exactly **3,401/3,401 matching ordered 2A03/VRC6 audio register/address values**, with unadjusted absolute write-time differences from −7 to +9 CPU cycles. Source-level pre-write tap phases differ (JP0672). The first changing register-write offset is from −1 to +1 at audio-write ordinal **13**.

The private JP0673 seven-frame witnesses passed their internal audio-equivalence gates, providing 30,066 monotonically PC-aligned instruction records out of Mesen 30,070 and native 30,071. First PC-matched instruction offset change is ordinal **3,300**: native-minus-Mesen from **0 to +3 cycles**. The owner uploaded `JP0674-micro-bracket.json`; its recomputation flags `JP0673_alignment_reproduced`, `JP0673_native_trace_hashes_verified`, `JP0673_original_capture_hash_verified` all true. The raw private CPU traces were **not** uploaded, so those flags attest checks made by the owner's local analyzer rather than independent reprocessing here.

## Exact JP0674 transition bracket

| Observed property | Original Mesen | Native C11 |
| --- | ---: | ---: |
| CPU cycles between matched instruction ordinals 3,299 → 3,300 | 10 | 13 |
| Unmatched `INSN` records **between these matches** | 0 | 2 |
| NMI vector read cycles relative to matched ordinal 3,300 | −1, 0 | −2, −1 |
| Three NMI stack access cycles relative to matched ordinal 3,300 | −4, −3, −2 | −5, −4, −3 |
| Matched-instruction native-minus-Mesen offset | — | 0 before, +3 after |

The NMI vector reads belong to **$FFFA/$FFFB**, with three closely preceding stack accesses. The nearest native **$4014** OAM DMA request is **+78 CPU cycles *after* the matched ordinal**, native DMA halts +79/+80. OAM DMA therefore cannot directly be the cause of this *first* earlier NMI-boundary transition.

The vector-read timing permits a more precise **phase hypothesis** from the sanitized numbers: native's **+3** matched instruction offset, plus native vector position `−2` versus Mesen `−1`, implies **+2 absolute cycles** at the first vector read; the second vector read yields the same **+2**. Likewise each nearest of the three stack accesses has **+2 absolute cycles** by ordinal-relative pairing. The remaining **+1** at the next matched instruction corresponds to different vector-to-instruction observation phases (Mesen's last vector callback is timestamped at the same cycle as its next instruction callback; native's last vector bus cycle is one cycle before its next `INSN` record). The first stack access is 8 native versus 6 Mesen cycles after the *previous* matched instruction. This narrows the issue to the **pre-stack NMI onset/previous instruction interval** plus callback-phase effects; this is not proof that native executed two extra hardware CPU cycles.

### Source inspection: why skipped native `INSN` lines are insufficient proof

In pinned `mstan/nesrecomp` commit `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`, `runner/cyc/cpu6502.h` logs `cyc_trace_instruction(pc)` in `cpu_fetch`/`cpu_fetch_rom` **before** the return check for `do_nmi | do_irq | do_reset`. Consequently a fetched opcode that is discarded for an interrupt can still produce a native `INSN` trace record. `runner/cyc/cpu6502.c` `cpu_interrupt(false)` does the second preliminary read, three stack transfers and the two vector reads (seven-cycle hardware interrupt sequence in combination with the first discarded fetch). In Mesen2 upstream `Core/NES/NesCpu.cpp`, `NesCpu::Exec()` calls `ProcessInstruction` before `GetOPCode`, executes the opcode then invokes `IRQ()` on the relevant interrupt condition; `IRQ()` performs **two** preliminary dummy reads, the three stack pushes, then two vector reads. So neither implementation's main NMI routine trivially contains two extra interrupt-entry bus cycles. Their **interrupt polling / callback placement** remains an untested difference. The two unmatched native trace records near ordinal 3,300 may reflect different entry logging, repeated PCs, unmatched actual instructions or alignment ambiguity. Source inspection does not adjudicate this without the private local traces.

Mesen bus witness here is **selective**, not a complete bus trace. Native traces observe all bus cycles, but the clocks/callbacks are not yet normalized. **Do not** patch CPU instruction timing, rebias event timestamps, alter input, or certify parity on this basis.

## JP0675 next diagnostic — no re-recording

An owner-private read-only tool `jp0675_nmi_entry_phase.py` and 12 synthetic regression tests are distributed in `JP0675-NMI-Entry-Microtrace-Audit-Kit.zip` (not ROM data). It must be run **on the owner's Windows machine** alongside the earlier `jp0673_compare_cpu_witness.py` and `jp0674_first_instruction_transition.py`. It SHA-authenticates prior original and native CPU traces, reproduces ordinal-3,300 matched PC alignment and 2 unmatched native rows, requires the adjacent NMI vector read pair and sequential stack pushes, and reports only relative clock, generic bus category and private-PC equality predicates. It fails closed if those invariants differ. The synthetic test suite passes **12/12**. Full owner Windows execution **pending**.

Expected safe artifact: `C:\Tools\Mesen2\Private\JP0673-CPU-Witness\JP0675-NMI-entry-phase.json`, which can be uploaded alone for further analysis. Do not commit the private raw witness files to Git.
