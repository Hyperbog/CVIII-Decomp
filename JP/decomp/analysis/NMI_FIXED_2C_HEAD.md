# Checkpoint 04FF — fixed PRG31 `$2C` nested-dispatch head

04FF is a **completed bounded checkpoint**, not a claim that the entire live `$2C` producer domain is closed. It closes exactly the fixed-bank nested target graph admitted by the 26 primary `$2C` table entries whose entrypoints lie in `PRG31:$F3DD-$F7FF`. The remaining primary entries, secondary `$68` dispatchers, and mapper-dependent callees are carried forward to 0500.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery boundary

04FE established the nested `$E7FB` pointer table at `$F39D-$F3DC`.

```text
$F39D-$F3DC  64-byte verification overlap
SHA-256      81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f

$F3DD-$F3FC  32-byte alignment fingerprint
SHA-256      65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa
```

The raw 04FF investigation window is `$F3DD-$F7FF` (1059 bytes), SHA-256:

```text
72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

Prior 04FE coverage `$F6AE-$F6E3` is never counted again.

## Admitted primary roots

The 32-entry nested `$2C` table has 26 distinct targets inside this window. Six encoded entries are deliberately carried forward:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

No table length is treated as a selector bound.

## Strict bounded graph

Recursive official-6502 decoding follows both sides of conditional branches. Fixed targets outside the window and CPU `$8000-$DFFF` targets are recorded as semantic exits rather than traversed under guessed mapper state.

```text
official instruction starts        401
unknown opcodes                       0
unique consumed instruction bytes   931
reachable store/RMW instructions     46
indexed/indirect store/RMW forms      0
```

Boundary exits:

```text
JSR -> CPU $8000-$DFFF       64
JMP -> CPU $8000-$DFFF        8
JSR -> fixed outside window   60
JMP -> fixed outside window    1
branch -> fixed outside         2
fallthrough -> fixed outside    1
```

## Exact genuinely-new manifest

Only instruction and operand bytes actually consumed by the admitted graph are counted:

```text
F3DD-F6AD   721   SHA-256 371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
F6E4-F705    34   SHA-256 cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5
F713-F723    17   SHA-256 4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300
F739-F781    73   SHA-256 b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac
F792-F7B6    37   SHA-256 b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1
F7CF-F7FF    49   SHA-256 13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574
```

Total genuinely new bytes: **931**.

Ordered-manifest SHA-256:

```text
2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

Unclaimed bytes remain explicit:

```text
F6AE-F6E3   54 bytes   prior 04FE coverage
F706-F712   13 bytes   not reached by these 26 roots
F724-F738   21 bytes   not reached
F782-F791   16 bytes   not reached
F7B7-F7CE   24 bytes   not reached
```

The older 1005-byte physical-prefix claim is superseded because it counted the final 74 unreached bytes merely from contiguity.

## Shared ZP `$10`

The admitted fixed graph has no direct ZP/absolute write to `$10` and no indexed/indirect store/RMW addressing form. Therefore **the bounded 04FF fixed graph preserves shared ZP `$10`**. This does not assert anything about the unresolved external callees.

## Local `$2C` transitions

Reachable fixed-side mutations are exactly:

```text
F3FF INC $2C
F443 INC $2C
F486 STA $2C
F4BF INC $2C
F4CF STA $2C
F4DC STA $2C
F4F3 STA $2C
F5CF INC $2C
F629 STA $2C
F635 STA $2C
F64F STA $2C
F6FB INC $2C
F716 INC $2C
F775 INC $2C
F7B4 INC $2C
F7DB STA $2C
```

ROM-local constant stores are bounded to the encoded state family. Conservative root association for the INC sites reaches at most primary entry `$1C -> $1D` locally. This is deliberately **not** promoted to the complete live `$2C` producer bound because external callees and six deferred primary entries remain open.

## 04FF result

**04FF closes 931 genuinely new fixed PRG31 bytes and proves the admitted 26-root fixed graph is ZP `$10`-safe.** It leaves the full `$2C` producer domain unresolved without blocking recovery: that work is explicitly moved to checkpoint 0500.

Reproducible audit: `tools/audit_nmi_fixed_2c_head.py`.

## Next checkpoint — 0500

Start the next raw investigation window at fixed `PRG31:$F800` and reconcile:

1. deferred primary entries `$F831/$F839/$F841/$F849/$F965`;
2. secondary `$68` inline dispatchers at `$F849` and `$F965` and their actual producer domains;
3. the four 04FF gaps `$F706-$F712`, `$F724-$F738`, `$F782-$F791`, `$F7B7-$F7CE` only if secondary-dispatch evidence admits them;
4. mapper-dependent callees only under proven VRC6 bank state;
5. whole-domain `$2C` writers/aliases before claiming `$2C <= $1F`.

VPP remains **21/100**.