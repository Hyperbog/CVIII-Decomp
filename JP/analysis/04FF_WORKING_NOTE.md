# 04FF working hold

Checkpoint 04FF remains **blocked/in progress** from fixed PRG31 `$F3DD`.

Durable partial evidence is now committed:

- `analysis/NMI_FIXED_2C_HEAD.md`
- `tools/audit_nmi_fixed_2c_head.py`

That strict audit proves **931 genuinely new instruction/operand bytes** for the 26 nested-table roots whose entrypoints lie in `$F3DD-$F7FF`. It also proves the bounded fixed graph itself is ZP `$10`-safe and enumerates its 16 explicit local `$2C` writers.

The earlier `NMI_FIXED_2C_PREFIX.md` / `audit_nmi_fixed_nested_prefix.py` 1005-byte accounting is superseded: it counted 74 raw bytes not consumed by the admitted 26-root graph. The compatibility audit now redirects to the corrected 931-byte tool.

Do **not** treat this note or the partial 04FF evidence as full selector closure. `analysis/RESUME_STATE.json` must remain `blocked` until at least these open edges are reconciled from JP-ROM evidence:

1. six deferred primary `$2C` entries: `$08->$F965`, `$0B->$F831`, `$0C->$F839`, `$0D/$0E->$F841`, `$10->$F849`;
2. secondary `$68` inline dispatchers reached at `$F849` and `$F965` and their actual producer domains;
3. fixed/banked callees that can return before `$2C` transitions, under their actual mapper state;
4. the first-level `$18` producer domain remains separately open.

No table length is a producer-domain bound and no `$8000-$DFFF` target may be traversed under guessed mapper state.
