# JP0682 — Native post-edge fetch resolution and Mesen-vs-native relative NMI intervals

Status: **JP0681 owner sanitized aggregate received; cross-core JP0682 owner-side audit pending** (2026-10-18).

## Established JP0681 result

The owner submitted `JP0681-native-NMI-poll-boundary.json` (schema `JP0681-native-NMI-poll-boundary-sanitized/v1`). The local script verified the JP0680 full private raw-log SHA-256, original JP0680 aggregate chronology and 9,315-event count. The report contains **no raw program counter, opcode, bus addresses or CPU trace**.

- With first native **edge latch** at relative CPU-count zero, last pre-edge `POLL_POST` is at **−2** with `CYC_POLL|CYC_DONE` (flag 5), `nmi_edge=false`, `do_nmi=false`.
- PPU first asserts its NMI output at **−1** CPU count, scanline **241**, dot **1**.
- **One `FETCH_PROCEED` event** is logged at **0 but before `EDGE_LATCH`**, which is also at **0**. The original JP0680 `completed_fetches_after_edge_before_discarded_nmi_fetch=1` used a *CPU-cycle-number-inclusive window*, so it mistakenly appeared to count a post-edge fetch. The corrected JP0681 **strict chronological post-edge fetch count is 0**. The label `completed_fetches` in JP0680 represents a *non-discarded opcode-fetch decision*, not instruction completion.
- At **+1** the first post-edge `POLL_POST` promotes `cpu.nmi_edge` to pending `cpu.do_nmi=true`; no prior post-edge poll failed to promote it.
- At **+3** a later `FETCH_DROP_NMI` initiates NMI entry. JP0676 separately established one additional **completed three-cycle instruction** in native-vs-Mesen alignment.
- The same-count order is significant: `FETCH_PROCEED` is logged after `hw_cycle_finish` (which advances `hw.cycles`), whereas `EDGE_LATCH` occurs at CPU NMI tick 4 of an adjacent hardware cycle with the same integer `hw.cycles` value. Equal *numeric CPU count* is not simultaneous physical CPU/PPU phase.
- JP0681 explicitly sets `Mesen_vs_native_root_cause_proven=false`, `master_clock_phase_equivalence_proven=false`, `cpu_timing_patch_authorized=false`.

**Engineering conclusion:** No evidence of CPU polling ignoring an already latched edge or of an opcode fetch *chronologically after* edge latch before the pending NMI is honored. Instead, the native CPU had already proceeded with the ordinary fetch before the NMI edge was sampled. This is consistent with edge arrival after the preceding poll, but whether the *original Mesen* detects/accepts NMI sooner for a hardware-accurate reason **remains unproved**. Do not patch `cpu_poll()` or CPU/PPU timing on these data.

## JP0682 private next comparison (zero emulation reruns)

Owner-private `JP0682-Mesen-Native-NMI-Relative-Audit-Kit.zip`, SHA-256 **`a9ea55b4675805c4933d48add507be5788681b5c01e89ae66282388f561c861c`**, contains a read-only Python sanitizer, a README and **15 passing synthetic/ROM-independent tests**. It requires the *actual successful* prior JP0678 owner-local Mesen NMI private log (pinned SHA-256 `728228f869fdb7406dde5892d5e51b7c89fee18c393d10c991cc08c64a513efb`), corresponding capture status, original-versus-rebuilt JP0678 CPU/bus/audio baseline report, 7-frame JP0679 exact PPU clock report and JP0681 native boundary report.

The analyzer obtains first Mesen `ppu_nmi_assert_vblank`, `cpu_nmi_edge_latched`, `cpu_nmi_eligible`, and `cpu_nmi_accept` events; contrasts their **within-engine CPU-cycle offsets** against native source/assert, edge, promoting poll, and discarded fetch. It outputs no private raw cycle, PC, opcode, bus or game data. Mesen's NMI PPU logger's `master` field is a **literal zero placeholder** and must **never** be used as an independent clock.

Mesen and NESRecomp instrument **different internal stages** under **unverified CPU-count and PPU/master-clock phase conventions**, so matching scanline/dot or comparing integer offsets alone does **not** certify the cross-engine NMI root cause. The kit explicitly outputs `nmi_root_cause_proven=false`, `cpu_ppu_master_phase_equivalence_proven=false`, and `cpu_timing_patch_authorized=false`. Its real owner-side comparison has **not yet run**.

Owner extracts ZIP to `C:\Tools\Mesen2\JP0673Kit` and runs `jp0682_relative_nmi.py` with the five private/aggregate input paths described in its README. Expected sanitized output: `C:\Tools\Mesen2\Private\JP0680-Native-NMI\JP0682-Mesen-native-NMI-relative.json`. Raw input logs, original ROM, DLL, EXEs stay private/off Git. If successful, analyze the reported relative stages before deciding whether any additional physical CPU clock-phase instrumentation is justified.
