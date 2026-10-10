# 04 — Active Objects, Scheduler Ordering and Collision Scratch

**Status:** PARTIAL, with local B-level graph and F-level 8-bit math tests. Evidence: [0501 scheduler](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md), [0502 collision](../analysis/NMI_BANK0B_COLLISION_ZP10_0502.md), [0504 fixed helper](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md).

## Object index and scheduling

Fixed $FDEA sets X=$01; its ordinary object scheduler repeats until CPX #$13, visiting **18 slots $01-$12** (not all 28 renderer slots). In each visited active slot, mapper state selects raw bank $0B before $B1F8 collision/object interaction. Separate peer loop sets $9B=$14, increments until $17 and compares against object peers $14-$16.

Within a B1F8 invocation, candidate scratch writers appear in ordered families: early vertical/proximity, ordinary object/player hitbox, weapon/projectile probes, then peer/object interaction. The final writer is the **last qualifying executed path**, not necessarily the latest code address or a guaranteed write every frame.

## Collision scratch RAM contract

The seven direct raw-$0B `STA $10` instruction addresses are $B3B6, $B3D2, $B40E, $B460, $B65F, $B740, $B76C. They build 8-bit wrapped X/Y probe coordinates and feed distance/proximity routines, with $11 often the paired other coordinate. For instance $B3B6 computes $10 = objectX[X] + offset[$07] modulo 256, while $B3D2 constructs a Y coordinate from objectY[X] and its table. The writer domain is broader than raw-$0B because the fixed helper [0504](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md) directly writes $10 at $FBFC, $FC1F, $FC4F, $FCA0, $FCF9.

The fixed helper follows tile/background probe calculations. $FD25 uses a 12-byte modulo-reduced table at $FD4D–$FD58; independent `ORA $FD62,Y` is a separate, **unbounded live producer** and must read mapped memory even where the indexed address overlaps code. [0505 exact partial lift](../analysis/FIXED_TILE_PROBE_0505.md).

## Faithful native algorithms

[Collision math](../src/collision_math.hpp) and its [exhaustive test](../tests/collision_math_test.cpp) cover **65,536** 8-bit input pairs; use explicit unsigned wrapping, original borrow/carry and branch semantics rather than host signed abs/clamping. [Tile probe](../src/fixed_tile_probe.hpp) tests 524,288 index arithmetic combinations with real JP mapped fixed-ROM data but **does not execute full background collision state**.

## Open proof

A cross-frame/source-to-renderer $10 register-lifetime proof, complete $54/$14 producer bounds, and all collision/weapon/enemy subsystem behaviors are not yet complete. [UNKNOWN registry](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) tracks the missing guarantees.

## 0509 raw-bank $0A actor creation (provisional)

[ROM-stepped mapped actor allocation](../analysis/0509_ACTOR_SPAWN_PRODUCER_FINDINGS.md) executes CPU $90CA in raw bank $0A and authentic PRG31 $FF06 for 4,096 slot maps (73,717 original instructions). Locally, $10=0 before scanning; success writes actor type $13 at $054E,X and clears $05EF,X, while all-full branches to $9128 without those stores. No original frame/mapper-liveness or global $10 lifetime claim. R-004 remains OPEN. New strict bytes 0, VPP 0.

## 0509 raw bank $0A guarded actor spawn — conditional source behavior

[Original instruction-step precheck evidence](../analysis/0509_ACTOR_PRECHECK_PRODUCER_FINDINGS.md) establishes a local raw-$0A:$90C5 JSR $8CDD and BNE $9128 guard, before the existing $90CA/$FF06 actor allocator. If $53 or $07E0,X is nonzero, no allocation occurs; otherwise $8CDD JMPs to fixed $FF06, and only a free slot proceeds to the second slot scan and $054E,X=$13 / $05EF,X=0. The local source execution confirms 12,288 synthetic cases, 188,332 instructions with 0 PRG/VPP promotion. The four encoded pointer words at $90BD are not verified dynamic dispatch. **Real game-path/mapper reachability, source of both guard bytes and shared $10 final writer remain unresolved.**

## 0509 actor guard RAM producers (bounded source execution)

[ROM-stepped raw-$0A $07E0,X and fixed $53/$54 audit](../analysis/0509_ACTOR_GUARD_PRODUCERS_FINDINGS.md) tests all four direct raw-$0A `STA $07E0,X` encodings: `$8154` (carry-bit), `$82A5` (initial zero), `$83EE` (borrow-sign extension), `$8402` (add-sign extension, possible `$07C2,X` reset); `$83D1` direction selection uses `$65` sign. Existing fixed PRG31 `$FB7A/$FB88` increments/decrements `$53/$54` as a 16-bit word. **All 262,912 bounded cases pass**, 3,280,384 original source instructions. This narrows conditional input domains but does not show `$90C5` executes during gameplay, that no other bank/indirect/IRQ writer exists, or that shared ZP `$10` is the final renderer value. Strict PRG/VPP unchanged; R-004 OPEN.

## 0509 connected raw-bank-$0A object event scheduler and multi-slot creator

[Original-ROM source audit](../analysis/0509_ACTOR_DISPATCH_CHAIN_FINDINGS.md) joins raw bank $0A six-object scheduler $84EA, actual $8501 two-level indirect dispatch, $8CDD/fixed FF06 vacancy gate and actual $90C5/$90DF/$9133 spawn handlers. The audited source variants create 1/2/3 actors with different script, position, scratch and ancillary object fields. Under insufficient slots, earlier successful actors persist and the originating $07C8 event counter advances only upon complete success. 98,304 original-source bounded tests/6,174,946 instructions pass through the source RTI-independent JSR/RTS chain. No authentic reset-to-stage reachability, mapped bank lifetime across IRQ, continuation into $83D1 or final $10-to-OAM lifetime is established. VPP/strict PRG credit remain unchanged. R-004 and R-006 OPEN.

## 0509 independent emulator source-to-object proof (new B/A local event witness)

[Original Mesen2 Stage 1-02 live dispatcher](../analysis/0509_MESEN_ACTOR_LIVE_FINDINGS.md) demonstrates authentic raw bank-$0A $84EA and $84F3 JSR $8501 at frame 3092, with row $07C2,X=$32, event $07C8,X=0 and original guards $53=$07E0,X=0. The real indexed handler is $8B2C, invoking original fixed FF06/FF24 and creating **two live type-$3D objects**, advancing $07CB/$07CC to $11/$21; stage path and trace reproduce from a clean ROM boot. This **narrows** actor allocation/game-frame reachability, but not global source-input domains, the remaining synthetic $90C5/$90DF/$9133 paths, PPU/OAM last-writer truth, or native full parity. No new strict PRG or VPP claim; fixed FB96 frontier persists.

## 0509 live original source-to-actor RAM producers and input-policy feedback

[Seven-case bank-qualified Mesen regression](../analysis/0509_MESEN_ACTOR_FEEDBACK_FINDINGS.md) establishes actual PRG20 raw-bank $0A $8143 row-$32 writes at $07C5/$07C6, $8157 bit guards, $8182 event initialization, $84F3->$8501->$8B2C execution, actor $8D90 type-$3D stores and $8B71/$85DD event increments at $07CB/$07CC. The source five-byte descriptors are $A444 for X3 and $A43F for X4; actual mapped PRG offsets and hashes are in the owning report. Three jump-including real-controller policies reach the event and four finite routes do not. This closes a **single live input/producer path**, NOT complete scheduler rows, native parity or final shared $10 renderer lifetime; R-004/R-006 remain OPEN. Strict PRG and VPP unchanged.

## 0510 faithful C++ native execution: live type-$3D actor creation

[Original JP bank-$0A row-$32 native lift and two independent Mesen RAM matches](../analysis/0510_ROW32_NATIVE_LIFT_FINDINGS.md): raw source `$8501/$8B2C/$8D5E/$8DC1/$8D76/$8B50` plus fixed `$FF06/$FF24`, original bank-$0B `$A00F` indexed type attributes. It creates slots 1 and 2 with type `$3D` for source objects 3 and 4 during independent real Stage 1 frame3092; exact non-stack 1,792-byte RAM parity for each of two events. The actual max-three actor cap checks slots 1..8, different from scanner slots 1..12; failure overrides source event byte to `$02`. Guard/cap alternative states only native synthetic-verified; genuine alternate branch liveness remains OPEN. Not a completed frame or fully lifted scene; no new strict bytes/VPP and R-004/R-006 still OPEN.

## 0511 original raw $0B 2-axis actor velocity native code, no whole-frame claim

[Native reconstructed $8001->$8037 actor movement](../analysis/0511_ACTOR_MOTION_NATIVE_FINDINGS.md): original `$04C4/$0509` X fractional carry into `$0438/$04F2`, `$0470` ninth-bit and signed whole-speed extension; `$04DB/$0537` Y fraction into `$041C/$0520`. Both source type-$3D slots execute naturally at physical bank $0B during original Mesen gameplay, 60 total original CPU instructions; native matches both complete nonstack source RAM snapshots (3,584 bytes) plus source A/Y/P. 69,646 native mathematical oracle states pass. Private savestate and Mesen bootstrap limitation documented. Raw-$0B `$80FD` separate writer and actor script/AI source context remain OPEN. No PRG/VPP credit or closure of R-004/R-006; checkpoint 0508 persists.

## 0512 original actor post-velocity X displacement caller and lift

[Fixed `$FDF2` bank switch `$0B` → `$FDF8` JSR `$80E3` native source reconstruction](../analysis/0512_ACTOR_DISPLACEMENT_NATIVE_FINDINGS.md) follows the already lifted original `$0B:$8001` velocity path. Original `$80E3-$810E` horizontal branch signed `$6B` subtracts from `$0438,X` and updates the nine-bit X bit0 at `$0470,X`. 73,742 C++ bit/carry/status tests pass; two naturally reached type-`$3D` source Mesen calls match 3,584 non-stack physical RAM bytes and returned A/X/Y/P; physical source offset `$02C0E3`. This does NOT establish the `$65`-negative branch `$810F`, original `$B1F8` follow-up, full actor scheduling, renderer/OAM, R-004 shared `$10`, or strict PRG/VPP promotion. Preserve 0508 floor and fixed frontierFB96.

## 0513 original $0B vertical/actor-gate and type3B extra displacement (synthetic oracle)

[Source-backed C++ and independent Mesen instruction equivalence](../analysis/0513_VERTICAL_DISPLACEMENT_NATIVE_FINDINGS.md) covers `$65&$80` negative branch `$810F`, even `$8113` and odd `$8140` signed Y movement, source actor type `$054E` deletion gate and `$8843-$886B` type-$3B two-byte `$0606/$061D` adder. 270,351 ROM-free C++ checks; 54 ROM-authenticated but RAM/PC-injected original Mesen cases compare all 1,792 nonstack RAM bytes and A/Y/P per call. Natural 300-frame Stage 1 observer did NOT enter `$810F`; game-live producer remains unproved, global R-004/R-006 remain open. No certified PRG or VPP promotion; last completed 0508, PRG49504 and VPP26 remain.

## 0514 source producer / gate evidence, strict separation of index domains

[Original fixed-stage `$6B` producer and raw bank-$0B `$B1F8` actor gate](../analysis/0514_ACTOR_PREFLIGHT_NATIVE_FINDINGS.md): Mesen PRG30 `$03D30A` physically writes `$6B` from `$53-$08` for `$62>=2`, original bank0B `$02F1F8` gates actors on `$0470&$11`, `$0400`, `$054E` type with exits B1F7/B217/B258. 60 live Stage 1 frames show 59 `$6B=0` stores and 360 B1F8 entries across actors X1/2/14–17. Original PRG30 `$D066` direct `$65` producer reads indexed room data through `($0A),Y`; no `$65` stores in bounded 60- and 200-frame observed segments. Native two-routine slice matches 38 original-ROM cases (36 RAM-injected) over 68,096 nonstack bytes with A/X/Y/P, 100,357 native unit cases; actual B217 collision/postprocessing and `$65` high-bit gameplay domain still OPEN. Scheduler X1..17 differs from original allocator X1..12; do not conflate. R-004/R-006, strict PRG49504, VPP26 and fixed FB96 remain unchanged.

## 0515 B1F8→B217→B232 collision eligibility lifted in native source code

[Bounded original-Mesen collision-admission source audit](../analysis/0515_COLLISION_ADMISSION_NATIVE_FINDINGS.md): physical raw bank0B `$B217–$B231` reads `$7E/$7D`, `$054E,X` and `$0470,X` and transfers to `$B258/$B162/$B1D8/$B232`. 0514 B1F8 gate and new B217 gate are composed in native C++, tested by 82,947 ROM-free cases. Two **nonindependent windows on one natural actor X1** plus 56 injected Mesen configurations match 103,936 non-stack RAM bytes and all branch/register results. Original next actual collision `$B339` indexes tables `$BB05/$BB0E` and calls `$80B3`; none lifted here. R-004/R-006 and original full frame/PPU/APU parity stay OPEN, no strict PRG or VPP credit, completed 0508 metrics and fixed frontier FB96 unchanged.

## 0516 original collision-distance math and connected actor admission verified

[Source-backed native `$B339->$80B3/$80C1->$B393` collision math](../analysis/0516_COLLISION_MEASURE_NATIVE_FINDINGS.md) follows previously lifted fixed `$FDF8`/raw `$B1F8→$B217→$B232`. Original room `$7F` indexes `$BB05/$BB0E`, actor type indexes `$BB80/$BC08`, original vertical player offset `$B394` contains `00 05` (not `00 01`). 139,343 native C++ cases and 50 independent original Mesen differential windows pass (89,600 exact nonstack RAM bytes); 2 natural windows are from **same actor**, 48 cases force RAM to enter unobserved vertical states. Original `$B7/$E5BE`, `$B396` actor-specific path, and `$B235` collision result path are OPEN; R-004/$10 renderer, R-006, strict certification remain open. Certified 0508 floor PRG49,504, VPP26, frontier FB96 unchanged.
