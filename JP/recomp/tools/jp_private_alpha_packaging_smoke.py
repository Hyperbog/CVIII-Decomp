#!/usr/bin/env python3
"""ROM-free guard for private Windows AlphaCandidate copy source paths.

The public CI builds cannot package an owner-supplied Japanese ROM. This
checks the same pinned source manifests used by Build-Alpha.ps1 before
owner-local compilation and private packaging, preventing wrong-folder
failures discovered only at the end of an expensive native build.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGER = ROOT / "JP/recomp/release/alpha/Build-Alpha.ps1"


def names_from_loop(source: str, marker: str) -> list[str]:
    pattern = r"foreach \(\$name in @\('"+re.escape(marker)+r"'(.*?)\)\) \{"
    match = re.search(pattern, source, re.S)
    if not match:
        raise AssertionError("Missing original private-packaging manifest: "+marker)
    result = re.findall(r"'([^']+\.(?:bat|ps1|py|lua))'", "'"+marker+"'"+match.group(1))
    if not result or len(result)!=len(set(result)):
        raise AssertionError("Empty or duplicate private-packaging entries: "+marker)
    return result


def smoke() -> None:
    text = PACKAGER.read_text(encoding="utf-8-sig")
    if "$src=Join-Path $repoPath ('JP/recomp/release/alpha/'+$name)" not in text:
        raise AssertionError("Alpha launcher copy must use JP/recomp/release/alpha")
    if "$src=Join-Path $repoPath ($relative+$name)" not in text or (
        "$relative=if ($name -in $recompHelpers)" not in text):
        raise AssertionError("Mixed recomp/decomp helper owner resolution missing")

    launchers = names_from_loop(text, "Play-CVIII.bat")
    helpers = names_from_loop(text, "jp_password_stage_0593.py")
    group = re.search(r"\$recompHelpers=@\((.*?)\)", text, re.S)
    if not group:
        raise AssertionError("Explicit owner list for native recomp tools missing")
    recomp = set(re.findall(r"'([^']+\.py)'",group.group(1)))
    if not recomp.issubset(set(helpers)):
        raise AssertionError("Unexpected private helper ownership")
    assert "Play-CVIII.bat" in launchers and "Resolve-Python.ps1" in launchers
    assert "jp_asset_pack_0597.py" in recomp
    assert "jp_password_stage_0593.py" not in recomp
    for name in launchers:
        path = ROOT / "JP/recomp/release/alpha" / name
        if not path.is_file():
            raise AssertionError("Missing launcher source: "+str(path))
    for name in helpers:
        owner = "recomp" if name in recomp else "decomp"
        path = ROOT / "JP" / owner / "tools" / name
        if not path.is_file():
            raise AssertionError("Missing "+owner+" helper source: "+str(path))
    print("PASS original-JP private Alpha packaging source manifest: "
          f"{len(launchers)} launchers, {len(helpers)} mixed-owner tools")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    if not args.smoke:
        parser.error("Run with --smoke")
    smoke()


if __name__=="__main__":
    main()
