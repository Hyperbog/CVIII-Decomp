#!/usr/bin/env python3
"""Deterministic, cross-project decompilation evidence and replay gates.

No proprietary ROM/game assets or original bytes are embedded. Python 3.10+ stdlib.
A byte-exact fallback is *not* considered verified semantic decompilation.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import difflib
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

VERSION = 1
CONFIDENCE = {"TRACE_EXECUTED", "STATIC_PROVED", "PRODUCER_TYPED_DATA",
              "STRUCTURAL_CANDIDATE", "RAW_FALLBACK"}
PROVEN = {"TRACE_EXECUTED", "STATIC_PROVED", "PRODUCER_TYPED_DATA"}
CODE_CONFIDENCE = {"TRACE_EXECUTED", "STATIC_PROVED"}

class EvidenceError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise EvidenceError(message)


def read_json(path: str | Path) -> dict:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    require(isinstance(doc, dict), "top-level document must be an object")
    return doc


def atomic_json(path: str | Path, doc: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def as_addr(v: int | str) -> int:
    # Address fields use hexadecimal strings; integer fields are decimal quantities.
    if isinstance(v, int):
        return v
    require(isinstance(v, str), "address must be integer or hexadecimal string")
    return int(v[2:] if v.lower().startswith("0x") else v, 16)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_bank(doc: dict, rom: bytes | None = None) -> dict:
    """Verify a physically identified *complete* ROM bank partition.

    ``rom`` means bank bytes, not a whole cartridge; callers authenticate and
    extract physical cartridge banks using their platform's extractor.
    """
    require(doc.get("schema_version") == VERSION, "unsupported bank map schema_version")
    bank = doc.get("bank")
    require(isinstance(bank, dict), "bank object missing")
    identity = bank.get("physical_id")
    require(isinstance(identity, str) and identity.strip(), "physical bank identity missing")
    start, size = as_addr(bank.get("cpu_base")), bank.get("size")
    require(isinstance(size, int) and size > 0, "invalid bank length")
    require(start >= 0 and start + size <= 65536, "invalid CPU mapped window")
    expected_sha = bank.get("sha256")
    require(isinstance(expected_sha, str) and len(expected_sha) == 64, "bank SHA256 missing")
    if rom is not None:
        require(len(rom) == size, "ROM byte length does not match physical bank")
        require(sha(rom) == expected_sha, "original physical bank SHA256 mismatch")
    segments = doc.get("segments")
    require(isinstance(segments, list) and segments, "missing bank segment list")
    # Keep the declared ordering; accidental reordering must not silently pass.
    cursor = start
    counts = Counter()
    code = 0
    semantic = 0
    for i, seg in enumerate(segments):
        require(isinstance(seg, dict), f"segment {i}: expected object")
        lo, hi = as_addr(seg.get("start")), as_addr(seg.get("end_exclusive"))
        require(lo == cursor, f"segment {i}: gap/overlap/order error at {cursor:04X}, got {lo:04X}")
        require(lo < hi <= start + size, f"segment {i}: out of bounds")
        cat = seg.get("evidence")
        require(cat in CONFIDENCE, f"segment {i}: unsupported evidence {cat}")
        typ = seg.get("type")
        require(typ in ("code", "data", "unknown"), f"segment {i}: bad type")
        if typ == "unknown":
            require(cat == "RAW_FALLBACK", "unresolved bytes cannot be counted as verified")
        if cat == "RAW_FALLBACK":
            require(typ == "unknown", "raw fallback must be unclassified")
        if typ == "code" and cat == "PRODUCER_TYPED_DATA":
            raise EvidenceError("typed data may not be counted as executable code")
        if typ == "code" and cat in CODE_CONFIDENCE:
            code += hi - lo
        if cat in PROVEN:
            semantic += hi - lo
            require(bool(seg.get("source")), f"segment {i}: proven evidence needs a source reference")
        if cat == "TRACE_EXECUTED":
            require(bool(seg.get("scenario")), f"segment {i}: trace-executed needs a scenario identifier")
        digest = seg.get("sha256")
        if digest is not None:
            require(isinstance(digest, str) and len(digest) == 64, f"segment {i}: invalid SHA256")
            if rom is not None:
                require(sha(rom[lo-start:hi-start]) == digest, f"segment {i}: hash mismatch")
        counts[(typ, cat)] += hi - lo
        cursor = hi
    require(cursor == start + size, f"bank incomplete: ends at {cursor:04X}")
    require(sum(counts.values()) == size, "accounting error")
    return {"status": "PASS", "physical_id": identity, "bytes": size,
            "verified_instruction_bytes": code,
            "proven_semantic_bytes": semantic,
            "structural_or_unverified_bytes": sum(n for (_, k), n in counts.items() if k == "STRUCTURAL_CANDIDATE"),
            "raw_fallback_bytes": sum(n for (_, k), n in counts.items() if k == "RAW_FALLBACK"),
            "classification": {f"{t}:{c}": n for (t,c),n in sorted(counts.items())},
            "has_authenticated_bank_image": rom is not None,
            "parity_proved": False}


def validate_cfg(doc: dict, bank_map: dict | None = None) -> dict:
    """Reject cross-bank aliasing, duplicate starts and unsupported jump targets."""
    require(doc.get("schema_version") == VERSION, "bad CFG schema")
    nodes = doc.get("nodes")
    edges = doc.get("edges")
    require(isinstance(nodes, list) and isinstance(edges, list), "CFG needs nodes and edges")
    ids, spans, by_id = set(), defaultdict(list), {}
    for i, n in enumerate(nodes):
        ident, phys = n.get("id"), n.get("physical_bank")
        require(isinstance(phys, str) and phys and isinstance(ident, str) and ident, f"node {i}: missing identity")
        require(ident not in ids, f"duplicate node id {ident}")
        ids.add(ident)
        lo, hi = as_addr(n["start"]), as_addr(n["end_exclusive"])
        require(0 <= lo < hi <= 65536, "invalid basic-block bounds")
        spans[phys].append((lo, hi, ident))
        by_id[ident] = n
    for phys, entries in spans.items():
        for a, b in zip(sorted(entries), sorted(entries)[1:]):
            require(a[1] <= b[0], f"physical {phys}: overlapping basic blocks {a[2]}, {b[2]}")
    incomplete = 0
    for i, e in enumerate(edges):
        require(e.get("source") in ids, f"edge {i}: missing source")
        status = e.get("status")
        require(status in ("resolved", "unresolved", "external"), f"edge {i}: unknown status")
        target = e.get("target")
        if status == "resolved":
            require(target in ids, f"edge {i}: resolved target not mapped")
        else:
            require(target is None, f"edge {i}: {status} must not fake a resolved target")
            require(bool(e.get("reason")), f"edge {i}: unresolved/external edge needs reason")
            incomplete += 1
    for root in doc.get("roots", []):
        require(root in ids, f"root {root} missing")
    if bank_map is not None:
        bid = bank_map["bank"]["physical_id"]
        start = as_addr(bank_map["bank"]["cpu_base"])
        end = start + bank_map["bank"]["size"]
        for n in nodes:
            if n["physical_bank"] == bid:
                require(start <= as_addr(n["start"]) < as_addr(n["end_exclusive"]) <= end,
                        f"CFG node {n['id']} outside claimed bank")
    return {"status":"PASS", "nodes":len(nodes), "edges":len(edges),
            "open_edges":incomplete, "fully_closed":incomplete == 0}


def iter_jsonl(path: str | Path):
    with open(path, encoding="utf-8") as f:
        for i, raw in enumerate(f, 1):
            if not raw.strip():
                continue
            entry = json.loads(raw)
            require(isinstance(entry, dict) and entry.get("step") is not None,
                    f"trace {path}, line {i}: missing step")
            yield entry


def normalize_frame(frame: dict, ignored: set[str]) -> dict:
    # Exclude non-deterministic timing metadata only, never execution state.
    return {k: v for k, v in frame.items() if k not in ignored}


def trace_diff(reference: str | Path, candidate: str | Path,
               ignored: set[str] | None = None) -> dict:
    ignored = (ignored or set()) | {"wall_time", "capture_note"}
    from itertools import zip_longest
    total = 0
    sentinel = object()
    for idx, (expected, actual) in enumerate(zip_longest(iter_jsonl(reference), iter_jsonl(candidate), fillvalue=sentinel)):
        if expected is sentinel or actual is sentinel:
            return {"status":"FAIL", "matched_steps":total,"first_divergence_step":idx,
                    "field":"trace_length", "reference":None if expected is sentinel else expected,
                    "candidate":None if actual is sentinel else actual}
        left = normalize_frame(expected, ignored)
        right = normalize_frame(actual, ignored)
        if left != right:
            differences = sorted(set(left) | set(right))
            first = next(x for x in differences if left.get(x, sentinel) != right.get(x, sentinel))
            return {"status":"FAIL", "matched_steps":total,
                    "first_divergence_step":idx,"field":first,
                    "reference":left.get(first), "candidate":right.get(first),
                    "reference_pc":left.get("pc"), "candidate_pc":right.get("pc"),
                    "reference_bank":left.get("physical_bank"), "candidate_bank":right.get("physical_bank")}
        total += 1
    require(total > 0, "empty traces cannot pass parity")
    return {"status":"PASS", "matched_steps":total, "first_divergence_step":None}


def attempt_update(ledger: dict | None, score: float, *, hypothesis: str,
                   budget: int = 3) -> dict:
    require(0 <= score <= 1, "score must be fraction 0..1")
    require(isinstance(hypothesis, str) and hypothesis, "hypothesis identity required")
    require(isinstance(budget, int) and budget > 0, "attempt budget must be positive")
    if ledger is None:
        ledger = {"schema_version":VERSION, "hypothesis":hypothesis,
                  "attempts": [], "best_score":-1.0, "no_improvement":0}
    require(ledger.get("hypothesis") == hypothesis, "hypothesis changed; use a new ledger")
    best = float(ledger["best_score"])
    improved = score > best
    ledger["best_score"] = max(best, score)
    ledger["no_improvement"] = 0 if improved else ledger["no_improvement"] + 1
    ledger["attempts"].append({"score":score,"improved":improved})
    ledger["action"] = "STOP_AND_DIAGNOSE" if ledger["no_improvement"] >= budget else "CONTINUE"
    ledger["attempt_budget"] = budget
    return ledger


def context_packet(atlas: dict, *, cpu: int, radius: int = 0x40,
                   max_segments: int = 20) -> dict:
    """Small hash-pinned room-bank context. Does not infer candidate liveness."""
    require(radius > 0 and max_segments > 0, "context budget must be positive")
    bank = atlas.get("bank", {})
    segments = atlas.get("segments", [])
    selected = [s for s in segments if as_addr(s["start"]) < cpu+radius and
                as_addr(s["end_exclusive"]) > cpu-radius]
    selected.sort(key=lambda s: (abs(as_addr(s["start"])-cpu),as_addr(s["start"])))
    chosen = sorted(selected[:max_segments],key=lambda s: as_addr(s["start"]))
    return {"schema_version":VERSION, "physical_bank":bank.get("physical_id"),
            "bank_sha256":bank.get("sha256"),"target_cpu":f"{cpu:04X}",
            "requested_radius":radius, "segments":chosen,
            "truncated":len(selected)>len(chosen),
            "warning":"Evidence-only context. Candidate bytes are not verified entry points."}


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="cmd", required=True)
    a=sub.add_parser("bank", help="validate full physical-bank source/evidence partition")
    a.add_argument("map");a.add_argument("--bank-bytes");a.add_argument("--report")
    a=sub.add_parser("cfg", help="validate physically-qualified CFG")
    a.add_argument("graph");a.add_argument("--map");a.add_argument("--report")
    a=sub.add_parser("diff", help="first-divergence semantic trace comparison")
    a.add_argument("reference");a.add_argument("candidate");a.add_argument("--report")
    a.add_argument("--ignore",action="append",default=[])
    a=sub.add_parser("context",help="make bounded bank context for AI")
    a.add_argument("map");a.add_argument("--cpu",required=True);a.add_argument("--radius",type=lambda s:int(s,0),default=64)
    a.add_argument("--limit",type=int,default=20);a.add_argument("--report")
    a=sub.add_parser("attempt", help="bounded iteration monitor, with persistent diagnostics")
    a.add_argument("ledger");a.add_argument("--hypothesis",required=True)
    a.add_argument("--score",type=float,required=True);a.add_argument("--budget",type=int,default=3)
    args=p.parse_args(argv)
    try:
        if args.cmd=="bank":
            res=validate_bank(read_json(args.map),Path(args.bank_bytes).read_bytes() if args.bank_bytes else None)
        elif args.cmd=="cfg":res=validate_cfg(read_json(args.graph),read_json(args.map) if args.map else None)
        elif args.cmd=="diff":res=trace_diff(args.reference,args.candidate,set(args.ignore))
        elif args.cmd=="context":res=context_packet(read_json(args.map),cpu=as_addr(args.cpu),radius=args.radius,max_segments=args.limit)
        else:
            path=Path(args.ledger)
            res=attempt_update(read_json(path) if path.exists() else None,args.score,hypothesis=args.hypothesis,budget=args.budget)
            atomic_json(path,res)
        if getattr(args,"report",None):atomic_json(args.report,res)
        print(json.dumps(res,sort_keys=True))
        return 1 if res.get("status")=="FAIL" or res.get("action")=="STOP_AND_DIAGNOSE" else 0
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(f"WORKFLOW ERROR: {exc}",file=sys.stderr)
        return 2

if __name__=="__main__":raise SystemExit(main())
