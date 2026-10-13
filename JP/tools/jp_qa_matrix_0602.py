#!/usr/bin/env python3
"""JP0602: assess private labelled Japanese gameplay CHR/PPU evidence.

Reads metadata and diagnostic CSV only: never a ROM or extracted art.
Validates provenance claims, file integrity, sampled fetch/frame alignment
and coverage. This is NOT a retail-play certification or renderer comparison.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
from pathlib import Path
from jp_chr_fetch_report_0600 import FIELDS as FETCH_FIELDS, invented_row, summarize as summarize_fetch
from jp_frame_evidence_report_0601 import EVIDENCE_FIELDS, analyze

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SCHEMA = "CVIII-JP-QA-capture/v1"
AREAS = ("title", "village", "clock_tower", "forest", "ship", "castle", "boss", "companion")
CHARS = ("Trevor", "Sypha", "Grant", "Alucard", "None")
KINDS = ("title", "gameplay", "boss", "cutscene", "recruitment")
FILES = ("CVIII-CHR-Audit.csv", "CVIII-CHR-Fetch.csv",
         "CVIII-Frame-Evidence.csv", "CVIII-CHR-Fetch.json",
         "CVIII-Frame-Evidence.json")
SHA = re.compile(r"^[0-9a-f]{64}$")
SCENE = re.compile(r"^[a-z][a-z0-9-]{2,47}$")
ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$")


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(262144), b""):
            h.update(chunk)
    return h.hexdigest()


def read_scene(folder: Path) -> dict:
    manifest = folder / "capture.json"
    if manifest.is_symlink() or manifest.stat().st_size > 65536:
        raise ValueError("Missing or unsafe capture manifest")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    keys = ("schema", "capture_id", "scene", "area", "character", "kind",
            "rom_sha256", "game_exe_sha256", "asset_index_sha256", "files")
    if not isinstance(data, dict) or any(k not in data for k in keys):
        raise ValueError("Missing capture metadata")
    if (data["schema"] != SCHEMA or data["rom_sha256"] != ROM_SHA or
        not ID.fullmatch(data["capture_id"]) or not SCENE.fullmatch(data["scene"]) or
        data["area"] not in AREAS or data["character"] not in CHARS or
        data["kind"] not in KINDS or
        any(not isinstance(data[k], str) or not SHA.fullmatch(data[k])
            for k in ("rom_sha256", "game_exe_sha256", "asset_index_sha256"))):
        raise ValueError("Invalid source ROM identity or scene metadata")
    listed = data["files"]
    if not isinstance(listed, dict) or set(listed) != set(FILES):
        raise ValueError("Missing or unexpected evidence file")
    bodies = {}
    for name in FILES:
        f = folder / name
        if not f.is_file() or f.is_symlink():
            raise ValueError("Missing/unsafe evidence: " + name)
        record = listed[name]
        length = f.stat().st_size
        if (not isinstance(record, dict) or
            not isinstance(record.get("bytes"), int) or
            record["bytes"] != length or length < 1 or length > 32*1024*1024 or
            not isinstance(record.get("sha256"), str) or
            not SHA.fullmatch(record["sha256"]) or
            sha_file(f) != record["sha256"]):
            raise ValueError("Tampered or oversized evidence: " + name)
        bodies[name] = f.read_text(encoding="utf-8")
    paired = analyze(bodies["CVIII-CHR-Fetch.csv"], bodies["CVIII-Frame-Evidence.csv"])
    summary = json.loads(bodies["CVIII-CHR-Fetch.json"])
    frame_summary = json.loads(bodies["CVIII-Frame-Evidence.json"])
    if not isinstance(summary, dict) or frame_summary != paired:
        raise ValueError("Stored original PPU summary does not match raw evidence")
    for f, src in (("pattern_fetches", "pattern_fetches"),
                   ("cache_mismatches", "cache_mismatches"),
                   ("invalid_fetches", "invalid_fetches"),
                   ("sampled_frames", "sampled_fetch_frames")):
        if summary.get(f) != paired[src]:
            raise ValueError("Saved fetch summary disagrees with actual read trace")
    if not bodies["CVIII-CHR-Audit.csv"].startswith(
        "sample,frame,mode,ctrl,bank0,bank1,bank2,bank3,"):
        raise ValueError("Missing VRC6 mapper/palette audit schema")
    return {
        "capture_id": data["capture_id"], "scene": data["scene"],
        "area": data["area"], "kind": data["kind"],
        "character": data["character"], "checkpoint": data.get("checkpoint", ""),
        "game_exe_sha256": data["game_exe_sha256"],
        "sampled_frames": paired["sampled_original_ppu_frames"],
        "fetches": paired["pattern_fetches"],
        "mismatches": paired["cache_mismatches"],
        "invalid_reads": paired["invalid_fetches"],
        "bank_changes": paired["bank_transitions"],
        "source_byte_parity": paired["fetch_source_byte_parity"],
    }


def build_matrix(root: Path, minimum: int = 10) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Expected private QA session directory")
    paths = sorted(root.rglob("capture.json"))
    if len(paths) > 1000:
        raise ValueError("Too many private captures")
    sessions, invalid, ids = [], [], set()
    for path in paths:
        try:
            if root.resolve() not in path.parent.resolve().parents:
                raise ValueError("Capture escaped private QA directory")
            scene = read_scene(path.parent)
            if scene["capture_id"] in ids:
                raise ValueError("Repeated capture ID")
            ids.add(scene["capture_id"])
            scene["folder"] = str(path.parent.relative_to(root))
            scene["quality"] = ("cache_mismatch" if not scene["source_byte_parity"]
                else "insufficient_samples" if scene["sampled_frames"] < minimum
                else "no_observed_fetches" if not scene["fetches"]
                else "observed_source_byte_parity")
            sessions.append(scene)
        except (ValueError, OSError, UnicodeError) as exc:
            invalid.append({"folder": str(path.parent.relative_to(root)), "reason": str(exc)})
    adequate = [s for s in sessions if s["quality"] == "observed_source_byte_parity"]
    covered = sorted({s["area"] for s in adequate})
    return {
        "schema": "CVIII-JP-QA-matrix/v1",
        "captures": len(sessions), "invalid_captures": invalid, "sessions": sessions,
        "minimum_sampled_frames": minimum,
        "areas_observed": covered, "unobserved_areas": [x for x in AREAS if x not in covered],
        "characters_observed": sorted({s["character"] for s in adequate}),
        "native_builds_observed": len({s["game_exe_sha256"] for s in sessions}),
        "shallow_or_failed_sessions": len(sessions)-len(adequate),
        "sampled_frames": sum(s["sampled_frames"] for s in sessions),
        "physical_chr_reads": sum(s["fetches"] for s in sessions),
        "cache_mismatches": sum(s["mismatches"] for s in sessions),
        "invalid_reads": sum(s["invalid_reads"] for s in sessions),
        "rendering_parity_proven": False,
        "authentic_gameplay_playtested_by_this_tool": False,
        "remaining_gate": "Owner must play actual retail stages and an independent "
                          "cached renderer must be compared to original PPU output",
    }


def smoke() -> None:
    def csv_rows(fields, rows):
        stream = io.StringIO()
        w = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)
        return stream.getvalue()
    fetch = csv_rows(FETCH_FIELDS, [invented_row(1, 20, 0, 2, 3, 1, count=4)])
    frame = csv_rows(EVIDENCE_FIELDS, [{
        "frame":"1", "pattern_reads":"4", "cache_mismatches":"0",
        "invalid_reads":"0", "bank_changes":"1", "ppu_color_fnv64":"0"*16,
        "bg_opaque_fnv64":"1"*16, "scanline_state_fnv64":"2"*16,
        "nonzero_bg_pixels":"2", "visible_bg_lines":"1", "visible_sprite_lines":"1"
    }])
    entries = {
        "CVIII-CHR-Audit.csv": "sample,frame,mode,ctrl,bank0,bank1,bank2,bank3,bank4,bank5,bank6,bank7,palette32,mapper_match\n",
        "CVIII-CHR-Fetch.csv": fetch, "CVIII-Frame-Evidence.csv": frame,
        "CVIII-CHR-Fetch.json": json.dumps(summarize_fetch(io.StringIO(fetch))),
        "CVIII-Frame-Evidence.json": json.dumps(analyze(fetch, frame))
    }
    with tempfile.TemporaryDirectory(prefix="jp0602-qa-") as temp:
        root = Path(temp)
        folder = root / "village-20261013T100000Z-aaaaaaaa"
        folder.mkdir()
        hashes = {}
        for name, content in entries.items():
            p = folder/name
            p.write_text(content, encoding="utf-8")
            hashes[name] = {"bytes": p.stat().st_size, "sha256": sha_file(p)}
        meta = {"schema": SCHEMA, "capture_id":"20261013T100000Z-aaaaaaaa",
                "scene":"village-entry", "area":"village", "kind":"gameplay",
                "character":"Trevor", "rom_sha256":ROM_SHA,
                "game_exe_sha256":"a"*64, "asset_index_sha256":"b"*64,
                "files":hashes}
        (folder/"capture.json").write_text(json.dumps(meta), encoding="utf-8")
        good = build_matrix(root, 1)
        assert good["captures"] == 1 and good["areas_observed"] == ["village"]
        assert good["physical_chr_reads"] == 4 and not good["rendering_parity_proven"]
        assert build_matrix(root, 10)["shallow_or_failed_sessions"] == 1
        with (folder/"CVIII-CHR-Fetch.csv").open("a") as f: f.write("tamper\n")
        assert len(build_matrix(root)["invalid_captures"]) == 1
        (folder/"CVIII-CHR-Fetch.csv").write_text(fetch, encoding="utf-8")
        p = folder/"CVIII-Frame-Evidence.json"
        p.write_text(json.dumps({**analyze(fetch, frame), "pattern_fetches":5}), encoding="utf-8")
        hashes[p.name] = {"bytes":p.stat().st_size, "sha256":sha_file(p)}
        (folder/"capture.json").write_text(json.dumps(meta), encoding="utf-8")
        assert len(build_matrix(root)["invalid_captures"]) == 1
        meta["rom_sha256"] = "f"*64
        (folder/"capture.json").write_text(json.dumps(meta), encoding="utf-8")
        assert len(build_matrix(root)["invalid_captures"]) == 1
    print("PASS JP0602 owner-local QA scene matrix/provenance/tamper gate")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--root", type=Path)
    p.add_argument("--json", type=Path)
    p.add_argument("--min-frames", type=int, default=10)
    p.add_argument("--require-coverage", action="store_true")
    a = p.parse_args()
    if a.smoke:
        smoke(); return
    if a.root is None or not 1 <= a.min_frames <= 10000:
        p.error("--root and --min-frames 1..10000 are required")
    report = build_matrix(a.root, a.min_frames)
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if a.json: a.json.write_text(output, encoding="utf-8")
    else: print(output, end="")
    if (report["invalid_captures"] or report["shallow_or_failed_sessions"] or
        (a.require_coverage and report["unobserved_areas"])):
        p.exit(1, "JP0602 private capture incomplete or failing\n")


if __name__ == "__main__":
    main()
