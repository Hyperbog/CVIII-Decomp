# Interruption / restart recovery protocol

This file is mandatory reading after any timeout, chat/thread limit, token limit, tool interruption, process crash, model/context switch, long pause, or other loss of working context.

The goal is to resume from the last **committed, ROM-verified semantic frontier** without silently trusting partial work, skipping dependency bytes, or re-counting/re-disassembling already closed territory.

## Source of truth order

When recovering, trust sources in this order:

1. authoritative JP ROM bytes;
2. committed audit tools and analysis artifacts;
3. `analysis/RESUME_STATE.json`;
4. this file;
5. `docs/DECOMPILATION_CONTINUITY.md` and `docs/PROGRESS.md`;
6. chat history only as a hint.

Never resume from an uncommitted conclusion merely because it appeared in chat. If these sources disagree, freeze forward work and reconcile the disagreement first.

## Mandatory recovery sequence

1. Confirm repository `Hyperbog/CVIII-Decomp`, branch `decompilation`, and fetch the current branch head.
2. Read `analysis/RESUME_STATE.json`, this file, `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`.
3. Inspect recent commits newer than the checkpoint commit recorded in `RESUME_STATE.json`. Never force an older snapshot over a newer branch head.
4. Verify the exact ROM identity before any audit or edit.
5. Run `tools/check_resume_frontier.py <ROM.nes>`.
   - If the state is marked blocked/provisional, the checker must hard-stop forward work and print the required repair.
   - Otherwise it verifies whole-ROM identity, a committed pre-frontier overlap hash, and a fingerprint beginning at the intended next frontier.
6. Re-run the audit tool named by `previous_checkpoint_audit` when the state is ready. A failed prior audit is a hard stop.
7. Re-check a small semantic overlap immediately before the frontier as described below.
8. Resume only at the first unresolved **semantic unit**. The overlap is verification-only and must not be counted as new coverage.
9. Carry forward established code semantics and machine state. Do not recreate already closed graphs unless a new contradiction invalidates them.

## Exact ROM identity

The JP target is immutable:

```text
size       393232 bytes (0x60010)
SHA-256    958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
PRG CRC32  BA6BDD6A
CHR CRC32  BF15255C
mapper     24 / Konami VRC6a
```

Any mismatch is a hard stop.

## Overlap rule

Every checkpoint must leave and verify a small overlap immediately before the next frontier, normally 32-64 bytes when addressable as one contiguous ROM span.

Overlap detects off-by-one resumes, wrong bank selection, stale docs, wrong ROM revisions, accidental gaps, and corrupt byte accounting. Overlap bytes are never new coverage.

The byte overlap is necessary but not sufficient. The overlap must include a **semantic-unit check**:

- **6502 code:** decode from a known instruction start through at least the final complete basic block. Confirm the declared span contains every operand byte of every claimed instruction.
- **Streams / bytecode:** recursively re-decode at least the final previously closed root and its reachable control cycle. For `FB`/`FD`/`FE` sound streams, include loop anchors, call/return state, pointer targets, and every parameter byte read by the parser.
- **Pointer/table data:** re-check at least the final two proven entries, their complete encoded bytes, and their targets.
- **Banked execution:** reassert raw VRC6 bank, CPU window, and physical PRG mapping before interpreting addresses.

**Critical rule:** a command/instruction is not inside a verified span merely because its opcode byte is inside the span. Every operand/parameter byte that the claimed execution reads must also be inside the dependency accounting, or already be explicitly covered by an earlier verified dependency.

If the semantic unit crosses the recorded boundary, extend/correct the dependency boundary and byte ledger before any new work.

## Mid-checkpoint interruption rule

A checkpoint is not authoritative until its evidence and handoff state are reconciled and committed.

If interrupted after analysis begins but before that transaction is complete:

- use partial artifacts only as clues;
- return to the last committed recovery state;
- verify the overlap/frontier;
- reproduce only the affected incomplete semantic units from ROM bytes;
- **do not restart broad already-closed banks or graphs**;
- do not advance VPP or the frontier from remembered results.

If some checkpoint files are committed but progress/continuity/state files are not, inspect and reconcile those commits before starting another checkpoint.

## Address and coverage accounting

Use half-open ranges internally: `[start, end_exclusive)`.

For every checkpoint record:

- execution/mapping domain and CPU range;
- physical PRG bank(s);
- contiguous dependency byte count;
- isolated dependency/probe bytes outside that span;
- prior bytes that overlap the new dependency;
- exact genuinely new byte count after subtracting prior coverage;
- SHA-256 of the dependency span;
- last semantically closed address/unit;
- first unresolved address/root/unit;
- unresolved pointer/call/bank edges.

Calculate:

```text
contiguous dependency bytes
+ isolated dependency bytes outside that span
- bytes already counted by earlier checkpoints
= genuinely new ROM bytes
```

A byte probed earlier remains previously counted even when interpreted more deeply later. Conversely, a command cannot be declared closed if required operands lie outside its accounted dependency.

## Resume without treading old ground

After the recovery checks pass:

1. identify the first unresolved root/routine/table entry from `RESUME_STATE.json`;
2. re-read only the small overlap needed to prove alignment and semantic continuity;
3. reuse prior parser/code/table audits rather than rebuilding them;
4. follow only new dependency edges from the unresolved unit;
5. count only genuinely new ROM bytes.

Backward edges into an already-audited region should be verified against the existing artifact, not decompiled a second time.

## Checkpoint commit discipline

For each completed checkpoint:

1. run the new/updated audit against the authoritative ROM;
2. confirm the declared dependency span contains every byte actually read for the claimed closure;
3. commit/update the analysis artifact;
4. commit/update the reproducible audit/tool;
5. update `docs/PROGRESS.md` and `docs/DECOMPILATION_CONTINUITY.md`;
6. update VPP only if the fixed rubric earns it;
7. update `analysis/RESUME_STATE.json` **last** so it describes the newest reconciled frontier;
8. run `tools/check_resume_frontier.py <ROM.nes>` against that state;
9. re-fetch branch head before reporting completion.

If interrupted before all steps finish, the next session treats the checkpoint as provisional and repairs only the affected boundary/dependency.

## Repaired historical integrity hold

The 04F7/04F8 operand-boundary hold is **resolved** and must not block current forward work.

The restart checker previously found two four-byte `FE FF lo hi` commands whose operands crossed their original claimed spans:

```text
04F7 root $9133: $9208 FE FF 33 91 -> operands through $920B
04F8 root $9E85: $A010 FE FF 85 9E -> operands through $A013
```

The stream audits were hardened to require complete operand containment before reading parameters. The repaired 04F8 dependency is:

```text
half-open span:                  [$920A,$A014)
inclusive CPU range:            $920A-$A013
length:                          3594 bytes
SHA-256:                         728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
04F7 mode-probe overlap:         11 bytes
genuine 04F8 bytes:             3583
```

The hardened audits passed, the provisional invalid 04F9 work was discarded, and forward work resumed from the repaired `$A014` frontier. Later checkpoints 04F9-04FC were regenerated/advanced from committed ready states. The **current** authoritative frontier is always the one in `analysis/RESUME_STATE.json`; this historical section is informational only.

## Recovery rule in one sentence

**Verify the ROM and current branch, replay the last trusted audit, re-check a small overlapping semantic unit including all operands, repair any mismatch without redoing closed ground, and only then continue from the first genuinely unresolved unit.**
