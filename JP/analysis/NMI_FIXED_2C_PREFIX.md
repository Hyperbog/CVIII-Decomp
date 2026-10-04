# Superseded 04FF draft — fixed PRG31 nested `$2C` prefix

This artifact is retained only as a historical pointer. Its original semantic findings (26 in-window nested roots, 401 official instruction starts, 16 explicit local `$2C` writers, and 136 deferred exits) were useful, but its original **1005-byte new-coverage accounting was too broad**: it subtracted the prior `$F6AE-$F6E3` overlap from the entire raw `$F3DD-$F7FF` interval even though 74 additional bytes in that interval were not consumed by the admitted 26-root graph.

The controlling 04FF evidence is now:

- `analysis/NMI_FIXED_2C_HEAD.md`
- `tools/audit_nmi_fixed_2c_head.py`

Those artifacts account only instruction/operand bytes actually consumed by the strict bounded graph and prove exactly **931 genuinely new bytes**, ordered-manifest SHA-256:

```text
2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

The unclaimed raw gaps are kept explicit:

```text
F6AE-F6E3   54 bytes   already counted by 04FE
F706-F712   13 bytes   not reached by the 26 admitted roots
F724-F738   21 bytes   not reached
F782-F791   16 bytes   not reached
F7B7-F7CE   24 bytes   not reached
```

The last four gaps total 74 bytes and may later become semantically admitted through deferred/secondary dispatch targets, but they are **not** 04FF coverage merely because they are physically between `$F3DD` and `$F7FF`.

04FF remains incomplete/blocked: the live `$2C` producer domain, six deferred primary entries, secondary `$68` dispatchers, and mapper-selected callees are still open.
