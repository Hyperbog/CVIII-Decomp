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
