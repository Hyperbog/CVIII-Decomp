# 0509 — ROM-free C++ actor/OAM pipeline research checkpoint

**Evidence scope:** executable native subsystem integration **without a ROM**.
A technical test fixture, **not the game**. Preservation-facing sources:
`src/actor_slot_0509.{hpp,cpp}`, `src/standalone_scene_0509.{hpp,cpp}`,
`standalone0509/CMakeLists.txt`, `standalone0509/README.md`, the prior
`src/oam_renderer.cpp` and `src/collision_math.hpp`.

## Independently matched original source architecture

The 0508 independent Mesen-based original-code proof had already credited
fixed physical PRG31 `$FF06-$FF11` (12 bytes), `$FF14-$FF55` (66 bytes) and
source/operand boundaries. The new native actor state lift creates no new
source credit. It reconstructs previously verified byte-level behavior:

- Fixed `$FF06`: `LDX #1`; test original RAM `$054E,X`; take first zero for
  `X=1..12`, returning `A=0` after BEQ into `$FF14:RTS`. When all 12 are
  nonzero, return `A=1, X=$0D` through `$FF12-$FF13`. The alternative
  `$FF12-$FF13` bytes remain **not credited as live source** despite known
  physical opcodes, consistent with the prior checkpoint.
- Fixed `$FF15`: clear exactly **four** RAM state arrays indexed by input X:
  `$04F2`, `$0509`, `$0520`, `$0537`. It does **not** clear `$054E,X`.
- Fixed `$FF24`: JSR `$FF15`, then clear **fourteen more** indexed arrays:
  `$067B`, `$068D`, `$0454`, `$0470`, `$0565`, `$04C4`, `$04DB`, `$05C1`,
  `$05D8`, `$05EF`, `$0606`, `$061D`, `$0633`, `$0645`. Neither the
  underlying helper nor the source ABI clears `$0400,X`.
- The actual ROM's 0508 authenticated chunks have SHA-256
  `$FF06-$FF11`: `c75f2332e11e13763245741d3f4ddb690f63dce3930c946cae3160090ac1488c`;
  `$FF14-$FF55`: `9f4374fdf490e30015a28e44abdc20c87259b501064c1d8eb9f4fee353d40d1a`.
  This audit enforces **78 original source bytes**, with the separate `$FF12-$FF13`
  return A=1 recognized but unclaimed, without embedding its game data.

## Executable integration and presentation contract

The independent `StandaloneScene0509` harness connects the **actual original
native OAM assembler**, the actual collision-distance primitive and this
newly lifted actor-state initialization/cleanup. It injects harmless synthetic
sprite set/frame pointer tables at 817F/9000/9020 and 9100/9140 and synthetic
CHR planar pixels with no likeness claim. It calls the actual original OAM
shadow algorithm, preserving its non-contiguous OAM slot progression `$C4`,
then renders the OAM result through a *host* 8x8 presenter to a 256×240 PPM.

Two synthetic 16×16 sprite composites are visible; the script can move the
left sprite, invoke `distance_below` and remove the second sprite. Those host
control rules are illustrative, **not Trevor movement, enemy AI, stage logic,
scroll, palette, sound or PPU timing**. The code never reads any original ROM.

## Regression acceptance

- Actor-slot scan: **4096/4096** occupancy combinations; all available slots
  and the none-found result checked.
- Actor-state clear: 4-field and 18-field RAM mutation maps checked for
  **256 X values each**; unrelated fields left unchanged.
- Real OAM lift: four-sprite descriptor/writes, 120-step deterministic
  synthetic timeline, exact pixels and two RGB hash goldens.
- Standalone native CMake builds one reusable library, one command-line
  preview and **two compiled C++ test executables**; CTest registers three
  ROM-free checks including a preview invocation.
- Optional local original-JP audit cross-checks source hash, exact 4+14 STA
  operand offsets and scan/JSR instruction boundaries. No original ROM/code
  data, screenshots, savestates or CDL are copied into Git.

**Checkpoint / rubric:** last completed certified semantic source checkpoint
**0508**, next research **0509**; strict PRG remains **49,504/262,144 (18.8843%)**;
VPP remains **26/100**. This new executable offers a practical test surface
for reconstructing real object movement and renderer output but **does not
satisfy playable-native-game or full hardware parity**.
