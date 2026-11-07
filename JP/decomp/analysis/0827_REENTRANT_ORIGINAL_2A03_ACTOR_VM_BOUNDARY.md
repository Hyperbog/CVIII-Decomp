# JP0827 — Isolated reentrant 2A03 actor response executor

## Motivation and exact scope

The owner asked for **isolated, reentrant original-6502 actor execution**
as the next step toward genuine 426-pixel interactive Stage 1 enemies.
JP0826 had source-keyed native clocks, but no original code execution
outside NESRecomp's normal CPU. JP0827 introduces a separate
original-instruction executor with a private CPU, stack and memory.
**It does not yet execute a complete type-$3D AI frame or inject
projectile/damage/drop writes.**

All source-ROM evidence is from the owner-supplied Japanese
Akumajou Densetsu original cartridge SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
The original physical raw0B 16KiB SHA-256 is
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
No original ROM data is shipped or compiled in native sources.

## Real 6502 machine and boundary

`cviii_actor_vm_0827.h` implements a small but real 2A03
instruction fetch / decode / execute loop:

- Independent A, X, Y, P flags, PC, SP and private
  return-depth; private 2KiB CPU RAM with correct
  $0000–$1FFF 2KiB mirroring, and a **private $0100-page stack**.
- Original byte-addressed instructions fetched from an
  already-authenticated **physical raw0B bank** mapped as
  CPU $8000–$BFFF. Other unmapped I/O, PPU/APU, mapper,
  and fixed-bank addresses are **not accessible**.
- Original binary `SBC`, `CMP`, `CPY`, `LSR A`,
  `LDA`, `LDY`, `STA`, `AND`,
  branches, `JMP`, private-bank `JSR/RTS`
  and base flags. NES 2A03 decimal mode is ignored
  for arithmetic as on real NES CPU.
- Whitelisted original source ranges
  **$B486–$B4D6** and **$B525–$B53E** only.
  A first external JSR, unknown opcode, out-of-window
  PC, unapproved memory access or exhausted instruction
  budget stops before executing side effects. Input entry
  is only original `$B486` or `$B525`,
  real actor slots 1–18.
- The executor is **reentrant**: no global actor RAM,
  no mutable shared registers, no game CPU callbacks.
  It never changes live NESRecomp memory or sound.

### Original $B486/$B525 differential execution

The owner-private local C11 regression loaded the original
raw0B bank and compared **131,072** cases:
256 original actor types × 2 original attr-bit2 states ×
16 high-nibble damage magnitudes × 16 original health values.
Each case independently executed physical original
opcode bytes in the isolated VM and compared
`$0669,X`, `$067B,X`, original halt PC
and first external sound call against previous C11
`cviii_effect_b486_prefix_0821` and
`cviii_b525_prefix_0826` decisions.
All cases **passed** with original guest RAM unchanged.

The original VM executes `$B486` damage/HP code and
can branch into actual `$B525` type-specific
sound selection; it **stops at original JSR $E249
in $B53C**, with sound accumulator $27 for original
types $3D/$3E/$4B/$47 or $32 otherwise.
The nonfatal `$B486` branch previously stopped in
the conservative model at `$B4BC`. The VM
executes the additional source instruction
`$B4BC: LDA #$24` and stops at the actual
`$B4BE: JSR $E249`, with A=$24.
A positive branch is therefore not incorrectly
interpreted as a defeat.
Source outside those bounds (notably `$B4D7`,
`$B47B` and downstream `$E75A/$E249`)
is left unresolved and never forced.

The ROM-free CI test additionally validates private
JSR/RTS stack, zero-page isolation, prohibited PPU
bus access, unrecognized-opcode rejection,
external call trap and bounded loops. No source bank
or private test savestate is uploaded to CI.

## Actual game wiring

When loading the original owner ROM,
`cviii_stage1_host_0725.c` now SHA-checks and
retains its **raw physical PRG0B** in the private
Enhanced host alongside already-authenticated raw0A
horizontal source/PRG26 sprite banks. A wrong/mixed
bank disables the VM and zeroes its private ROM cache.

After each PPU/CPU-authenticated Stage1 frame,
the native world observes real source-linked type3D
allocations and invokes
`cviii_world_probe_vm_0827` only for those
**currently genuine original CPU actors**.
It creates a fresh private 6502 context from the
original RAM snapshot, executes the hypothetical
`$B486` call to its bounded original stop, compares
original source outcomes and records per-source stop PC,
status, probe count, matched/mismatched and deferred
effects. A disagreement is recorded and **never
becomes a guest RAM, collision or damage write**.

Crucial nuance: a per-frame snapshot probe is a
**counterfactual original-code evaluation**.
It does not prove the original game actually called
`$B486` on that frame. Nor does it implement
independent row32/type3D enemy AI or original projectile
hitboxes. It is an execution substrate for that next
step, not a completed native offscreen combat system.

Save-state/scene reset clears transient VM results
and source-link generations. ROM-derived source
and previously verified room geometry remain resident.

## Verification

- Owner-private original ROM: 131,072 independent
  raw-code versus C11 response comparisons passed.
- Separate Linux GCC and Clang ASan/UBSan synthetic
  instruction tests compiled/executed in
  `.github/workflows/jp0827_actor_vm_gate.yml`.
- Two CMake/CTest targets:
  `JP0827_Original6502VM` and
  `JP0827_PrivateWorldProbe`.
  World integration test constructs synthetic
  ROM-compatible RTS path, checks private VM counters,
  deliberately provides wrong code to verify mismatch
  rejection, then checks original-room/savestate reset.
  Windows alpha builder explicitly runs both.
- Gameplay/original 4:3 center unchanged,
  original source and CHR files not checked into Git.

## Remaining blockers before actor combat authority

1. Restore exact original type3D actor AI PC entry,
   timer/scratch use and action-frame calling convention;
   extend the private VM with only those proven original
   2A03 instructions and sandbox required read-only PPU
   collision context.
2. Give each offscreen instance its **own persistent
   writable 2KiB virtual CPU state** and validated
   game input/scroll/physics parameters, and execute
   the original actor action routine for the full
   width, rather than sampling the real guest state.
3. Compile/validate independent weapon/projectile
   slots and the full $B486->$B525->$E249 sound,
   $B525–$B5DE defeat/replacement, drops, score
   and pickup chains, including sprite/PPU coherence.
4. Perform controller-reached original Mesen vs
   virtual 6502 state and side-effect comparisons
   through spawn/contact/damage/deallocation.
5. Enable game-world writes and native OAM projection
   only after those invariants pass; preserve
   original-mode and savestate determinism.

Until then the **4:3 interaction restriction remains**;
no false claim of widescreen weapon hits, enemy spawns,
sound events or pickup parity is authorized.
Strict PRG 49,504/262,144 and VPP 31/100 unchanged.
