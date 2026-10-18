# JP0676 — NMI polling and discarded-fetch source review

Status: **pinned-source analysis completed, 15 synthetic ROM-independent tests PASS; owner-local JP0676 raw-trace classification pending**. No change to CPU execution, write timestamps, or original 3,401/3,401 ordered 2A03/VRC6 register/value parity. No private original ROM or CPU bus data published.

## What the current JP0675 aggregate proves

The earliest change in 30,066 aligned instruction pairs occurs at ordinal **3,300**, between first matching NMI stack/vector operations: previous matched instruction clocks equal, the next matched instruction is **native +3**. The previous matched instruction → first interrupt stack push span is **native 8 cycles vs Mesen 6 cycles**. All three subsequent native stack pushes and both NMI-vector reads are **+2 absolute cycles** compared with original Mesen. The remaining +1 in instruction-start offsets is explained as an observation-phase candidate (Mesen's last vector read callback occurs at the same reported clock as its next instruction callback; native's is one clock before its next `INSN` line). This is not a common-phased full bus comparison.

The original JP0675 report attests two unmatched native instruction-start records, respectively at **+3 and +6** after the previous matched start; the first native stack push is at **+8**. Mesen has no unmatched instruction starts in the same matched pair. The exact NMI pin-assertion and CPU interrupt-poll cycles are **not** captured.

## Pinned source paths and distinct instruction record semantics

| Native (mstan/nesrecomp `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`) | Mesen2 (`b9fa69ddc6d0a331fb103fdb5eef6904305703c2`) |
| --- | --- |
| `runner/cyc/cpu6502.h`: `cpu_poll(f)` copies a latched `nmi_edge` to `do_nmi`, conditioned on the CPU cycle's poll call | `Core/NES/NesCpu.cpp`: `EndCpuCycle` detects NMI edges and maintains `_prevNeedNmi`, while `Exec` checks it after an opcode's execution |
| `cpu_fetch` logs `cyc_trace_instruction(pc)` **before** reading opcode and checking `do_nmi | do_irq | do_reset`; a fetched-and-discarded opcode can therefore produce an `INSN` record | `Exec` calls `ProcessInstruction` **before** the opcode fetch; it then executes the opcode and can enter `IRQ()` after that instruction completes |
| `runner/cyc/cpu6502_interp.c`: pending interrupt from `cpu_fetch` dispatches `cpu_interrupt(false)` | `Core/NES/NesCpu.cpp`: `IRQ()` handles the pending hardware interrupt and uses two initial dummy reads |
| `runner/cyc/cpu6502.c`: an interrupt has **first discarded fetch**, then a **second read of same PC**, followed by three stack writes and the `$FFFA/$FFFB` vector pair | `IRQ()` performs **two preliminary dummy reads**, three stack writes, then the vector pair; it does not by itself have two extra cycles |

This makes a specific seven-cycle native signature (two identical-PC reads, three descending-page stack writes, `$FFFA` and `$FFFB` reads) the best discriminator for the **later** unmatched native `INSN` record. If it appears at offset **+6**, the report can certify that record as a discarded fetch rather than an executed opcode. The **earlier** unmatched native record at **+3** can be labeled a **completed three-cycle instruction** only if all three intervening native bus cycles are present and the third carries the source's `done` flag.

These tests distinguish trace logging from real extra instruction execution, but **do not distinguish** later native NMI polling from a shifted PPU NMI edge in an emulator with different CPU/PPU alignment. A genuine fix requires visibility into **both NMI line assertion** and **CPU poll/accept timing**. Do not adjust PPU/CPU clocks, inject NMI, remove a bus cycle, or add a generic timestamp bias solely based on this data.

## Read-only owner-local JP0676 audit

`jp0676_discarded_fetch_audit.py` accepts the SHA-pinned original seven-frame Mesen witness and four native frame traces already collected in JP0673; it validates JP0673/JP0674/JP0675 aggregate schemas, alignment and the first offset, independently reconstructs native bus read/write events with the native `done` marker, and emits only a **sanitized relative-cycle** verdict. It does not emit private PC, opcode, value, or bus address. The provided Python tests are synthetic: **15/15 PASS**, including corrupt/missing reads, missing `done`, nonsequential stack writes, vector mismatch and spoofed prior aggregates. **Real owner Windows execution is pending.**

The sanitized output `JP0676-discarded-fetch.json` will determine whether the native +6 record is a discarded fetch and whether the +3 record terminated a completed instruction. If the latter holds, the difference is more than just logging an interrupted opcode: the native trace completed an instruction on that extra boundary. The fundamental root cause — NMI sampling/polling vs PPU-vblank timing — remains undetermined without edge/poll timestamps.