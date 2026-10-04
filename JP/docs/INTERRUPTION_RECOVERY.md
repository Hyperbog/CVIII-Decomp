# Interruption / restart recovery protocol

This file is mandatory reading after any timeout, chat/thread limit, token limit, tool interruption, process crash, or other loss of working context.

The goal is to resume from the last **committed, ROM-verified frontier** without silently trusting partial work and without re-counting or re-disassembling already closed bytes.

## Source of truth order

When recovering, trust sources in this order:

1. the authoritative JP ROM bytes;
2. committed audit tools and analysis artifacts;
3. `analysis/RESUME_STATE.json`;
4. `docs/DECOMPILATION_CONTINUITY.md` and `docs/PROGRESS.md`;
5. chat history only as a hint.

Never resume from an uncommitted conclusion merely because it appeared in chat. If an interruption occurred before a checkpoint was committed, restart that checkpoint from the last committed frontier.

## Mandatory recovery sequence

1. Confirm repository `Hyperbog/CVIII-Decomp`, branch `decompilation`, and fetch the current branch head.
2. Read `analysis/RESUME_STATE.json`, this file, `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`.
3. Compare the branch history against `last_completed_checkpoint_commit` in `RESUME_STATE.json`.
   - If the branch contains newer decomp commits, inspect them before doing new work. The resume state may be stale.
   - Never move the frontier backward merely because an older handoff document is stale.
4. Run `tools/check_resume_frontier.py <ROM.nes>`.
   - It verifies the whole-ROM SHA-256.
   - It verifies a small byte window immediately **before** the frontier against a committed SHA-256.
   - It verifies a small fingerprint beginning **at** the frontier, solely to prove the intended start address is aligned to the expected ROM bytes.
   - A mismatch is a hard stop. Do not continue analysis on a mismatched ROM/frontier.
5. Re-run the audit tool named by `previous_checkpoint_audit` in `RESUME_STATE.json` when practical. A failed prior audit is a hard stop until reconciled.
6. Resume at `next_unprocessed_cpu`. The pre-frontier overlap is verification-only and must **not** be counted as new coverage.
7. Carry forward only explicitly recorded machine state and unresolved edges. Do not recreate already closed static graphs unless a new dependency invalidates them.

## Overlap rule

Every checkpoint must leave a small verification overlap immediately before the next frontier, normally 32-64 bytes when addressable as one contiguous ROM span.

The overlap exists only to detect:

- off-by-one resume errors;
- wrong bank/window selection;
- accidental use of a different ROM revision;
- stale continuity documents;
- corruption or mistaken checkpoint accounting.

Overlap bytes are never new decompilation coverage. If a later checkpoint needs to semantically revisit them, state that explicitly and do not count them twice.

## Mid-checkpoint interruption rule

A checkpoint is not authoritative until its evidence is committed.

If interrupted after analysis has begun but before the checkpoint is completely committed:

- preserve any temporary notes only as clues;
- return to the last committed `RESUME_STATE.json` frontier;
- rerun the frontier checker;
- rerun or reconstruct the interrupted checkpoint deterministically from ROM bytes;
- do not advance VPP or the frontier from partially remembered results.

If some checkpoint files were committed but the progress/continuity/state files were not, inspect the intervening commits and their artifacts first. Complete/reconcile that checkpoint instead of starting a new one.

## Address and coverage accounting

For every new span record all of:

- raw VRC6 bank / CPU address range;
- physical 8 KiB PRG bank(s);
- contiguous byte count;
- any isolated probe bytes already counted by earlier checkpoints;
- exact **new-byte** count after subtracting overlaps/probes;
- SHA-256 of the dependency span;
- last closed CPU address;
- first unprocessed CPU address;
- unresolved pointer/call/bank edges.

Never infer progress from a visually contiguous range if control flow escapes it. Pointer-target closure and bank/parser state remain controlling.

## Checkpoint commit order

For each completed checkpoint:

1. commit the analysis artifact;
2. commit the reproducible audit/tool;
3. run the audit against the authoritative ROM;
4. update `docs/PROGRESS.md` and `docs/DECOMPILATION_CONTINUITY.md`;
5. update `analysis/RESUME_STATE.json` **last**, so it always describes the newest fully reconciled checkpoint;
6. confirm the branch head and report the checkpoint only after the above are present.

`RESUME_STATE.json` must include the prior completed checkpoint commit, the next frontier, verification overlap, next-frontier fingerprint, previous audit path, unresolved edges, and VPP.

## Current recovery frontier

At creation of this protocol, the last completed decomp checkpoint is **04F8**.

- raw bank: `$04`
- physical bank at frontier: PRG09
- last closed CPU byte: `$A011`
- next unprocessed CPU byte: `$A012`
- next checkpoint: **04F9**
- intended initial window: `$A012-$B1FF`
- do not open raw bank `$05` or fixed `$E7FB` during 04F9

The exact machine-readable values and hashes are in `analysis/RESUME_STATE.json`. Do not copy values from this prose if the state file has been advanced by a later committed checkpoint.
