# JP0843: one-run seeded native route coverage measurement

JP0842 built the original Japanese mapper-24 cartridge with 6,716 bank-qualified recompilation seeds. A successful build alone does not prove executed native-code coverage. JP0843 runs that seeded executable **once** in headless Original/LLE mode, using only the existing JP0837 replay and hash/miss evidence. It does not run MesenCE or change guest input.

Windows owner-only invocation:

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
python .\JP\recomp\tools\jp0843_seeded_coverage_verify.py `
  --rom "C:\Tools\Mesen2\Akumajou Densetsu (Japan).nes" `
  --jp0837-dir "$env:USERPROFILE\Documents\jp0837-private" `
  --seeded-build "$env:USERPROFILE\Documents\jp0842-seeded-build" `
  --out-dir "$env:USERPROFILE\Documents\jp0843-private"
```

Before execution, validate original-JP ROM fingerprint, actual NESRecomp git checkout against pinned `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`, seeded executable SHA-256, original JP0837 provenance, original deterministic input schedule, and private seed content. Refuse to overwrite existing output. Save `seeded.hashes`, `seeded.misses`, `seeded.stdout`, `seeded.stderr` and `jp0843-report.json` privately.

Success requires exact native-state hashes for all 3,901 frames compared with prior unseeded native execution, and fewer interpreted ROM instruction hits on the identical route. Report native CPU cycle fraction, interpreted ROM/RAM cycle counts, remaining bank-qualified misses and first hash divergence, if present.

This is route-specific compiled-execution coverage, **not complete ROM recompilation, original-Mesen parity, or input serial-bus phase proof**. The earlier timing investigation remains closed. Synthetic `--smoke` was run locally; actual JP0843 seeded replay must run on the owner's private Windows machine.