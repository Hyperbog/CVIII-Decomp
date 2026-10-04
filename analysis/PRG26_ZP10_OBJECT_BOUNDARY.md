# Checkpoint 04F1 — PRG26 cross-object ZP `$10` cache boundary

Scope of new ROM analysis: **512 bytes only**, `PRG26:$8000-$81FF`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

Window SHA-256:

```text
c45429bfae7777f783641b5206e41d501c67d96a4dee92f6b572961276a43f5a
```

## Proven renderer boundary

The main object loop calls `$8070` and then advances directly to the next object:

```asm
8031  20 70 80  JSR $8070
8034  E6 05     INC $05
8036  D0 DA     BNE $8012
```

There is no ZP `$10` initialization at this boundary.

Within the entire audited `$8000-$81FF` window, the renderer's direct ZP `$10` accesses are exactly:

```text
$8064  LDA $10
$80BF  STA $10
$811B  STA $10
$8166  LDA $10
```

The two loads are the compressed-record paths. The two stores occur only after a full record has supplied and transformed an attribute byte.

Therefore `$10` is not descriptor-local or object-local state. It is a persistent renderer cache that crosses object calls.

## Consequence for reachable descriptor `$9FA9`

Previous checkpoints prove the normal type-`$08` path reaches selector `$10` + frame `$14`, which resolves to descriptor `$9FA9`.

`$9FA9` begins with three compressed sprite records before its first explicit attribute. Those records therefore consume the `$10` value left by renderer history before this object begins.

The exact source is:

1. the final full-record attribute emitted by the highest lower-index object that rendered earlier in the same ascending slot walk; or
2. if no prior rendered full record has occurred, the pre-existing shared ZP `$10` value entering `$8001`.

The renderer itself does **not** supply a constant default for `$9FA9`.

This is the fidelity contract needed by the native lift. It is incorrect to reset `$10` at frame, object, or descriptor entry.

## Native regression

`tests/oam_renderer_test.cpp` now includes `test_cache_persists_across_object_boundary()`:

- object slot 0 emits one full record with final attribute `$23`;
- object slot 1 begins with one compressed record;
- the second object's first sprite must emit attribute `$23` and leave ZP `$10=$23`.

This locks cross-object cache persistence independently of the earlier test that seeded `$10` before the first object.

## Scope limit

This checkpoint does not attempt to enumerate every gameplay value that may be present in `$10`, nor every possible predecessor object for `$9FA9`.

It proves the lower-level machine contract: **the incoming attribute is intentionally inherited renderer state, not a constant associated with `$9FA9`.**

Reproducible audit: `tools/audit_prg26_cache_boundary.py`.
