# JP0747 — DMC phase collision replay isolation (authentic retail evidence)

**Outcome:** Replayed the original Japanese Mapper24 ROM on both MesenCE and
current pinned NESRecomp via **corrected local-frame owner inputs**.
Identified a 53-CPU-cycle DMC fetch lead in the upstream native engine.
An opt-in +54 initial DMC timer probe restores both early collision sites
and watched player state through frame 7528. It does **not** restore whole-game
parity: another controller/DMA overlap at frame 7536 still differs, native
room transition is late, and the camera stalls at 9576. No production/gameplay
patch is justified yet.

## Proven original re-execution
Original Japanese ROM SHA-256:
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
MesenCE NativeAOT headless replay using explicit
`emu.setInput(buttons,0,0/1)` and the JP0718 owner poll log matched
**full 2048-byte CPU RAM and exact CPU cycle** at archived local frames
24, 264, 416, 6728, 9248, 9312, 9376, 9440, 9504, 9576.
This is internal automated testing, *not* owner gameplay beyond JP0722.

Original Mesen controller cycle-event callbacks and native CYC
`--trace-frame` establish:

| Event | Original Mesen CPU cycle | Native pinned baseline cycle | Difference |
| --- | ---: | ---: | ---: |
| DMC PRG read $C10B=$F5, local frame6839 | 203669511 | 203669458 | -53 |
| DMC PRG read $C081=$6A, local frame6879 | 204861559 | 204861506 | -53 |

At native frame6839 the DMC halt repeats the CPU's held $4017 address
for cycles 203669455–457, reads $C10B at 458, then resumes
$4017=$E0 at 459. The original does **not** have a controller read
glitch there and writes controller press $28=$80 and action $0565=$06
in frame6839. Baseline native instead executes ROM $E292 and delays the
action by one frame.

### Why globally suppressing DMA controller reads is wrong

An isolated read-halt suppression policy makes the first action pulse
pass, but authentic original MesenCE at frame6879 performs **19**
$4017 bus reads (including three overlapping DMA reads) and ends
with a $41 bit. In policy 1/3, those legitimate reads are suppressed,
causing **native to advance player state too early at frame6880**.
Production controller reads and DMA-halt behavior were left unchanged.

### DMC initial timer-phase probes

The original pinned NESRecomp source initializes the DMC timer to
`apu.dmc_timer=1022`. ROM-free CI experiment builds isolate counter
values 1074 (+52), 1076 (+54) and 1078 (+56) *without changing any
controller reads*. Exact authenticated private replay observations:

| Probe | $C10B DMC read native CPU cycle | Native $4017 frame6839 | Action frame6839 |
| --- | ---: | --- | --- |
| unchanged 1022 | 203669458 | $E0 6th, $41 8th | delayed |
| 1074 (+52) | 203669398 | sixteen $40 | delayed |
| **1076 (+54)** | **203669512** | sixteen $40 | correct |
| 1078 (+56) | 203669658 | sixteen $40 | correct |

The +54 probe puts the source DMC read only **one CPU cycle later**
than original. At frame6879 it puts $C081 DMC fetch at
**204861560** versus original **204861559**, and the native trace
also shows three held-$4017 DMA cycles and reproduces its real
$4017=$60/$41 glitch. The original/native watched gameplay-state
fields match for dense captured samples through frame **7528**.
Remaining few CPU-cycle differences and whole-RAM differences are
**not certified away**.

### Next failing checkpoint: 7536 — CPU instruction phase at DMA

Original CPU $4017 reads (16) all return $40 during the A+B+LEFT
pulse at frame7536. The source writes B press $28=$40 and actor
action $0565=$1A; native +54 writes $28=$00 and leaves action
$0565=$08. The DMC sample fetch is nearly cycle-aligned:

- Original source reads $C043=$FF at cycle **224431775**.
- Native +54 fetches $C043=$FF at cycle **224431776**.

But the **pending CPU bus address differs**:
- Original MesenCE observes CPU reads of **$E2B1** at cycles
  **224431772, 773, 774**, then the DMC sample at 775,
  then a clean **$4017=$40** read at cycle 779.
- Native CYC already fetched **$E2B1** at cycle
  **224431770**, opcode operands at 771–772, and then
  holds **$4017** on cycles **224431773–775**. After DMA
  byte read at 776, the actual CPU gets **$4017=$E1** at
  cycle 777 and the game takes the wrong press-clear branch.
- The same +54 build had correct watched gameplay through the
  dense sample at frame7528, so the next failing event is tightly
  localized to a CPU instruction/DMC arbitration phase difference.

The presence of a DMA fetch at an almost matching absolute CPU cycle
does **not** guarantee the CPU holds the same address. **Do not fix this
by replacing $4017 with a constant or suppressing all DMC-halt reads.**

### Long replay gates

With the +54 probe and corrected local input schedule, authentic frame
logs at the original's snapshot times give:

| Original local frame | Original state | Native +54 |
| ---: | --- | --- |
| 9248 | selector 00/01/03, camera X256 | same selector and camera; player X/Y each 1 off |
| 9277 | selector **00/01/02** | **00/01/03**, room decrement still late |
| 9312 | selector 00/01/02 | **same selector**, but some subpixel/X offsets |
| 9376 | camera X0 | camera X0; player X+1/Y-1 |
| 9440 | camera X10 | X9; action and $62 differ |
| 9504 | camera X49 | X48; Y/action differ |
| 9576 | camera **X93** | **X56**; stall remains |

This closes the false inference that the entire game was fixed by
the first DMC phase correction. It has *not* been resolved.

### Implementation and certification controls

Code (branch jp0723-ppu-queue-decoder, draft PR #13):
- `JP/recomp/tools/jp0746_controller_dma_probe.py`: separate mode1/2/3
  hypotheses; disabled by default after overcorrection established.
- `JP/recomp/tools/jp0747_dmc_phase_probe.py`: fail-closed pinned
  upstream C source probe only for offsets 52/54/56.
- `JP/recomp/native/rom_runtime_0732/CMakeLists.txt`:
  `JP0746_CONTROLLER_DMA_POLICY=0` and
  `JP0747_DMC_POWERON_PHASE_PROBE=0` by default. Ordinary production
  build remains **unchanged**.
- `.github/workflows/jp0746_controller_dma_experiment.yml` and
  `.github/workflows/jp0747_dmc_phase_probe.yml`:
  ROM-free build artifacts; private ROM/replay never uploaded to CI.
- Current required proof: find and correct the source/native CPU
  **instruction phase / DMC DMA halt arbitration** before frame7536,
  rerun through original room decrement frame9277 and camera9576,
  and preserve synthetic external NESRecomp conformance tests.

**No production hardware patch, no gameplay native handler additions,
no new byte admission. VPP 31/100; strict physical PRG
49,504/262,144; last owner gameplay test JP0722.**
