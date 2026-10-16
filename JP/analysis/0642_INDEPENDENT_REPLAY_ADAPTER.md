# JP0642 — Independent original-Mesen/native replay adapter

**Scope:** two independent, bounded, owner-private fresh-power-on runs.
The public repository and CI contain no copyrighted ROM, original game
screenshots, Mesen executable, commercial-generated C or savestate.

## Contract and orchestration

[JP0641](0641_SCENARIO_PREFLIGHT_CONTRACT.md) supplies the strict
versioned manifest, original JP ROM SHA-256 and native frame-change
input schedule. JP0642 maps `90 START` followed by `93 -` to Mesen's
inclusive `--input 0:start@90-92`. Combined buttons are sorted into
the Mesen CLI's comma-separated format. The native C11 program reads
the exact original file via `--input`; releases are preserved.

The CLI first verifies all pinned identities. Actual `--run` requires
a SHA-authenticated owner retail ROM, original Mesen agent binary with
manifest-pinned SHA-256, matching separately SHA-pinned MesenCore
runtime library, native C11 executable with manifest-pinned SHA-256,
and a new output folder **outside the source repository**. There is no
shell command interpolation and no cross-runtime savestate loading.

The Mesen command uses a private home, `--frames`, `--timeout`,
translated `--input` intervals, `--screenshot` and `--state-json`.
The native command uses `--edition original --frames --input
--hash-out --screenshot`. Each is invoked even when the other exits
unsuccessfully. Reference JSONL must contain exactly one NES
`loaded` event, one terminal successful `summary` with reason
`frame_limit`, no error events, zero stop code and the full frame
budget. The state JSON and 256x240 PNG are authenticated by SHA-256.
The native run reuses the JP0578 real per-frame hash/PNG validator.

### Commands

```sh
python3 JP/tools/test_jp_scenario_replay_0642.py
python3 JP/tools/jp_scenario_replay_0642.py \
  --manifest JP/scenarios/title-start-preflight.json

# Owner-local only: copy scenario JSON and schedule to a private folder;
# fill in reference.sha256 and native.sha256 in that private manifest.
python3 JP/tools/jp_scenario_replay_0642.py --run \
  --manifest "/private/scenarios/title-start-preflight.json" \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --reference-exe "/private/mesen-agent" \
  --reference-core-sha256 "<matching-MesenCore-so-hash>" \
  --native-exe "/private/jp_akumajou_densetsu" \
  --out "/private/jp0642-new-output"
```

The source sample is only a **300-frame title-input probe**, not a
confirmed title-to-village route. For a true scenario a developer
must populate both executable SHA-256 pins. Linux and Windows use
different MesenCore extensions (Linux `.so`, Windows `.dll`).
The private output folder contains both consoles' stdout/stderr,
captured original state and final PNG, native frame hashes/final PNG
and an identity-bearing `replay-report.json`. Do not publish it.

## Evidence status

A run-level `PASS` proves only that both independently launched
processes produced structurally valid results for the declared frame
budget. `first_execution_failure` identifies a failing runtime when
one does not complete. It is **not** a first game-state divergence.

Independent emulator and native frame hashes, frame boundaries,
CPU cycles and PNG encodings are not automatically comparable.
`cpu_trace_parity`, `rendering_parity` and actual first gameplay
divergence therefore remain **NOT_EXERCISED**. They need independently
aligned common observations and decoded image comparison (JP0643).
No genuine Mesen or native retail-ROM run was available to this
session. Only synthetic subprocess/negative fixtures and owner-ROM
JP0641 identity preflight ran locally; independent CI tests follow.

**Certification unchanged:** strict semantic PRG49,504/262,144
(18.8843%), VPP27/100, checkpoint0508, fixed PRG31 frontier
$FB96, R-002 OPEN.
