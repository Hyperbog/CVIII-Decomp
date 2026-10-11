# Agent rules — whole-bank / whole-subsystem work

1. State the **whole physical bank or complete runtime subsystem** being reconstructed; an isolated function is an internal step, not a checkpoint deliverable.
2. Preserve and authenticate original image bytes. Do not alter golden references or test expected results to improve a match. Keep original retail media out of commits.
3. Record all addresses as physical bank + mapped CPU location (or executable object + relocated address). Do not merge same-address routines from different mapper configurations.
4. Build a CFG and a closed byte-range partition; classify entries as confirmed code, typed data, unverified candidates, or unresolved. No speculative instruction promotion.
5. Generate bounded context: code/IR, callers and callees, RAM/global structures, side effects, metadata hashes, and prior matched analogues. Do not overload the agent with an entire cartridge source dump.
6. After every hypothesis, run compile/rebuild, exact comparison where applicable, and original-versus-native trace replay. Log the first divergence.
7. Three non-improving attempts on one hypothesis => pause that approach, write blockers, adjust method; **continue the bank-level goal**.
8. Use compiler-specific AST normalization/permutation only when supported and measured beneficial; tools written for MIPS/PowerPC/ARM cannot be presumed to work on 6502, Z80, or DOS Watcom LE.
9. Do not count `.byte` fallback, code-like byte patterns, embedded ROM copies, or unproven pointer roots as semantic progress.
10. Report separate outcomes: exact original-image rebuild, evidence-backed source understanding, native compilation, emulator/DOS versus native parity, and playable game state. Do not equate them.
