# Decompilation acceleration policy

This project should use every practical source and tool that speeds identification or verification while preserving exact Japanese-ROM behavior.

## Authority hierarchy

1. **Authoritative Japanese ROM bytes and observed execution** control behavior.
2. Reproducible ROM-backed audits, traces, and native parity tests are accepted verification evidence.
3. Hardware documentation such as NESdev constrains CPU/PPU/APU/VRC6 semantics.
4. External disassemblies, decompilers, CDL, NSF metadata, emulator annotations, and cross-version projects are secondary accelerators.
5. Guesses, inferred names, and semantic labels remain provisional until reconciled with the JP ROM.

No external source may silently override a JP-ROM disagreement.

## Approved accelerators

Use as appropriate:

- NESdev hardware and 6502 references;
- the existing Castlevania III disassembly in `cyneprepou4uk/NES-Games-Disassembly` as a structural/symbol oracle;
- `retrodisasm`, CDL, and execution traces for code/data and live-path evidence;
- Ghidra NES tooling for cross-references and graphing;
- other 6502/NES disassemblers or decompilers as hypothesis generators;
- `nesrecomp` architecture as a reference for eventual static recompilation/runtime design;
- the supplied NSF/M3U for audio correlation;
- automated JP<->US routine/table matching.

## Cross-version rule

US Castlevania III uses different mapper/audio hardware, so US addresses and mapper-specific behavior must never be transplanted blindly. Candidate matches should be classified as one of:

- exact byte match;
- relocation-only match;
- structurally equivalent;
- hypothesis only.

A candidate US symbol becomes an authoritative JP semantic label only after its JP routine/data structure and relevant call/data flow are reconciled against the Japanese ROM.

## Dynamic evidence rule

CDL and runtime traces can prove that a path executed under the recorded scenario. They do **not** prove that an unobserved path is impossible. Static producer/domain analysis remains required where absence/non-reachability matters.

## Decompiler rule

Decompiler output is never controlling evidence. It may accelerate routine recognition, but 6502 widths, flags, wrapping, stack behavior, interrupts, mapper state, shared zero-page state, and self-/data-dependent control flow must be preserved from ROM semantics.

## Automation priorities

Prefer building reusable tools that reduce repeated manual work:

1. JP<->US normalized routine/table matcher;
2. whole-PRG control-flow/reference atlas;
3. RAM-symbol candidate map with confidence/evidence tags;
4. CDL/trace import and annotation;
5. CPU/bank/interrupt trace-parity harness;
6. deterministic frame-state/image parity tests.

Acceleration tooling does not earn VPP by itself. VPP increases only when the fixed rubric's behavior/structure is supported by durable JP-ROM-backed evidence.
