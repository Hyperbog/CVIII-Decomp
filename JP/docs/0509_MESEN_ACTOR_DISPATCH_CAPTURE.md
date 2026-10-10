# 0509 optional original Mesen2 actor-event reachability capture

**Purpose:** verify real original-gameframe and raw-bank-$0A mapper liveness independently. The connected source-step audit already passes 98,304 cases. This is an optional external emulation test, not a prerequisite to run those local tests.

1. Load the original **Japanese Akumajou Densetsu** ROM in Mesen2 with its normal Mapper 24 / VRC6a. Play normally into a stage or room. Do not use the US ROM, forcibly alter PC, or edit a selector to fabricate access.
2. Set an **execution breakpoint** at CPU **$84F3**, and optionally at **$8501**, **$90C5**, **$90DF**, and **$9133**. Record only hits where the physical raw VRC6 bank mapped at **$8000-$BFFF** is **$0A**. Without bank validation an identical CPU address can name a different routine.
3. At a naturally reached $84F3 break, record: gameplay frame/room, PC, A/X/Y/P/SP, mapper-selection RAM **$23**, CPU RAM **$53/$54/$69**, and each of **$07C2+X**, **$07C8+X**, **$07E0+X**. Record the twelve destination slot occupancy bytes **$054F-$055A**.
4. If feasible, step 150–300 original instructions from the $8501 indirect jump through the $8CDD guard and fixed $FF06 scan to the selected handler return. Record which original RAM addresses change, particularly $054F-$055A, the indexed actor scripts $05EF-$05FA, and the originating $07C8+X.
5. Supply the exported debugger text log, annotated screenshots, or a privately shared original-JP Mesen savestate here for comparison. Please do not commit any ROM copy or savestate to Git.

**Most useful single artifact:** one natural $84F3 breakpoint with confirmed bank $0A, frame/room, original X and the three indexed RAM selectors, plus a short stepping trace through $84F8. If none is hit, report the duration/frame count, input path and stage tested; that finite negative observation is not global proof of dead code.

Do not change P/stack/mapper/selector state to make the test pass. The important missing evidence is the actual naturally reached producer-and-dispatch state, not another synthetic conditional CPU run.
