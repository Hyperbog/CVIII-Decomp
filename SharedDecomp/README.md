# Shared decompilation / native-parity evidence gates (v1)

This is **working**, standard-library-only cross-project tooling for source auditing and original-versus-native regression. It is not an emulator, ISA translator, Ghidra bridge, or proof of a complete native recompilation.

Use the same `workflow.py`, `test_workflow.py`, schema and acceptance thresholds in NES, SMS/Z80, and DOS/Watcom repos. Original media, commercial source bytes and licensed assets are never committed.

## Executable commands

```sh
python3 -m unittest discover -s SharedDecomp -p 'test_*.py' -v
python3 SharedDecomp/workflow.py bank path/to/bank-map.json --bank-bytes /local/physical_bank.bin
python3 SharedDecomp/workflow.py cfg path/to/mapper-aware-cfg.json --map path/to/bank-map.json
python3 SharedDecomp/workflow.py context path/to/bank-map.json --cpu 801E --radius 0x100 --report /tmp/packet.json
python3 SharedDecomp/workflow.py diff /tmp/original.jsonl /tmp/native.jsonl --report /tmp/first_divergence.json
python3 SharedDecomp/workflow.py attempt /tmp/candidate.json --hypothesis room-loader --score 0.87
```

### Bank map schema

- `schema_version`: `1`
- `bank`: `{ "physical_id": "NES:JP:VRC6:raw0A", "cpu_base": "8000", "size": 16384, "sha256": "..." }`
- `segments`: ordered, **gap-free, overlap-free** list of `{start: "8000", end_exclusive: "8010", type: "code|data|unknown", evidence: "...", source?: "audit-name", scenario?: "trace-ID", sha256?: "..."}`
- Evidence enums: `TRACE_EXECUTED`, `STATIC_PROVED`, `PRODUCER_TYPED_DATA`, `STRUCTURAL_CANDIDATE`, `RAW_FALLBACK`.

Only the first two evidence classes count as **confirmed instruction bytes**; only the first three as source-backed **semantic evidence**; even those do not establish **native runtime parity**. A `RAW_FALLBACK` is always unknown. A `STRUCTURAL_CANDIDATE` never gains strict code credit. Evidence references and scenarios are required for certified ranges.

Bank map physical IDs are not CPU addresses: switching bank at the same `$8000` CPU window gives distinct identities. `--bank-bytes` verifies SHA-256 of the locally supplied physical bank and optional per-segment hashes. For a full-ROM format, extract and authenticate banks with the platform-specific adapter first.

### Physically qualified CFG schema

`{ "schema_version":1, "nodes":[{"id":"raw0A:801E", "physical_bank":"NES:JP:VRC6:raw0A", "start":"801E", "end_exclusive":"8024"}], "edges":[{"source":"raw0A:801E", "target":null, "status":"unresolved", "reason":"runtime indirect address open"}], "roots":["raw0A:801E"] }`

The validator rejects duplicate and overlapping blocks in the same **physical** bank, invalid resolved targets, and missing explanations for unresolved/external edges. It reports open edges; it **does not** infer an observed game entry merely from a plausible pointer.

### Execution traces

One deterministic JSON object per line, aligned on a common logical `step`. An NES 6502 record may include:

```json
{"step":0,"physical_bank":"raw0A","pc":"801E","registers":{"A":0,"X":0,"Y":0,"SP":253,"P":36},"mapper":{"prg8000":"0A"},"memory_writes":[{"addr":"0004","value":"94"}],"hardware_events":[]}
```

Use corresponding Z80 flags and slot registers for SMS, or DOS x86 registers/fixups/services for Ravenloft. The comparator checks **all non-timing fields**, including physical bank/mapper/writes, and emits the **first divergent step and top-level field**, not a fabricated percent match. The source and host runners must emit comparable **logical step boundaries**; mapping native implementation events to those boundaries is adapter work and is **not supplied by this package**. Do not report a native match using synthesized or self-copied traces. Empty traces explicitly fail.

### AI bounded loop

`attempt` persists an append-only score history for a named hypothesis. Three consecutive non-improving scores (configurable) yield `STOP_AND_DIAGNOSE`, a non-zero exit code. This stops that **hypothesis**, not the overall bank/subsystem deliverable. Do not alter original bytes, source audit goldens, expected output or compiler flags to hide a divergence. Compiler-specific permutation is optional; it is not an off-the-shelf solution for 6502/Z80.

### CI and native port definition

- ROM-free tests must pass on all applicable repository commits.
- ROM-backed identity/reassembly and differential replay must run locally with **user-supplied** original media; never silently claim CI ran those jobs.
- Completion requires mapped entry proofs, data/CFG closure, native implementation and reference-versus-host replay of declared scenarios. A byte-identical bank with unresolved candidate bytes is **not complete**.
- For DOS/Watcom, matching exact linked LE bytes and running a native Windows executable are independent objectives with separate acceptance reports.
