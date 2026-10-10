# Checkpoint 0509 — actor allocation caller and gate, raw bank $0A

**Evidence class:** Provisional, original-ROM opcode execution under synthetic RAM. This is NOT original game-frame or emulator liveness.

## Original source chain

Physical PRG20/21 raw VRC6 bank $0A at CPU $8000-$BFFF; fixed PRG31 at $E000-$FFFF. The previously tested $90CA local allocation body has an immediate predecessor:

    $90C5  JSR $8CDD
    $90C8  BNE $9128

The actual $8CDD helper runs LDA $53; if nonzero, returns. Otherwise it reads LDA $07E0,X; if nonzero, returns. Only when both bytes are zero does it JMP $FF06, the fixed first-vacant-slot scanner (not JSR). The scanner RTS returns to the caller's $90C8 BNE because the $90C5 JSR stack frame is still active. The first scan therefore gates entry to $90CA. If all 12 actor slots are occupied, A=1 and the outer BNE skips $90CA.

On the successful branch only, $90CA then clears zero-page $10, invokes $FF06 a second time, sets $054E,X=$13, and zeros $05EF,X before exiting at $90F7. This source-only test leaves all other actor lifecycle and OAM effects unproved.

Four physical little-endian words starting at $90BD are $90C5, $8E50, $90DF, $8E50. Their source hash and values are audited. **They are a mechanical pointer slice, not proof of an executing dispatch or of the bound/index reaching this entry.**

## Byte integrity and execution results

The independent full-image ROM SHA is the established Japanese SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28. Three hash-locked raw-$0A regions:

- $8CDD-$8CE9 (13 bytes) SHA-256 c1cd8387e6e6a0d5b7b460de3b869f77a2df3f3e15debfca42152acb85a65b06
- $90C5-$90C9 (5 bytes) SHA-256 c4d9c294a87d2b82fb2efb9e47a394029126a5873d29aa87d20ccce5e95b176c
- $90BC-$90C3 (8 bytes) SHA-256 a0f96ee2ce69a443b2f4d418e753150f57c2dfa574137305abccae3b78d717b6

Original fixed scanner $FF06 is already hash-authenticated by the earlier actor ABI audit. The [bounded instruction runner](../tools/audit_actor_precheck_0509.py) tests **4096 occupancy masks x 3 mutually exclusive gate classes = 12,288 states**: 4095 allocation, 1 full, 4096 $53-blocked, 4096 indexed-$07E0,X-blocked. Incoming X varies across 1..12 in each test. All paths preserve exact scalar register results, selected RAM writes, no unrelated RAM mutation, and JSR/RTS stack balance. **188,332** original instructions executed at **25** distinct CPU PCs. Deterministic outcome SHA-256: 47fdbefa1de0cfc74889d9a04037c259ced20d22a186c8c0b18324ab3e74c263. [Machine report](0509_actor_precheck_report.json).

## Limits / next obligation

All inputs use deliberately synthetic RAM and an explicitly assumed raw-$0A mapping; no real original Mesen/CPU frame trace proves the dispatch reaches $90C5, nor is the $53/$07E0,X global producer domain closed. Real actor spawning, CPU/PPU/IRQ timing, image/audio parity, room $18/$19/$68 state and last $10 writer remain OPEN. Conditional static table candidates cannot be promoted solely from shape or synthetic execution.

No strict semantic PRG bytes promoted; **49,504/262,144 = 18.8843%**, VPP **26/100**, completed source checkpoint **0508**, fixed physical frontier **FB96** unchanged.

Run locally with the user-supplied authentic ROM:

    python3 JP/tools/audit_actor_precheck_0509.py 'Akumajou Densetsu (Japan).nes' --report /tmp/actor_precheck.json
