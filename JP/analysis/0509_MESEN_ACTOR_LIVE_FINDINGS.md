# 0509 — Independent original Mesen2 live actor-event dispatcher and type-$3D creation

**Status: VERIFIED ORIGINAL-JAPANESE GAMEPLAY ENTRY for a bounded Stage 1-02 path.** This replaces the prior statement that the whole bank-$0A:$84EA → $8501 dispatcher had no independent Mesen reachability witness. The *different* provisional actor creation entries $90C5/$90DF/$9133 remain unproved live; strict PRG accounting and checkpoint certification do not advance.

## Emulator and ROM provenance

The original user-supplied iNES Mapper 24 VRC6a image was loaded unmodified by independently built **Mesen 2.1.1**, via the public headless `mesen-agent` Linux x64 artifact. Mesen agent executable SHA-256 **95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0**; matching external MesenCore.so SHA-256 **d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040**. Original ROM SHA-256 **958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28**. This Mesen core hash differs from the earlier 0508 independently recorded core build and is stated explicitly; no identity with that prior binary is assumed.

Cold boot through real Mesen CPU/mapper/PPU with **controller-only** input: four brief Start presses before frame 370; held right/A for the Stage 1 introduction; then held right with periodic A and Up pulses. Clean, frame-aligned checkpoints are frame 1503 and frame 2603. **No PC, RAM, mapper, stack, or savestate edits were made.** Savestates were used only to accelerate repeated stepping from an already naturally executed point.

## Genuine bank-qualified breakpoint and source selector

At **frame 3092**, Mesen's execution breakpoint **NesMemory:$84F3, condition [$23]==$0A** hit with original PC=$84F3, A=$32, X=$03, Y=$02, P=$00, SP=$F1 and CPU cycle **92,059,934**. Mapped VRC6 raw bank was $0A ($23=$0A). The first-level RAM $18=$04; RAM $53=0; the selected source object X=3 had **$07C2,X=$32**, event subindex **$07C8,X=$00**, and guard **$07E0,X=$00**; the twelve destination actor slots were unoccupied.

Authentic source ROM double indirection resolves row $32: **$8523+2*$32 = $8587**, the ROM word there is **$8B26**, and the first word of that second table is **$8B2C**. Mesen steps the original instructions $84F3 (JSR $8501), $8501–$8520 (table lookup and JMP ($0002)), and the actual raw-bank-$0A handler $8B2C. This is a **new live actor-event row** compared with the previously synthetic rows $08/$09/$0A.

## Actual 600-instruction CPU trace

An independent debugger replay from the saved unmodified breakpoint executed **600 original 6502 instructions**. Each of **$84F3, $8501, $8520, $8B2C, fixed $FF06, fixed $FF24 and the $84F8 scheduler return** appears **twice**. The trace also proves the $8B2C → $8D5E/$8DC1 scanning and initialization path and an actual mapper switch through fixed $E77A to raw bank $0B. The two dispatches create actor slots **1 and 2**, both with **$054E,X=$3D**. The corresponding source object event fields progress **$07CB:00→11** and **$07CC:00→21**. Post-step CPU cycle **92,062,031**.

Two independently reproduced runs from clean source boot reached the same breakpoint at frame 3092, with identical CPU PC/A/X/Y/P/SP/cycle count, and produced **bit-identical** 600-instruction text traces. SHA-256 of that *private* source trace: **dce02d6ce15c65a4b2dbdeea880b3171206514eeb7d35bb9168fcff56db48d93**. [Compact machine report](0509_MESEN_ACTOR_LIVE_REPORT.json). The original ROM, emulator binary, internal savestates, raw text trace and Mesen code/data masks are not committed.

## Physical code/data logger cross-check and exclusions

A separate natural-input Stage 1-02 run with the independent Mesen physical PRG CDL recorded **CODE** for physical raw-$0A CPU **$84EA, $84F3, $8501 and $8520** and fixed **$FF06** over frames 2603–3803; the raw-$0A **$90C5/$90DF/$9133** creation entries were **not** observed on that sampled branch. Earlier frames 1503–1803 had $84EA code but not $84F3/$8501. This is a bounded positive/negative observation, not a global reachability domain conclusion.

## Reproduce and conservative accounting

The original complete clean-boot and debugger replay, including a fresh input schedule and SHA verification, passed from the provided ROM using `JP/tools/audit_mesen_actor_live_0509.py` with a standalone Mesen-agent 2.1.1 binary. It asserts authentic RAM selector/guard values, original source pointer words, identical trace SHA and CPU cycles. Required external emulator binary and original ROM are not included in the repository. An earlier, narrower [capture guide](../docs/0509_MESEN_ACTOR_DISPATCH_CAPTURE.md) remains useful for unrelated rows.

**Strict PRG +0; total 49,504 / 262,144 (18.8843%), VPP 26/100, completed checkpoint 0508, physical fixed frontier FB96 unchanged.** Even though the selected original event row has verified game-entry liveness, promoting new source bytes requires an independent physical overlap subtraction, instruction/data boundaries and the project's checkpoint audit. The global room-$18=0C/0D producer and all-route native frame/PPU/APU parity remain OPEN.
