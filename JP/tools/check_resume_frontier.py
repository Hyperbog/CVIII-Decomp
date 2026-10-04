#!/usr/bin/env python3
"""Verify the committed resume frontier before continuing a decomp checkpoint."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def mapped_slice(region: bytes, cpu_base: int, start: int, end_inclusive: int) -> bytes:
    assert cpu_base <= start <= end_inclusive < cpu_base + len(region)
    return region[start - cpu_base : end_inclusive - cpu_base + 1]


def main(rom_path: str) -> None:
    root = Path(__file__).resolve().parents[1]
    state_path = root / "analysis" / "RESUME_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))

    rom = Path(rom_path).read_bytes()
    rom_sha = hashlib.sha256(rom).hexdigest()
    assert rom_sha == state["rom_sha256"], (rom_sha, state["rom_sha256"])
    prg = rom[16 : 16 + 0x40000]
    assert len(prg) == 0x40000

    execution = state["execution_context"]

    def mapped_region_for(record: dict) -> tuple[bytes, int, str, tuple]:
        # Switchable 16 KiB VRC6 bank at CPU $8000-$BFFF.
        raw_name = record.get("raw_vrc6_bank")
        if raw_name is not None:
            raw_index = int(raw_name, 16)
            first_prg = raw_index * 2
            region = prg[first_prg * 0x2000 : (first_prg + 2) * 0x2000]
            assert len(region) == 0x4000
            label = f"raw bank ${raw_index:02X} / PRG{first_prg:02d}-PRG{first_prg+1:02d}"
            return region, 0x8000, label, ("raw", raw_index)

        # Fixed or otherwise explicit physical 8 KiB PRG mapping.
        physical = record.get("physical_prg_bank")
        if physical is not None:
            physical = int(physical)
            cpu_base_raw = record.get("cpu_base")
            assert cpu_base_raw is not None, "physical_prg_bank records require cpu_base"
            cpu_base = int(cpu_base_raw, 16) if isinstance(cpu_base_raw, str) else int(cpu_base_raw)
            region = prg[physical * 0x2000 : (physical + 1) * 0x2000]
            assert len(region) == 0x2000
            label = f"physical PRG{physical:02d} @ ${cpu_base:04X}-${cpu_base+0x1FFF:04X}"
            return region, cpu_base, label, ("physical", physical, cpu_base)

        # Backward-compatible fallback for older states.
        banks = execution["physical_prg_banks"]
        if len(banks) == 2:
            first_prg = banks[0]
            assert banks[1] == first_prg + 1
            raw_index = first_prg // 2
            region = prg[first_prg * 0x2000 : (first_prg + 2) * 0x2000]
            assert len(region) == 0x4000
            label = f"raw bank ${raw_index:02X} / PRG{first_prg:02d}-PRG{first_prg+1:02d}"
            return region, 0x8000, label, ("raw", raw_index)

        assert len(banks) == 1 and execution.get("cpu_base") is not None
        physical = banks[0]
        cpu_base_raw = execution["cpu_base"]
        cpu_base = int(cpu_base_raw, 16) if isinstance(cpu_base_raw, str) else int(cpu_base_raw)
        region = prg[physical * 0x2000 : (physical + 1) * 0x2000]
        assert len(region) == 0x2000
        label = f"physical PRG{physical:02d} @ ${cpu_base:04X}-${cpu_base+0x1FFF:04X}"
        return region, cpu_base, label, ("physical", physical, cpu_base)

    status = state.get("status", "ready")
    if status != "ready":
        print("ROM identity: OK", rom_sha)
        print("RESUME FRONTIER: BLOCKED", status)
        repair = state.get("repair_required", {})
        for reason in repair.get("reasons", []):
            print("-", reason)
        candidate = repair.get("candidate_dependency_span")
        if candidate:
            region, cpu_base, label, _ = mapped_region_for(candidate)
            start = int(candidate["start_cpu"], 16)
            end = int(candidate["end_cpu_inclusive"], 16)
            data = mapped_slice(region, cpu_base, start, end)
            digest = hashlib.sha256(data).hexdigest()
            assert len(data) == candidate["length"]
            assert digest == candidate["sha256"], (digest, candidate["sha256"])
            print(
                "repair candidate bytes: OK",
                label,
                f"${start:04X}-${end:04X}",
                f"({len(data)} bytes)",
                digest,
            )
        print("required action:", repair.get("next_action", "reconcile the blocked checkpoint before forward work"))
        raise SystemExit(2)

    overlap = state["verification_overlap"]
    overlap_region, overlap_base, overlap_label, overlap_key = mapped_region_for(overlap)
    ostart = int(overlap["start_cpu"], 16)
    oend = int(overlap["end_cpu_inclusive"], 16)
    obytes = mapped_slice(overlap_region, overlap_base, ostart, oend)
    assert len(obytes) == overlap["length"]
    osha = hashlib.sha256(obytes).hexdigest()
    assert osha == overlap["sha256"], (osha, overlap["sha256"])

    fp = state["frontier_fingerprint"]
    fp_region, fp_base, fp_label, fp_key = mapped_region_for(fp)
    fstart = int(fp["start_cpu"], 16)
    fend = int(fp["end_cpu_inclusive"], 16)
    fbytes = mapped_slice(fp_region, fp_base, fstart, fend)
    assert len(fbytes) == fp["length"]
    fsha = hashlib.sha256(fbytes).hexdigest()
    assert fsha == fp["sha256"], (fsha, fp["sha256"])

    frontier = state["frontier"]
    last_closed = int(frontier["last_closed_cpu"], 16)
    next_cpu = int(frontier["next_unprocessed_cpu"], 16)
    transition = bool(frontier.get("domain_transition", False))
    if not transition:
        assert last_closed + 1 == next_cpu
    assert oend == last_closed
    assert fstart == next_cpu

    if transition:
        assert overlap_key != fp_key, (overlap_key, fp_key)

    print("ROM identity: OK", rom_sha)
    print(
        "pre-frontier overlap: OK",
        overlap_label,
        f"${ostart:04X}-${oend:04X}",
        f"({len(obytes)} bytes)",
        osha,
    )
    print(
        "frontier fingerprint: OK",
        fp_label,
        f"${fstart:04X}-${fend:04X}",
        f"({len(fbytes)} bytes)",
        fsha,
    )
    print("last completed checkpoint:", state["last_completed_checkpoint"])
    print("last completed checkpoint commit:", state["last_completed_checkpoint_commit"])
    if transition:
        print(
            "safe resume domain transition:",
            overlap_label,
            f"${frontier['last_closed_cpu']} ->",
            fp_label,
            f"${frontier['next_unprocessed_cpu']}",
        )
    else:
        print("safe resume CPU frontier: $" + frontier["next_unprocessed_cpu"])
    print("next checkpoint:", frontier["next_checkpoint"])
    print("NOTE: verification overlap is not new coverage")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
