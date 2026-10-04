# Interruption-safe decompilation resume protocol

This protocol is mandatory after **any** interruption: chat/thread rollover, timeout, token limit, tool failure, model/session reset, user interruption, or any uncertainty about whether the previous checkpoint finished cleanly.

Its purpose is to prevent skipped bytes, duplicate work, stale assumptions, partial checkpoint claims, and accidental drift from the controlling ROM.

## Golden rule

**Never resume from conversational memory alone.** The repository and the exact target ROM are authoritative.

A checkpoint is either:

- **CLOSED**: evidence/audit artifacts and continuity/progress updates are committed, and the branch head was confirmed; or
- **OPEN / PARTIAL**: anything else.

Never promote an OPEN/PARTIAL result to a closed fact merely because a prior chat said it looked correct.

## Mandatory restart sequence

Before examining any new ROM bytes:

1. Read, in order:
   - `docs/RESUME_PROTOCOL.md`
   - `docs/WORK_STATE.md`
   - `docs/DECOMPILATION_CONTINUITY.md`
   - `docs/PROGRESS.md`
   - `docs/PROGRESS_METRIC.md`
   - `docs/ROM_IDENTITY.md`
2. Confirm repository `Hyperbog/CVIII-Decomp`, branch `decompilation`, and fetch the current branch head.
3. Verify the source ROM identity exactly. For the JP target:
   - size `393232` (`0x60010`)
   - SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
4. Read `docs/WORK_STATE.md` and identify:
   - last CLOSED checkpoint;
   - next checkpoint ID;
   - exact physical PRG bank / CPU address boundary;
   - overlap verification range + SHA-256;
   - prior audit(s) that must pass before forward work.
5. Re-run the last closed checkpoint's audit tool(s) against the exact ROM. If any audit fails, **stop forward progress** and reconcile the repository/ROM discrepancy first.
6. Verify the overlap bytes immediately before the next boundary against the hash recorded in `WORK_STATE.md`.
7. Inspect that overlap semantically enough to reconnect control/data state at the boundary. The overlap is verification context only; it is **not new coverage** and must not be counted again.
8. Only after steps 1-7 pass may new bytes be opened.

## Overlap rule

Every forward checkpoint must leave a small deterministic overlap fingerprint for the next checkpoint.

Default overlap:

- **64 bytes immediately preceding the next contiguous CPU/ROM boundary**, unless the semantic boundary requires a larger window;
- record physical PRG bank(s), CPU address range, byte count, and SHA-256 in `docs/WORK_STATE.md`;
- if a checkpoint uses isolated probes/non-contiguous bytes, record those separately and do not pretend they form contiguous coverage.

On resume:

- recompute the overlap hash from the controlling ROM;
- compare it exactly;
- inspect the final instructions/data grammar/pointer state crossing the boundary;
- then continue at the exact first **unclosed** byte/state.

Do **not** re-count overlap bytes toward the 500-5000-new-byte checkpoint budget.

## Coverage accounting rules

Maintain three distinct concepts:

1. **Closed contiguous bytes** — ROM ranges fully covered by the checkpoint's stated proof.
2. **Isolated probes** — individual bytes/roots read for metadata, mode, pointer, or domain proof outside the contiguous span.
3. **Semantic closure** — control/data states proven reachable and closed, which may differ from simple byte coverage.

Never merge these categories merely to simplify a progress statement.

For each checkpoint, record:

- checkpoint ID;
- physical PRG bank(s);
- CPU range(s);
- exact contiguous byte count;
- exact isolated-probe count, if any;
- overlap with prior checkpoints;
- exact **new-byte** count after subtracting overlap/already-counted probes;
- SHA-256 for each contiguous span;
- entry state / parser state / bank state assumptions;
- unresolved exits/dependencies.

## OPEN/PARTIAL checkpoint handling

If an interruption occurs before a checkpoint is committed as CLOSED:

1. Treat all chat-only findings as provisional.
2. Do not advance the checkpoint number.
3. Re-open from the last CLOSED boundary in `WORK_STATE.md`.
4. Re-verify the saved overlap and prior audits.
5. Reproduce the partial finding from ROM/tools before relying on it.
6. Continue the same checkpoint ID until it is either closed or explicitly abandoned/corrected.

If useful partial evidence had already been committed, it must be labeled `PARTIAL` in the artifact and in `WORK_STATE.md`; its byte ranges may be reused only after its audit is rerun successfully.

## Control-flow / disassembly safety

At every resumed boundary:

- carry physical bank + CPU address, not CPU address alone;
- carry parser/mode/state constraints when they affect dispatch reachability;
- carry recursive stream grammar state, loop anchors, call/return state, and pointer targets where applicable;
- do not seed impossible indirect edges just because bytes decode as pointers;
- do not infer code/data boundaries from plausible 6502 decoding alone;
- do not extend tables past proven producer domains;
- do not invent host-side bounds or defaults absent ROM proof;
- preserve exact 6502 widths, flags, wrapping, stack/interrupt behavior, shared zero-page state, and VRC6 banking/IRQ semantics.

## Commit discipline

A checkpoint is CLOSED only when all of the following are true:

1. ROM-backed analysis is complete for the checkpoint's declared scope.
2. Reproducible audit/tooling exists where practical and passes on the exact target ROM.
3. `docs/PROGRESS.md` is updated.
4. `docs/DECOMPILATION_CONTINUITY.md` is updated.
5. `docs/WORK_STATE.md` is updated with the **next** boundary and overlap fingerprint.
6. VPP is updated only if the fixed rubric actually earns a point.
7. All changes are committed to `decompilation`.
8. The branch head is fetched/confirmed after the commit.

If any item is missing, the checkpoint is not closed.

## Corruption / inconsistency response

If any of these disagree — ROM hash, span hash, overlap hash, audit output, recorded branch head, byte counts, or checkpoint ranges — do not guess which copy is right.

Instead:

1. stop forward work;
2. identify the last commit where ROM-backed audits pass;
3. reconstruct the disputed boundary from the controlling ROM;
4. correct continuity/progress/work-state documentation explicitly;
5. commit the correction before proceeding.

Corrections are preferable to silently preserving a bad assumption.

## No-treading rule

Once a checkpoint is CLOSED and its audits re-pass, do not redisassemble/recount its ranges in later checkpoints except for the small overlap needed to reconnect state or when a concrete contradiction requires reopening it.

Later work should start at the first unclosed byte/state documented in `WORK_STATE.md` and follow only live dependencies required to close the new question.
