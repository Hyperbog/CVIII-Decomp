# JP0744 — Verified original replay repair and first native input-phase cause

**Status:** Historical MesenCE original replay is now **authenticated against every
required JP0718 CPU-cycle/RAM anchor**. Original Japanese game data is unchanged.
A real native first-gameplay input lag was isolated and corrected in a private
**zero-based** input schedule. This repairs early player parity but **does not
solve the entire retail-native Stage 1 route**; a later selector transition
remains divergent. Do not claim playable-complete parity or lift VPP/strict PRG.

## Exact MesenCE script fault (fixed in tracked canonical source)

Current MesenCE `Core/Debugger/LuaApi.cpp` `LuaApi::SetInput` consumes
`emu.setInput(button_table, subport, port)` with both numeric arguments.
The earlier internal JP0740 Lua observer called the two-argument form.
On the actual Linux MesenCE NativeAOT emulator, the two-argument form
left `emu.getInput(0).start=false` despite an intended historical
START button and all observed serial $4016 low bits zero. Explicit
`emu.setInput(buttons(original_p1), 0, 0)` and
`emu.setInput(buttons(original_p2), 0, 1)` cause the CPU to observe
the fourth START serial-read bit and reproduce the archived game transition.

At historical local frame **416**, exact original **CPU cycle
12,415,968** and RAM **$19=$04, player Y $041C=$AC** were reproduced;
at frame **664**, exact cycle **19,801,533**, RAM **$19=$03,
player Y=$88** reproduced. Input callback relocation and arbitrary
frame shifts were not needed.

Using an accelerated *private* Mesen Lua recorder with opcode-PC callbacks
limited to previously authenticated watched store sites, the complete
source write window **9,370–9,576** successfully executed with
**9,052** ordered bus events. All four independent historical
anchor pairs passed:

| Original local frame | Archived CPU cycle | New replay | Result |
| ---: | ---: | ---: | --- |
| 9,376 | 279,249,268 | 279,249,268 | exact RAM/cycle |
| 9,440 | 281,155,220 | 281,155,220 | exact RAM/cycle |
| 9,504 | 283,061,172 | 283,061,172 | exact RAM/cycle |
| 9,576 | 285,205,368 | 285,205,368 | exact RAM/cycle |

Source-private trace SHA-256:
`9f96aa2aa1a7d89fd7395fc47fcf7ff3fb0893f2b17daf39a416f304f4697a29`.
Its original replay footer was `END COMPLETE 9052 9576 4`.
No original ROM, replay input schedule, or private RAM dumps committed.

## Actual first corrected native input observation

The JP0719-native input file used the Mesen **absolute PPU frame count**.
Original JP0718 raw input recorded `absolute_frame=1685,
local_frame=1684, player1=RIGHT`. Existing original Mesen CPU
trace at local frame **1,684** reads $4016 serial bits:
`0 0 0 0 0 0 0 1`, repeated twice, and the original game writes
player action $0565 **$02→$04** from bank $0E:$961C in frame
1,684; X-coordinate $0438 advances **$20→$21** at bank $0E:$875B
in frame 1,685. The original owner archive itself has a valid
startFrame origin of **1** and 17,562 recorded polls.

Old native replay first reads RIGHT and writes
$28/$2A `00→01` at **native frame 1,685**; action and first X
advance are also one frame late. Reconstructing the private native
schedule in *recorded original local frame* coordinates instead of
absolute PPU frame coordinates moves the native RIGHT serial bit,
$28/$2A, action, and X writes into the **same respective frames**
as the original. Exact authenticated ROM-offset writer PCs match:
- player action original/native $0E:$961C (PRG physical $3961C);
- player X update original/native $0E:$875B (physical $3875B);
- start edge observed via original/native CPU bus $4016.

The corrected input schedule preserves **17,562/17,562** original
owner poll masks (zero mismatches) and has private SHA-256:
`43114d291d97b1ac7482fa6134a0953aeceea802718544b026e00b77d40a3d9c`.
`JP/decomp/tools/jp0743_native_input_epoch.py` is the tracked,
fail-closed archive-to-native local-frame converter; its original
START at local 393 and first RIGHT at local 1684 are now explicit
protected invariants. The old original-absolute schedule is
**not** a valid native replay input schedule.

## What parity has and has not been established

Corrected native replay completed in original mode, with a new
physically mapped CPU bus trace at native frames **1,650–1,840**
(`END COMPLETE 8402`). Archived original versus new native
frame-log comparisons show **zero differences in the selected
gameplay fields** at all original snapshot checkpoints inspected
from **1,624 through 6,000**. This does **not** establish byte-for-byte
whole-RAM equality; other RAM addresses and small CPU-cycle differences
remain. A corrected 9,370–9,600 native trace also completed with
`END COMPLETE 9897`, SHA-256
`3afab47b4606fb4b4b3fe809d72377fc6cf12612dddf5cceeef2cdf9ecb9b19e`.

**Remaining later native defect:**
At original frame **9,376**, selector remains original `00/01/02`,
but corrected native frame-log has `00/01/03`. Original retail event
trace records a selector decrement `$36:03→02` at frame **9,277**,
CPU cycle **276,275,916**. Its saved callback PC `$D3EB` is
**post-instruction**: actual physically mapped store opcode is
`DEC $36` at CPU **$D3E9** (original PRG physical **$3D3E9**).
The verified original Japanese 7-byte window PRG $3D3E9-$3D3EF
has SHA-256
`bcb3a6e0feafdb4a39a734717f56e432bf5b69295cb71957278ebb5bfb4ad696`.
A new authenticated original Mesen capture near the selector boundary
passed source RAM/cycle anchors **9,248** and **9,312**. At frame
**9,277**, its **actual** $D3E9 CPU read-modify-write produced
a dummy $36 03→03 at CPU cycle 276,275,915 and the real
$36 03→02 at 276,275,916. Source-private boundary trace
SHA-256:
`b74ce146d8f690e8d984fd00a41187a9ff2613775a26081c8b869eff29769c3f`.

**Do not blame $D3E9 yet:** the code branches on actor vertical speed
$0520, signed scroll high $65, and scroll position $54 before deciding
whether to decrement room selector $36; the native execution
decision near original frame 9,277 has **not** been instruction-level
cross-certified. The corrected schedule repairs early controller
timing, but does not yet reproduce the entire intended stage path.

## Evidence and next correction gate

A ROM-free GitHub Actions build of the opt-in Linux C11 NESRecomp
CPU-bus tracer is successful. Native writer logging has been extended
to watch $0036 and $0065, permitting a narrow private selector boundary
capture without publishing owner data. The final instrumented native
$36/$65 window execution is still pending a complete trace.
First establish its actual $D3E9 conditional branch, player vertical
speed $0520 and scroll $65 at the boundary. If a game behavior patch
is justified, require original opcode-ROM proof and owner-independent
replay parity regression before changing interpreted or native code.

**Last owner-performed gameplay test remains JP0722.** All the
work above is internal replay/testing. **Source metrics unchanged:**
VPP **31/100**, strict original PRG **49,504/262,144 bytes**,
admission checkpoint 0508. No new native gameplay opcode handlers.


## JP0744B — Actually executed original/native $36 boundary traces

After the initial report, the ROM-free Linux native observer from successful
Actions run `40139966851` was downloaded and executed with the corrected
**local-frame** controller schedule. Native bounds:
`JP0745_TRACE_FIRST_FRAME=9240`,
`JP0745_TRACE_LAST_FRAME=9312`. Run was completed with exit code 0
and `END COMPLETE 2998`. It observes actual mapped original-Japanese
interpreted guest bus writes to $36 and $65, not snapshots alone.

- Original MesenCE re-execution passed *exact* independent local-frame
  RAM/cycle anchors **9248 (275437361)** and **9312 (277343316)**.
- Original observed $36 CPU read-modify-write at local frame **9277**:
  CPU **276275915** `W $36 03→03` (6502 RMW dummy), then
  CPU **276275916** `W $36 03→02`; mapped opcode PC
  **$D3E9**, physical PRG **$3D3E9**.
- The corrected current native interpreter produced **no $36 writes**
  in its complete **9240–9312** CPU event trace. In particular,
  at native frame **9277** it writes unchanged scroll mode
  `$62:02→02` from bank $0E:$936E; it does not execute the
  original boundary decrement. This confirms the actual failure to
  enter the original room transition and is not an assumption from a
  nearby still image.
- At native frame **9248**, physically mapped actor routine
  bank $0E:$98A7 writes vertical speed
  `$0520:FF→FF`; the independently captured original Mesen RAM
  anchor at original frame **9248** has **$0520=$00**.
  Therefore a significant upstream vertical-motion state discrepancy
  exists before the missing room decrement. Neither the prior control
  input timing correction nor the original `DEC $36` opcode should be
  blamed without tracing the earlier actor/collision producer.
- The original room-boundary writer is a real RMW instruction at
  $D3E9; the original JP0718 raw event log's PC `$D3EB` was
  **post-opcode** and should not be treated as the write instruction.

**Unresolved:** root cause of the actor-speed difference and later room
transition. The selected gameplay state matches through original frame
6000; source/native parity after 6000 and before 9248 has not yet
been established densely enough to locate the upstream producer.

No speculative native actor/scroll patch was applied. Strict source
certification unchanged; last owner test JP0722.
