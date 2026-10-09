# 0508 bulk: conditional state-$04 fork and hypothetical PPUSTATUS perturbation

**ROM authority:** Akumajou Densetsu JP SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. **Status:** bounded experimental mapped-CPU/PPU-timing research only; no physical-hardware gameplay trace, no semantic coverage promotion.

After reconciling a stale local pre-controller CPU source with the already committed controller-enabled source, rerunning the prior 480-frame start30 scheduler exactly reproduced **4,438,080 instructions and 475 NMI entries**, ending at raw bank $0C CPU $8A67. The experiment forks the same synthetic execution when `$18=$04` first occurs at modeled frame 421, step 3,892,701, PC $E553, RAM `$19=2/$2C=0`.

Seven forks from this identical state:

| Input or hypothetical stimulus | Further CPU instruction steps | Result |
|---|---:|---|
| start30 baseline | 545,379 | Frame 480, $18=$04, $2C=3 |
| Start held | 545,638 | Frame 480, $18=$04, $2C=0 |
| Start each 5 frames | 543,948 | Frame 480, $18=$04, $2C=3 |
| All buttons held | 545,638 | Frame 480, $18=$04, $2C=0 |
| Unverified PPUSTATUS sprite-0 bit 6 from scanline 0 | 4,432 | Unsupported opcode `$E3` at CPU `$0001`, frame 421 |
| Same hypothetical bit from scanline 80 | 4,432 | Unsupported opcode `$E3` at CPU `$0001`, frame 421 |
| Same hypothetical bit from scanline 180 | 4,567 | Unsupported opcode `$A7` at raw bank $0D CPU `$9F22`, frame 421 |

The four valid synthetic-controller continuations execute **2,180,603 additional instructions** combined and do not reach `$18=$0C/$0D`. The three **synthetic/unjustified sprite-zero injections are not valid game or ROM execution traces**; they only show that blindly forcing PPUSTATUS bit 6 is unsafe. This does not establish global non-reachability or a hardware sprite event model. The hot fixed `E04B-E054` CPU path is the ordinary main-loop arithmetic (`INC $20; CLC; LDA $20; ADC $1B; STA $20; JMP $E04B`), not evidence of a stuck CPU trap. Proper video/CHR/raster behavior and an external reference emulator remain the next needed dependency.

Run `python3 JP/tools/audit_0508_state04_hardware_sensitivity.py 'Akumajou Densetsu (Japan).nes' report.json` to regenerate the exact deterministic committed JSON report. No original ROM bytes are in Git. **VPP 25/100, strict PRG 49,404/262,144, completed checkpoint 0507, fixed PRG31 frontier FB96 all unchanged.**
