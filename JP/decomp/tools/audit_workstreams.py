#!/usr/bin/env python3
"""Verify native-product vs semantic-source workstream ownership and counters.

ROM-free, no external dependencies. Does not move historic paths or promote
source certificates. Authoritative counters remain in the original ledger.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORK = Path("JP/decomp/workstreams")
MANIFEST = WORK / "WORKSTREAMS.json"
PRODUCT = Path("JP/recomp/workstreams/native-recompilation/PRODUCT_STATE.json")
SEMANTIC = WORK / "semantic-decompilation/EVIDENCE_STATE.json"
ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)

def read_json(file: Path) -> dict:
    result = json.loads(file.read_text(encoding="utf-8"))
    require(type(result) is dict, f"Expected object in {file}")
    return result

def safe_relative(raw: str) -> Path:
    require(type(raw) is str and bool(raw) and "\\" not in raw and
            not raw.startswith("/") and not raw.endswith("/"),
            f"Unsafe/empty workstream path: {raw!r}")
    parts = Path(raw).parts
    require(parts and not any(p in (".", "..", "") for p in parts)
            and not Path(raw).is_absolute(), f"Workstream path escapes repo: {raw!r}")
    return Path(raw)

def validate_manifest_shape(m: dict) -> dict[str, str]:
    require(m.get("schema") == "JP-workstream-boundaries/v1",
            "Workstream manifest version drift")
    require(m.get("source_rom_sha256") == ROM_SHA, "Unexpected cartridge identity")
    streams = m.get("streams")
    require(type(streams) is dict and set(streams) ==
            {"native_recompilation", "semantic_decompilation", "shared"},
            "Exactly the native, semantic and shared workstream namespaces are required")
    owners = {}
    for name, stream in streams.items():
        require(type(stream) is dict and type(stream.get("files")) is list
                and bool(stream["files"]), f"Empty/invalid owned files: {name}")
        if name != "shared":
            require(safe_relative(stream["home"]).as_posix().startswith(f"JP/{'recomp' if name == 'native_recompilation' else 'decomp'}/workstreams/{name.replace('_','-')}/"),
                    f"{name}: status home is outside canonical directory")
            require(safe_relative(stream["status_file"]).as_posix().startswith(f"JP/{'recomp' if name == 'native_recompilation' else 'decomp'}/workstreams/{name.replace('_','-')}/"),
                    f"{name}: machine state is outside canonical directory")
        for row in stream["files"]:
            require(type(row) is dict and set(row) == {"path", "role"} and
                    type(row["role"]) is str and len(row["role"]) >= 6,
                    f"{name}: malformed role declaration")
            path = safe_relative(row["path"]).as_posix()
            require(path not in owners, f"Double-owned path {path}: {owners.get(path)} vs {name}")
            owners[path] = name
    must_be_native = (
        "JP/recomp/native/nesrecomp_cycle/CMakeLists.txt",
        "JP/recomp/native/enhanced/cviii_edition.c",
        "JP/recomp/release/alpha/README_ALPHA.md",
        "JP/recomp/tools/patch_cyc_savestates_0591.py",
        "JP/recomp/tools/patch_cyc_stage_menu_0594.py",
    )
    must_be_semantic = (
        "JP/decomp/analysis/PROGRESS_SCORE.csv",
        "JP/decomp/analysis/RESUME_STATE.json",
        "JP/decomp/analysis/NATIVE_EVIDENCE_LEDGER.json",
        "JP/decomp/docs/PROGRESS_METRIC.md",
        "JP/recomp/native/enhanced/cviii_room_stream_0659.c",
    )
    for path in must_be_native:
        require(owners.get(path) == "native_recompilation",
                f"Playable product is not owned by native recompilation: {path}")
    for path in must_be_semantic:
        require(owners.get(path) == "semantic_decompilation",
                f"Source certification/dormant helper improperly owned: {path}")
    require(owners.get("JP/decomp/docs/ROM_IDENTITY.md") == "shared",
            "Shared ROM identity must not be product/research only")
    policy = m.get("policy")
    require(type(policy) is dict and bool(policy.get("bridge_rule"))
            and bool(policy.get("migration")),
            "Workstream migration and mixed-source integration policies required")
    return owners

def validate_semantic_counters(rows: list[dict], state: dict,
                               ledger: dict) -> tuple[int, int]:
    require(len(rows) == 8 and len({r.get("category") for r in rows}) == 8,
            "Expected eight unique fixed-rubric categories")
    values = []
    for row in rows:
        try:
            weight, earned = int(row["weight"]), int(row["earned"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError("Bad VPP row") from e
        require(0 <= earned <= weight and weight > 0,
                "Out-of-bounds semantic VPP weight/credit")
        values.append((weight, earned))
    weight_sum = sum(w for w, _ in values)
    earned_sum = sum(e for _, e in values)
    require(weight_sum == 100, "Semantic VPP rubric weights changed")
    require(state.get("rom_sha256") == ROM_SHA and
            ledger.get("rom_sha256") == ROM_SHA, "Mismatched research ROM authority")
    cert = ledger.get("certification")
    prg = state.get("progress_metrics", {}).get("strict_verified_prg_floor_bytes")
    require(type(cert) is dict and
            type(state.get("vpp", {}).get("earned")) is int and
            type(cert.get("vpp_earned")) is int and
            earned_sum == state["vpp"]["earned"] == cert["vpp_earned"],
            "Semantic rubric, resume state and ledger VPP disagree")
    require(type(prg) is int and 0 < prg <= 262144 and
            type(cert.get("strict_prg_floor")) is int and
            prg == cert["strict_prg_floor"], "Strict PRG certification state mismatch")
    require(state.get("last_completed_checkpoint") == cert.get("certified_checkpoint"),
            "Certified semantic checkpoint disagreement")
    require(state.get("frontier", {}).get("next_unprocessed_cpu"),
            "Original-source frontier missing")
    return earned_sum, prg

def validate_product_index(product: dict, semantic: dict,
                           owners: dict[str, str]) -> None:
    require(product.get("schema") == "JP-native-product-state/v1" and
            product.get("stream") == "native_recompilation",
            "Product-state schema/workstream drift")
    require(semantic.get("schema") == "JP-semantic-research-state/v1" and
            semantic.get("stream") == "semantic_decompilation",
            "Semantic research-state schema/workstream drift")
    require("owner-tested" in product.get("product_status", "").lower()
            and product.get("release") == "0.2.0-alpha.1",
            "Playable owner-tested release identity missing")
    require("not" in product.get("product_metrics", "").lower()
            and "VPP" not in product.get("product_metrics", "").upper(),
            "Product completion must not be represented as semantic VPP")
    capabilities = product.get("capabilities")
    require(type(capabilities) is list and len(capabilities) >= 5,
            "Missing major original native product features")
    ids = [item.get("id") for item in capabilities]
    require(len(ids) == len(set(ids)) and
            {"native_original_game", "save_states", "stage_companion_select",
             "sprite_flicker_correction"} <= set(ids),
            "Native core/saves/stage-companion/flicker feature coverage incomplete")
    for feature in capabilities:
        require(type(feature) is dict and feature.get("state")
                and owners.get(safe_relative(feature.get("source")).as_posix()) ==
                "native_recompilation",
                f"Product feature evidence outside product workstream: {feature.get('id')}")
    canonical = semantic.get("canonical_sources", {})
    checks = {"vpp_csv": "JP/decomp/analysis/PROGRESS_SCORE.csv",
              "strict_prg_and_checkpoint": "JP/decomp/analysis/RESUME_STATE.json",
              "evidence_ledger": "JP/decomp/analysis/NATIVE_EVIDENCE_LEDGER.json",
              "rubric": "JP/decomp/docs/PROGRESS_METRIC.md"}
    for k, path in checks.items():
        require(canonical.get(k) == path and
                owners.get(path) == "semantic_decompilation",
                f"Duplicated or diverted semantic authority: {k}")
    require(semantic.get("do_not_duplicate_live_counters") is True,
            "Workstream must not fork historical VPP/PRG counters")
    require(not any(k in product for k in
                    ("vpp", "vpp_earned", "strict_prg", "strict_prg_floor",
                     "strict_verified_prg_floor_bytes")),
            "Semantic progress counter inserted into product feature JSON")
    require(not any(k in semantic for k in
                    ("vpp_earned", "strict_verified_prg_floor_bytes")),
            "Independent semantic counter copy inserted into index")

def validate(root: Path = REPO) -> dict:
    manifest = read_json(root / MANIFEST)
    owners = validate_manifest_shape(manifest)
    for path in sorted(set(owners) | {
            manifest["streams"]["native_recompilation"]["home"],
            manifest["streams"]["native_recompilation"]["status_file"],
            manifest["streams"]["semantic_decompilation"]["home"],
            manifest["streams"]["semantic_decompilation"]["status_file"]}):
        resolved = root / safe_relative(path)
        require(resolved.is_file() and resolved.stat().st_size > 0,
                f"Missing workstream-owned original file: {path}")
    product = read_json(root / PRODUCT)
    semantic = read_json(root / SEMANTIC)
    validate_product_index(product, semantic, owners)
    with (root / "JP/decomp/analysis/PROGRESS_SCORE.csv").open(
            encoding="utf-8", newline="") as f:
        score = list(csv.DictReader(f))
    vpp, prg = validate_semantic_counters(score,
        read_json(root / "JP/decomp/analysis/RESUME_STATE.json"),
        read_json(root / "JP/decomp/analysis/NATIVE_EVIDENCE_LEDGER.json"))
    native_home = (root / manifest["streams"]["native_recompilation"]["home"]).read_text(
        encoding="utf-8")
    source_home = (root / manifest["streams"]["semantic_decompilation"]["home"]).read_text(
        encoding="utf-8")
    rubric = (root / "JP/decomp/docs/PROGRESS_METRIC.md").read_text(encoding="utf-8")
    require("owner-tested" in native_home.lower() and "NESRecomp" in native_home,
            "Native README no longer documents the playable release")
    require(f"{vpp}/100" in source_home and f"{prg:,}" in source_home,
            "Semantic landing page drifted from authoritative score/certificate")
    require(f"**VPP: {vpp} / 100" in rubric and
            "semantic" in rubric[:900].lower(),
            "Research rubric has lost accurate scope/score")
    return {"native_release": product["release"], "native_status": product["product_status"],
            "semantic_vpp": vpp, "semantic_strict_prg_bytes": prg,
            "owned_source_paths": len(owners),
            "owner_counts": {kind: len(manifest["streams"][kind]["files"])
                for kind in ("native_recompilation", "semantic_decompilation", "shared")}}

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=REPO)
    a = p.parse_args()
    result = validate(a.repo_root.resolve())
    print("PASS native recompilation product: ", result["native_release"], "— owner-tested runtime")
    print(f"PASS separate semantic source research: VPP {result['semantic_vpp']}/100; "
          f"strict PRG {result['semantic_strict_prg_bytes']:,}/262,144")
    print("PASS no double-owned anchors:", result["owned_source_paths"],
          "classified; original build/ledger paths stable")

if __name__ == "__main__":
    main()
