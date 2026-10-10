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
