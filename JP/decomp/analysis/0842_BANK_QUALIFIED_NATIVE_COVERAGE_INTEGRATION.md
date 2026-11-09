# JP0842 — Consume real bank-qualified interpreter misses in the native build

## Scope and evidence

This change wires the **existing, private** JP0837 bank-qualified coverage into the **pinned** NESRecomp C11 compile path. No new Mesen capture, gameplay diagnostic, original-ROM mutation, upstream engine upgrade, or Enhanced rendering changes are required.

Original Japanese iNES mapper 24 ROM identity is SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; no ROM bytes, generated C, or privately recorded inputs are checked in. The owner previously reported **6,716 distinct interpreter-only ROM instruction starts**, **27 physical 4 KiB PRG banks**, and **10,917,746 interpreter miss hits** during a 3,901-frame native/interpreter run. Both execution modes produced identical frame hashes in that route. These are *recompilation coverage gaps*, not total executed PRG coverage or Mesen gameplay parity.

## Implementation

- `JP/recomp/tools/jp0842_seed_profile.py` consumes a **previously generated JP0837 directory** containing `jp0837-report.json`, `native.misses`, `native.hashes`, `interp.hashes`, and `jp0837-bank-qualified-seeds.txt`. It authenticates original ROM, the known JP0835 source/input fingerprints, pins the expected engine revision, verifies 3,901 native/interpreter hash rows are identical, and checks report counts against every miss-log entry. It validates `$E000-$FFFF` mapper 24 fixed physical 4 KiB bank identities and emits a canonical private `4k:BB:AAAA count` seed list and a provenance manifest.
- `JP/recomp/native/nesrecomp_cycle/CMakeLists.txt` accepts `JP_CYCLE_SEED_FILE` (default empty); when supplied it rejects missing or malformed seed data, then passes `SEED_FILE` to the existing `nesrecomp_add_cycle_game` target. No dependency is vendored, and the Original/Enhanced logic remains unchanged.
- `JP/decomp/tools/nesrecomp_cycle_0568.py` passes the optional validated seed file to CMake, **explicitly clears the seed option in ordinary unseeded builds** to prevent stale CMake cache entries, and records the seed count/digest in build metadata. Its CLI additionally supports `--seed-file` for direct, preprepared profiles.
- `JP/recomp/tools/build_retail_cycle_0575.py` supports `--jp0837-dir`; it prepares the verified private profile inside the private build folder, validates the pinned checkout, and compiles the normal native target with the seeds. The existing default without `--jp0837-dir` behaves as before.

## Build with existing JP0837 evidence (Windows PowerShell)

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
$rom = 'C:\Tools\Mesen2\Akumajou Densetsu (Japan).nes'
$source = "$env:USERPROFILE\Documents\jp0837-private"
$out = "$env:USERPROFILE\Documents\jp0842-seeded-build"
python .\JP\recomp\tools\build_retail_cycle_0575.py `
  --rom $rom --out $out --jp0837-dir $source --build-only
```

The build output contains `jp0842-bank-qualified-seeds.txt`, `jp0842-bank-qualified-manifest.json`, and the ordinary compiled `jp_akumajou_densetsu` executable/build metadata. No additional emulator test runs are requested. The build directory should be **new** to avoid changing existing private binaries.

For a preprepared seed profile with a separately managed engine, set `-DJP_CYCLE_SEED_FILE=/private/validated/jp0842-bank-qualified-seeds.txt` when configuring the CMake target, or pass `--seed-file` to `nesrecomp_cycle_0568.py`. Direct CMake validation authenticates the ROM and seed *syntax/physical bank identity*. Only the JP0842 private-profile preparation establishes the additional JP0837 provenance link.

## What these checks mean

The seed list adds bank-qualified discovery *candidates* to the native code generator. It does not itself prove the resulting executable compiled all seeds or eliminated all interpreter fallback. Further gains depend on normal CMake regeneration and the compiler's discovery/dispatch behavior. The source evidence does not prove full native coverage, all gameplay routes, controller bus parity, or equivalence to Mesen. VPP and strict PRG certification remain unchanged. Do not conflate interpreter miss entries with new strictly certified 6502/2A03 behavior.

## Automated checks

ROM-free `--smoke` checks canonical rendering and repository-output isolation. A local original-JP ROM check additionally confirmed generated profile parsing, the actual ROM identity, and rejection of incorrect fixed bank `$E000` mappings. The GitHub regression workflow executes the smoke check. No user-interactive emulator retesting is part of JP0842.