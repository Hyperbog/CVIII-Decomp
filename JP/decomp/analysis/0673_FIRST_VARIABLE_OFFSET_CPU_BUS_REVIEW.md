# JP0673 — First variable CPU-cycle offset: bracket, ROM-free contract and targeted witnesses

## JP0673 owner upload — authenticated 30,066-PC instruction alignment, first change ordinal 3,300 (2026-10-17)

The owner has now supplied the **sanitized** output `JP0673-aligned-aggregate.json` of the corrected, authenticated CSV/ZIP fallback matcher. This report was checked against the separately preserved `JP0673-status.txt`: original Mesen witness SHA-256 `a063546419c9c4c86a24cde00c19af4517f935cd5c6d9f3892f3f291f60791bc` and all four native frame-trace SHA-256 values match the acquisition status. The matcher reports `audio_stream_headless_and_original_provenance_matched: true`, meaning the short headless and original CPU runs passed the programmed 13-write/76k–171k Mesen audio-equivalence gates. **Only the aggregate and earlier status were uploaded, so the assistant has not independently re-read or re-aligned the owner's full private raw CPU traces.**

Aggregate: Mesen **30,070** and native **30,071** instruction starts in the common clock window; **30,066** strictly monotonic matching PC pairs (**99.9834%** coverage), with **5 native and 4 original instructions unmatched**. The first **3,299 matched instruction timestamps have identical absolute CPU-cycle counts**. At matching instruction ordinal **3,300** native-minus-Mesen instruction-clock offset changes from **0 to +3**; matched instruction offset range is **0..+4**, with only 3,299/30,066 timestamp-exact pairs overall. The change lies between original audio writes 12 and 13, for which the write-callback difference separately shifts −1→+1 (+2). The two differences are **not interchangeable**, because an instruction-start timestamp and audio write timestamp use different callback phases. Native trace includes **1,024 DMA bus access records and 4 DMA halt records** over frames 2–5; the aggregate does not identify their proximity to ordinal 3,300.

**Root cause remains unknown.** The original matcher uses nearest matching PC within ±32 absolute cycles; at a repeated PC or an unmatched insertion/deletion, the reported first shift may be a mistaken alignment rather than a genuine extra CPU bus cycle. The short Mesen witness probes only selected I/O bus addresses, not all CPU bus accesses. The assistant prepared `JP0674-Instruction-Micro-Bracket-Kit.zip` as an **owner-local** read-only next step: SHA-pin every private witness back to the JP0673 aggregate, reproduce the same PC alignment, identify unmatched-instruction gaps immediately around ordinal 3,300, and summarize native DMA and Mesen NMI/vector/stack/OAM/controller/PPU events in narrow ±16/64/256/1024-cycle windows, outputting no raw PC/opcode/bus values. It passed 9 ROM-independent Python tests including synthetic insertion and tamper rejection; Windows execution against real private traces remains pending. Do not attribute the first offset to NMI, OAM DMA, DMC or extra instruction until this micro-bracket is reviewed; no CPU timing/audio code changes are warranted yet.

## JP0673 owner local matcher path correction — prior native CSV preserved inside ZIP (2026-10-17)

After successfully collecting the full seven-frame Mesen witness and four native headless per-frame traces, the owner attempted `jp0673_compare_cpu_witness.py`. The matcher aborted **before audio-prefix equivalence or instruction alignment**, with `FileNotFoundError` on the prior window-mode `CVIII-Audio-Registers.csv` at the hardcoded *extracted-directory* path. The owner had previously collected `JP0668-Native-StderrFix-20261017-205325-9e1573.zip`; the archive contains the same private CSV under an outer folder. The original-window CSV SHA-256, independently known from JP0671, is `3d4a32dd8c507119960f17e7a8104d17b492a6ff23eda4c11688eeec38b3eac3`.

This is a **local file-location issue**, not a failed parity/alignment gate. A private, backwards-compatible comparator patch now checks the exact CSV SHA-256 and, if the extracted file is missing, reads the named CSV member directly from the sibling ZIP or another `JP0668-Native-StderrFix-*.zip` in the owner-private directory. No extraction, file overwrite, altered replay, or relaxation of PC/audio alignment checks. Seven synthetic file/ZIP/hash tests passed and the fallback was exercised successfully against the preserved owner capture ZIP in a separate analysis workspace. **The owner's Windows retest is pending**, so no cause of the first two-cycle CPU timing difference is yet identified. The patch and tests are distributed as `JP0673-Private-CSV-Archive-Fallback-Fix.zip`; only code and safe aggregate documentation are public.

## Owner Windows JP0673 witness acquisition — complete, content comparison pending (2026-10-17)

The owner ran the **v2** JP0673 script with the verified private diagnostic Alpha; the prior v1 dependency on a historical JP0668 status file was removed. The returned `JP0673-status.txt` attests that a seven-frame Mesen2 CPU instruction/bus log finished (`MesenStatus: COMPLETE_LOG_IGNORE_EXIT_CODE_MINUS_ONE`) and native headless trace captures for **frames 2, 3, 4, 5** completed. Original JP ROM SHA-256 remains `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; native diagnostic EXE SHA-256 remains `9039b9b8bce775249a765a2fad100b286b91168fb6defc5404503f1ab5c9d8ed`. Original Mesen log SHA-256 `a063546419c9c4c86a24cde00c19af4517f935cd5c6d9f3892f3f291f60791bc`, and Mesen build SHA-256 `8ef403d6b9af32075416193914d7993ce8480b347fe1f20a0cfd9815374933e7`. The four native trace file hashes are recorded in the owner's private status. Every seven-frame native audio CSV hash is identical (`fd6873ae7ff63e9aecf20b280dcbfed13452f69c09c1e47665a7f78665930260`), consistent with deterministic repeated headless execution but **not sufficient** to attest equality with prior window-mode original/native audio.

**No raw CPU/PC/bus log was uploaded or committed.** Status is `RAW_WITNESSES_COLLECTED_REQUIRES_INDEPENDENT_INSTRUCTION_ALIGNMENT`, not an instruction-timing result. The next step is to run the already-distributed `jp0673_compare_cpu_witness.py` **owner-locally** against the new private witness directory, the validated JP0671 1,100-frame original log and the prior JP0668 native register CSV. Its gates check 7-frame original audio equivalence, native headless-to-window first-13-write prefix equivalence, chronological native/mesen instruction records, monotonic PC alignment, and at least 90% matched coverage. If it succeeds, publish only the sanitized aggregate JSON. Until then, the exact divergent instruction/bus/DMA operation is **UNKNOWN** and CPU-cycle parity remains uncertified.

## Result from authentic owner-private traces (no ROM/events redistributed)

The corrected original JP0671 Mesen2 trace and retained JP0668 native C11 Alpha trace have **3,401/3,401 equal ordered register/value events**. JP0673's fail-closed audit identifies the **earliest offset change at audio write ordinal 13**:

| Observation | Mesen2 | Native C11 |
| :-- | --: | --: |
| Write 12 cycle | 80,414 | 80,413 |
| Write 13 cycle | 165,488 | 165,489 |
| Native minus Mesen write timestamp | −1 → +1 | — |
| CPU cycles elapsed between the writes | 85,074 | 85,076 |

Mesen end-frame boundaries **3, 4, 5** and three actual input polls fall strictly inside this gap. The first scripted player-one Start press occurs at frame 90; first logged DPCM descriptor write is event 117. The two extra native cycles accumulate before either, so a *button-input mismatch at frame 90* and DPCM *descriptor programming* cannot explain this **first** transition.

**Exact cause remains unknown.** Audio-only writes lack CPU read/instruction/NMI/DMA observations during 85,000+ intervening cycles. Do **not** infer whether two native CPU cycles were added, two Mesen CPU cycles omitted, or the same number of cycles have been accounted for against different power-up/frame epochs. Distinguish observed elapsed-count difference from actual executed extra bus cycles.

## Source-bound phase convention

- Native pinned engine `mstan/nesrecomp` `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`: `cpu6502.h` runs `hw_cycle_start` → `hw_write` → `hw_cycle_finish`; `hw_machine.c` increments `hw.cycles` in `hw_cycle_finish`. Project's JP0610 audio observer reads `hw.cycles` inside write handler **before** retirement.
- Mesen2 upstream `SourMesen/Mesen2` reviewed `b9fa69ddc6d0a331fb103fdb5eef6904305703c2`: `NesCpu.cpp` `MemoryWrite()` performs `StartCpuCycle(false)` → memory-manager write → `EndCpuCycle(false)`; `StartCpuCycle` increments CPU `CycleCount`, and the `NesMemoryManager.cpp` dispatcher calls the debugger's Lua write callback before hardware write.
- **Conditional prediction** on the same instruction/bus cycle stream and common counter epoch: native−Mesen **−1 on every write**. A fixed write-callback phase is not a mechanism for the changing −1→+1 offset.

## ROM-independent executable contract model: completed

`jp0673_rom_free_bus_contract.py` executes a deliberately synthetic *bus-cycle schedule*, not actual Mesen2 or NESRecomp code. It models 6502 `LDA #`, `STA abs`, `INC abs` (two writes), a taken branch, a seven-cycle NMI-entry fixture, and another `STA abs`. It verifies that **four writes and all six synthetic instruction starts** have a constant native−Mesen offset of **−1** under the two source-documented counter phases. In a controlled counterexample, inserting two synthetic read cycles after the first `STA` changes the four write offsets from `[-1,-1,-1,-1]` to `[-1,+1,+1,+1]` without changing addresses/values. This shows *how* a real gap difference would manifest; it **does not prove any two bus cycles were inserted in the owner build**.

Eleven isolated Python regression tests pass, including fail-closed event value/order checks and write-bracket inclusion. No licensed ROM or game-derived register content is part of the model.

## Next actual CPU instruction/bus witness (short, owner-private; no rebuild)

The pinned native `cyc_host.c` already supports `--trace-frame N --trace-out FILE` (single frame, forces headless), and `cyc_trace.c` emits `INSN PC=...` and per-cycle CPU/DMA bus records. The project's previously compiled **trace-capable native EXE** can be used; no source alteration or new build is necessary. Mesen's documented `emu.callbackType.exec` supplies CPU instruction start callbacks, plus read/write memory callbacks for the NMI vector, `$4014` OAM DMA, `$4016` controller, `$2002` PPU status, `$2000` PPU control, and stack page. Controller state stays neutral because the investigated interval precedes scripted presses.

The optional owner-private `JP0673-Run-CPU-Witness.ps1` kit captures just **7 Mesen frames** and native frames **2–5** as full upstream trace files. It verifies exact ROM/Mesen/executable SHA256 before running and stores *raw* CPU PC/bus/opcode traces **only** under `C:\Tools\Mesen2\Private\JP0673-CPU-Witness`. It is **not yet Windows-tested**. The local comparison program must confirm that all captured original Mesen audio writes within the study window match the earlier JP0671 log, and that the headless native first 13 writes match the earlier 1,100-frame native window capture. If not, **the witness is not comparable and should not be used for causal conclusions**.

After proving provenance, align actual CPU instruction PC sequences by absolute timestamp proximity without rebasing; find the **first change in the aligned instruction-interval difference** and inspect neighboring DMA and interrupt-vector bus entries. This can narrow the 85,074/85,076-cycle gap to an instruction/interrupt boundary. If Mesen/native instruction streams or trace-mode event sequences differ, record that discrepancy rather than asserting a timing defect.

The native source `--trace-frame` path switches to **headless** mode, unlike the existing window-mode Alpha reference; the 13-write exact-prefix gate is therefore essential. Also, Mesen `exec` callbacks and native `INSN` printouts need an independent opcode/bus-phase check before treating their *absolute* cycle numbers as the same phase. Neither this gate nor Windows execution is yet proved.

## Remaining gates

1. **Confirmed:** first changed write offset at ordinal 13 and 2-cycle interval disagreement across end-frame boundaries 3–5.
2. **Confirmed only in synthetic source-informed model:** fixed callback phase creates constant −1 offset; a two-cycle schedule discrepancy can make −1→+1.
3. **Not yet observed:** earliest mismatch in matched real CPU instruction PCs, branch/I/O reads, NMI stack/vector access, or DMA cycles.
4. **Not certified:** cycle-exact parity, full DMC DMA parity, PCM parity, or general complete-game behavior.

All output suitable for the public repo consists only of aggregate counts, evidence hashes, source references and synthetic fixtures. Owner-private raw CPU PC/audio event streams remain off GitHub.