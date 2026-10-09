# 03 — PPU/OAM Shadow Buffer and Sprite Descriptor Renderer

**Status:** PARTIAL; strong JP instruction/path evidence and native subsystem tests, no full-frame golden video parity. Primary studies: [NMI OAM frame](../analysis/PRG26_OAM_frame.md), [sprite format](../analysis/PRG26_SPRITE_FORMAT.md), [shared $10](../analysis/ZP10_OAM_STATE.md).

## Physical execution and shadow-OAM data flow

Fixed NMI $E0C2 selects raw switch bank $0D (physical PRG26/PRG27), then calls CPU $8001 = **physical PRG26:$8001**. The renderer constructs CPU shadow OAM in $0200–$02FF; the NMI later writes $02 to $4014 for 256-byte OAM DMA.

Raw bank $0D:$8001 loops over **28 object slots** X=$00..$1B. The $0400,X and $0470,X suppress conditions precede descriptor traversal; position/object fields include $041C,X, $0438,X, $0454,X and $048C,X. Zero-page $00–$03/$05/$07–$0F carry renderer-local state.

## Sprite-descriptor encoding

$8070 reads a table-selected pointer using $048C,X and pointer words at $817F; it follows a second pointer selected through $0400,X, then decodes variable-length sprite descriptors. A full entry emits OAM `Y,tile,attr,X` and replaces cached attribute **$10**; a compressed entry can emit `Y,tile,X` and **reuse inherited $10**. Bit6 of the attribute is horizontal flip; $8119 XORs it for transformed sprites. See [descriptor and attr evidence](../analysis/PRG26_ZP10_OBJECT_BOUNDARY.md).

Physical OAM has **64 entries of four bytes**. The JP code initializes $07=$40 slots and, after drawing active object sprites, fills remaining Y coordinates with $F4 (hidden). Sprite order is rotated using $22 = $22 + $44 modulo 256. Some terminal paths use stack unwinding to escape OAM-full conditions; native code must reproduce control effects, not only pixel geometry.

## Shared ZP $10 is a persistence contract

It is unsafe to initialize $10 to zero at renderer entry. Some full descriptors set it, compressed descriptors inherit it, and the pre-render collision helpers can alter it. Seven direct bank-$0B collision writes are explained in [0502](../analysis/NMI_BANK0B_COLLISION_ZP10_0502.md); five additional fixed PRG31 direct writes in [0504](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md). The **exact last writer for every frame remains OPEN**.

## Native and PPU boundary

Existing [native OAM](../src/oam_renderer.hpp) and [test](../tests/oam_renderer_test.cpp) cover established local descriptor behavior. This is not proof of complete PPU registers $2000/$2005/$2006/$2007, scrolling, CHR, sprite evaluation, scanline IRQ, or full frame parity. Refer to user-provided NESDoc, MOS 6500 manual and EveryNES for hardware checks; their generalized diagrams must not override JP ROM writes.

Next: derive complete PPU/scrolling producer domain, CHR banking during render, real frame traces with 256-byte OAM golden comparisons, and shared-attribute initialization/provenance.

## 0508 Phase 9 — bounded nametable clear port sequence, not frame parity

The [Phase 9 original-instruction witness](../analysis/0508_PHASE9_FINDINGS.md) executes fixed `$EB82` on its conditionally entered room-state-zero path, reading the 42-byte `$EC1D-$EC46` stream. The original command interpreter issues two groups of **1,024 zero-valued `$2007` writes**, starting at `$2000` and `$2400`, and returns to raw `$0A:$B589`. The audit checks 512 combinations of initial RAM seeds and PPUCTRL increment=1 or 32. In increment-32 mode the bus addresses alias; neither stream length nor write count certifies 2,048 distinct VRAM destinations there. PPUSTATUS=0, no rendering/scanline timing or actual reset-to-frame trace; do not confuse this VRAM path with sprite OAM (`$10` last-writer still OPEN). Previously counted fixed PRG code/data: 0 newly credited bytes.
