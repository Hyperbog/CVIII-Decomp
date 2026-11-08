# JP0834 — original-JP Stage 1 synchronized actor-lifetime capture bridge

## What is verified

The owner-supplied Japanese Mapper24 cartridge SHA-256 and the Stage 1-02 physical raw0A/0B/0F source hashes passed the locally executed JP0833 source attestation. The new `jp0834_sync_stage1_capture.py --smoke` passed locally using **synthetic** ZIP and CYCFRAME v2 records. It detects loss of an authentic type-$3D source-linked actor in a sampled interval, rejects a mismatching continuation, and rejects truncated native logs.

## Private replay usage

The repository's original JP0718 Mesen capture ZIP contains one `-ram.tsv` with local frame/cycle/post-frame 2KiB CPU-RAM snapshots and one `-input.tsv` containing 17,562 original input polls. The existing JP0743 converter validates this capture's absolute-to-local frame epoch (including START at local 393 and RIGHT at local 1684), and generates the authoritative native input file.

With an owner-local compiled NESRecomp binary and that **same actual original-Mesen capture**, run:

```sh
python3 JP/recomp/tools/jp0834_sync_stage1_capture.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --owner-capture /private/JP0718-original-capture.zip \
  --native-exe /private/jp_akumajou_densetsu \
  --out-dir /private/jp0834
```

The bridge runs the native executable from power-on with the JP0743 converted controller schedule, `--edition original`, `--frame-log-at mesen`, and frame samples taken **only** where authenticated owner-Mesen snapshots show room `00/01/00`. It verifies native `CYCFRAME` v2 headers/lengths, requires matching frame indices, and exports private JP0833 JSONL pair and a summarized actor lifetime report. A source actor must be observed for **both** original phases 3 and 4 before a sampled actor-lifetime result can pass.

For existing native logs, `--native-frame-log` can diagnose mismatches but deliberately **cannot certify synchronized execution**, because CYCFRAME does not prove which input schedule the external invocation consumed. That mode exits nonzero even when sampled RAM matches.

All outputs contain private game state and are created exclusively in the caller's private output directory (mode 0600); do not commit, attach to public CI or upload the cartridge, owner input, emulator state or frame logs.

## Claim boundaries

A successful paired check means only: the same authenticated original replay input was given to the native executable, all selected original Stage 1-02 post-frame snapshots and their watched actor RAM fields agree, and sampled original source-child presence/loss intervals match. It does **not** identify actor writer PCs, establish identity between sparse snapshots, certify continuous offscreen actor behavior, prove original $B727 contact/$B525 defeat, or certify CPU/PPU/VRC6/audio parity.

**This task did not execute a fresh owner-Mesen/native synchronized game replay:** the private JP0718 capture ZIP and Mesen/native executables were not installed alongside the original ROM in the environment. No gameplay parity certificate, VPP or strict PRG coverage change is claimed.
