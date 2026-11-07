# JP0745 - First A-pulse controller read anomaly

The exact-Japanese-ROM original MesenCE replay again passed private historical full-RAM/CPU-cycle anchors at local frames 6728 and 7336. A separate authentic native CYCFRAME v2 replay using the corrected zero-based input schedule was compared to dense original 2KiB RAM snapshots every eight frames. The first selected gameplay-state mismatch occurs at frame **6840**, preceded by an A+RIGHT pulse in local frame **6839**. These are genuine original/native ROM-at-launch executions, not synthetic smoke tests.

## Earliest watched action and controller-state differences

At original local frame 6839, both source and native CPU bus traces show the same sixteen $4016 reads, two complete eight-read groups:
41 40 40 40 40 40 40 41 (twice). The A and RIGHT bits therefore reach controller port 1 in both runs.

Controller port 2 differs in that frame: original MesenCE returns **$40 on all sixteen $4017 reads**, while native returns **$E0 on the sixth and $41 on the eighth** (the rest $40), at native CPU cycles **203669459** and **203669549**, respectively. This is an actual CPU bus mismatch, not an inferred input schedule discrepancy.

Original executes bank30 CPU **$E287** (physical PRG $3E287) writing press RAM **$28:00 to 80** at CPU cycle **203670015**, and bank30 **$E28B** updating held RAM **$2A:01 to 81** at cycle **203670023**. Native instead takes CPU **$E292** (physical PRG $3E292) and clears $28:00 to 00 at cycle **203669987**. Original player action source $0E:$95A2 writes $0565:04 to 06 in frame6839; native does so in frame6840. Original $0E:$9626 and $9636 advance $0565:06 to 08 and $05C1:01 to 00 in frame6840; native does both in frame6841. This matches first sampled frame6840 discrepancies: player X original 136 native137, action original08 native06 and collision/fall original00 native01. Vertical-speed and camera differences occur later.

Original ROM fixed-bank CPU **$E270-$E298** compares double-sampled input bytes $00/$02 and $01/$03. Different samples branch to the clear-press path $E290-$E298; equal samples execute controller press/hold update $E287/$E28B. The ROM itself is not the fault.

## Remaining root-cause isolation

The pinned NESRecomp implementation in runner/cyc/hw_machine.c contains CPU controller read treatment involving DMA, open-bus high bits and bus-driven values. Native $4017:$E0/$41 is a confirmed symptom contributing to the failed controller-sample equality test, **not yet a proof whether DMC DMA, OAM DMA, serial shift delay or incorrect internal/open-bus state is responsible**. A prior native wrong-branch at 6837 also requires comparison even though resulting $28 remains zero. Next trace should record native $00-$03 controller sample registers and DMA/controller shift/arbitration state near exact bad $4017 cycles before fixing any bus model. Do not replace $4017 by a constant or patch original Japanese game code speculatively.

Owner last manually tested JP0722. No native game logic or original-ROM bytes modified. Certification unchanged: 31/100 VPP; strict PRG 49,504/262,144.
