# JP0612 — Original JP fixed $E249 sound-request CPU-entry observations

**Purpose:** preserve real sound-request entries before the original game scheduler chooses hardware writes. No original ROM, NSF, game data or licensed runtime C source is committed.

## Original-JP address contract

The [0611 bank-$0C study](0611_SOUND_REQUEST_ENTRY_CENSUS.md) authenticates fixed PRG31:$E249 (opcode PHA, $48) and its bank-$0C:$8850 wrapper. The private pinned NESRecomp cycle host executes CPU instructions through **two paths**: statically generated code calls `hw_read_rom` at an opcode fetch, and interpreter fallback calls `hw_read`. Both pass through `hw_machine.c`. The [JP0612 private overlay generator](../tools/patch_cyc_sound_requests_0612.py) taps both only when all conditions hold: `cpu_opcode_fetch`, PC $E249, fetched opcode $48, mapper 24, and none of `cpu.do_nmi/do_irq/do_reset` set. It observes **after** the original read and before the CPU executes PHA. A fetch discarded by an interrupt is not counted.

The [C11 logger](../native/enhanced/cviii_sound_requests_0612.c) writes a bounded owner-local CSV with cycle, PC, incoming A command, X, Y, S, P, tracked VRC6 PRG bank ($23), and two raw stack bytes at $0100+(S+1) and $0100+(S+2) with 8-bit wrap. Those stack bytes are deliberately **not named a caller PC**; a JMP tail entry can inherit a different stack frame. A CPU-cycle timestamp can repeat or decrease after a save-state load. The logger does not read hardware via CPU buses, mutate CPU/memory/audio, classify music versus SFX or change PCM.

## Owner-private invocation

After regenerating the Windows AlphaCandidate with the latest branch, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -AudioTrace
```

Alongside existing `CVIII-Audio-Registers.csv`, the launcher now requests `CVIII-Sound-Requests.csv`. The hardware register log is still the JP0610 observer, with its original schema. Each file is independent and opt-in. Events dropped inside the original sound scheduler **before reaching $E249** are invisible, and per-request acceptance/rejection after $E249 has not yet been proven. Pair trace cycles only as discovery, not as certified ownership or event correlation.

## Verification boundary

- Local isolated compilation: GCC/Clang-style strict C11 logger fixture `-Wall -Wextra -Werror -pedantic`, 2 test events, wrong PC ignored, duplicate-open rejected — PASS.
- Standalone Python source overlay smoke: both opcode-fetch paths, interrupt gate, mapper gate, duplicate patch rejection, changed-anchor fail closed — PASS.
- Public upstream `mstan/nesrecomp` master inspection: all three required `hw_machine.c` replacement anchors each present exactly once; exact **pinned private checkout** must still pass build-time checks.
- Both Windows and Linux CI workflow files have synthetic ROM-free build/test gates, but the new HEAD's GitHub Actions results and real private Windows GUI gameplay were **not** independently verified in this session.
- No MesenCE sound request trace paired with actual runtime CSV has yet been collected, and no dropped SFX, musical ownership or enhanced mixer parity can be inferred.

**Accounting unchanged:** 49,504/262,144 (18.8843%) strict semantic PRG, VPP 27/100, last certified checkpoint 0508, fixed investigation frontier $FB96. Preserve RESUME_STATE.json untouched: JP0612 is *research instrumentation*, not semantic checkpoint 0509 completion.

**Next module:** validate owner-generated CSV ordering and pair per-command CPU-cycle windows against JP0610 register traffic, marking ambiguous/shared-channel cases. Instrument earlier event producers only after ROM and original Mesen execution prove them.
