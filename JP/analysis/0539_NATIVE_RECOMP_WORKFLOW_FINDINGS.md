# Whole-bank 0A -> native matching infrastructure (0539)

This checkpoint introduces shared cross-project evidence/replay gates and **one genuine native C++ translation** of the original Japanese Castlevania III raw0A `$801E–$8046` three-level room selector routine. It deliberately does **not** claim a complete bank or native game port.

## What is implemented

1. `SharedDecomp/workflow.py`: exact physical-bank partition validation; candidate-versus-proven byte accounting; mapper/physical CFG edge validation; bounded AI context; deterministic first-divergence JSONL trace comparison; persistent three non-improvement hypothesis guard.
2. `JP/tools/export_0538_bank_workflow.py`: converts the entire 0538 bank atlas to the shared evidence schema, rejecting changed original ROM identities, unrecognized kinds, broken census, gaps/overlaps, altered range SHA-256 (when original ROM supplied). Bank `raw0A` SHA-256 remains `1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.
3. `JP/tools/native/raw0a_lookup_native.cpp`: portable C++ translation of original stage -> middle -> leaf pointer selection. No embedded retail game code or assets. Native program accepts a local 16,384-byte bank binary and bounded selector TSV; outputs deterministic semantic JSONL records.
4. `JP/tools/native/replay_raw0a_native.py`: authenticates original Japanese retail ROM SHA-256, executes the existing instruction-exact 6502 reference `test_raw0a_lookup_cpu.run` on all 135 0538 selector triples, runs the compiled C++ translation for the same inputs and uses the new independent trace-differ to compare pointer results. Emits two replay traces and a first-divergence report.
5. ROM-free unit tests (shared core + target adapter + C++ native compile smoke), integrated into repository regression gates. Original user ROM stays local; public CI reports only ROM-free successes.

## Actual original-ROM test executed in local working tree

- Original Japanese retail image SHA: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- Complete bank-level partition: 16,384 bytes, SHA verified.
- **2,162 confirmed 6502 instruction/operand source bytes** and **168 previously audited data bytes**.
- **2,910 candidate code bytes**, **7,460 structural-only game-data bytes** and **3,684 unresolved bytes**, excluded from confirmed-code totals.
- Native lookup vs instruction-exact reference: **135/135 semantic pointer results match**, including all three intermediate pointers.
- `actual_gameplay_frame_parity = false`; `mapper_and_hardware_events_verified = false`.
- Whole-ROM exact reassembly remains an independent prior 0538 result; no new strict PRG bytes added (49,504/262,144), VPP 27/100 unchanged.

## Local reproduction

```sh
python3 -m unittest discover -s SharedDecomp -p 'test_*.py' -v
python3 JP/tools/export_0538_bank_workflow.py --smoke
python3 SharedDecomp/workflow.py bank JP/analysis/0539_RAW0A_BANK_MAP.json
python3 -m unittest discover -s JP/tools/native -p 'test_native_lookup_smoke.py' -v

# Original user-owned Japanese ROM, required for independent ROM/CPU vs C++ execution:
python3 JP/tools/build_fullbank_0a_source.py --rom "$JP_ORIGINAL_ROM" --out /tmp/jp-0539
python3 JP/tools/export_0538_bank_workflow.py --atlas /tmp/jp-0539/raw0a_hierarchy_atlas.json --rom "$JP_ORIGINAL_ROM" --out /tmp/jp-0539/workflow
python3 JP/tools/native/replay_raw0a_native.py --rom "$JP_ORIGINAL_ROM" --cases /tmp/jp-0539/raw0a_bounded_selector_cases.json --out /tmp/jp-0539/native-parity
```

### What is still missing

- Actual Mesen gameplay traces proving entry to `$801E` and full selector producer ranges.
- Mapper/PPU/APU cycle, interrupt, RAM object-copy and game-frame parity.
- Native execution of the rest of raw0A (still **2,910 code candidates** and **3,684 unresolved bytes**).
- A complete native Castlevania III engine and playable whole-game recompilation.

The cross-project core is architecture-neutral and is also installed on RLOFT for original-vs-host trace comparisons once a real DOS execution capture and matching native Windows event adapter exist. It is **not** a claim of complete DOS parity.
