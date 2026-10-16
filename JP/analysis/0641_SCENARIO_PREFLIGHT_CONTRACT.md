# JP0641 — Deterministic gameplay replay scenario preflight (foundation only)

**Scope:** new JSON scenario contract and provenance validator. No game runtime,
Mesen binary, private screenshot, original ROM, extracted asset, or licensed
NESRecomp implementation is committed. This phase runs no emulator.

## Contract

The versioned `CVIII-JP-replay-scenario/v1` manifest explicitly specifies:
scenario ID; exact Japanese retail-ROM SHA-256; bounded 1–12,000 frames;
`power_on` start; internal Original + LLE baseline presentation; one
SHA-256-pinned `nesrecomp-frame-schedule/v1` ASCII input file; and reference
Mesen2 and native NESRecomp identities with nullable executable SHA-256 pins.
The example `JP/scenarios/title-start-preflight.json` is **not an observed
successful game route**: its two input changes are illustrative only.

The CLI rejects unknown/duplicated fields, unknown manifest versions,
incorrect ROM identities, unsafe input filenames, missing/symlinked or
oversized evidence, reordered/out-of-range frame events, unknown/repeated
buttons, changed input content, unsupported save-state starts, altered
baseline PPU config and executable identity drift. If a runtime executable
is supplied, its expected hash **must** be populated in the manifest.
The existing `nesrecomp_cycle_0568.authenticated()` function checks actual
retail ROM identity if `--rom` is supplied. It is not required by public CI.

```sh
python3 JP/tools/test_jp_scenario_preflight_0641.py
python3 JP/tools/jp_scenario_preflight_0641.py \
    --manifest JP/scenarios/title-start-preflight.json
# Private authenticated-ROM preflight, without running gameplay:
python3 JP/tools/jp_scenario_preflight_0641.py \
    --manifest JP/scenarios/title-start-preflight.json \
    --rom "/private/Akumajou Densetsu (Japan).nes" \
    --out "/private/jp0641_preflight.json"
```

Every report returns an explicit overall `PASS` (preflight only) or `FAIL`,
with separate `PASS`/`FAIL`/`NOT_EXERCISED` statuses. Original gameplay,
native gameplay, CPU trace parity, rendering parity and frame comparison
are **always `NOT_EXERCISED`** in JP0641; nothing about build correctness,
actual title-to-village success or original/native frame equality is inferred.

## Next phases

JP0642 may translate the same bounded input schedule into independently
validated reference-agent and native-runner inputs, attach pinned emulator,
compiled runner and runtime configuration identities, execute two separate
fresh starts, and compare genuine records at matched phase boundaries.
Only such independently captured evidence can change runtime-parity status.
Do not presume Mesen savestates and native savestates are interchangeable.
Use a verified scene from issue #1 as the first visible renderer regression.
The seven-layer SDL chain stays intact while executable behavior tests mature.

**Verification:** isolated ROM-free fixture suite and owner-ROM identity
preflight locally passed; separate Windows/Linux CI to follow. Historical
strict semantic PRG 49,504/262,144 (18.8843%), VPP 27/100, certified
checkpoint 0508, fixed frontier `$FB96`; R-002 **OPEN**.


## JP0641 Windows checkout SHA-256 portability correction

The first independent Windows CI run 38832650652 correctly rejected a checked-out sample schedule because Git's default Windows CRLF conversion changed the bytes relative to the committed LF hash. Linux CI and both synthetic negative-fixture suites passed. Scoped `JP/scenarios/.gitattributes` now enforces LF for scenario `.txt` and `.json` files. Input SHA-256 checks are **not** relaxed or normalized; a changed byte still fails validation. Re-run CI on the updated branch before claiming a cross-platform pass.
