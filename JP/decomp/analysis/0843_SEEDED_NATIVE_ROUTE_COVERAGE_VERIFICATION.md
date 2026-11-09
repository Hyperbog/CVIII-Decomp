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

This is route-specific compiled-execution coverage, **not complete ROM recompilation, original-Mesen parity, or input serial-bus phase proof**. The earlier timing investigation remains closed. Synthetic `--smoke` was run locally; the owner's subsequent real Windows result is recorded below.

## Owner-confirmed Windows result — 2026-11-09

The owner executed the JP0843 tool on Windows with the original Japanese ROM, the existing JP0837 private replay, and the JP0842 seeded native executable. The owner-provided JSON output reports **\`status: pass\`**. These figures are recorded from that Windows output, not from a separate replay in GitHub CI.

| Metric | Reported result |
| --- | ---: |
| Compared native frame hashes | 3,901 |
| First seeded versus baseline native hash difference | \`null\` |
| Baseline interpreted ROM instruction-start hits | 10,917,746 |
| Remaining interpreted ROM instruction-start hits | 18 |
| Hits eliminated | **10,917,728 (99.9998%)** |
| Baseline distinct interpreted ROM instruction starts | 6,716 |
| Remaining interpreted ROM instruction starts | **1** |
| Remaining physical 4 KiB bank | **60** |
| Interpreted ROM cycles | **36** |
| Interpreted RAM cycles | **0** |
| Native CPU cycles | 116,171,309 |
| Total CPU cycles | 116,171,352 |
| Native cycle fraction | **0.9999996298571097 (99.9999629857%)** |

Provenance reported by the owner:

- Original-Japanese Mapper24 ROM SHA-256: \`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28\`
- Pinned engine checkout: \`2b4fcdb98c9e702be3fb365cfc645003c50b5fc1\`
- Seeded executable SHA-256: \`7381866f56d4b2eadb3c18501332fcd546b5e4f262ad2587346b01aa9f9afe3c\`
- Seed profile SHA-256: \`c1a80756bc841576d1c2709aadb599118391bd4d405bdb960d616e2c92fd3c83\`
- Baseline and seeded native per-frame hash-file SHA-256: \`86dd1152f5bddc3b9dbcab91ec02a5d0a8727705a2840c6d50b6609566b00d4d\`

**Disposition:** The targeted bank-qualified seed integration is effective on the previously captured 3,901-frame route, and the seeded native runtime reproduces the baseline native hash sequence. The single remaining interpreted entry (18 hits, 36 cycles) is not a blocking defect. Do not resume the closed Mesen timing investigation or add speculative opcode/mapper patches. No claim is made for full-game native coverage, independent Mesen parity, or input-bus phase matching. Private ROM and execution artifacts remain outside the repository.
