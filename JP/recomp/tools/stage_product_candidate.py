#!/usr/bin/env python3
"""Stage a private, QA-pending Windows product candidate from AlphaCandidate.

Keeps the working flat runtime intact, copies only an allowlist defined by the
existing release manifest, and never publishes the ROM-derived game executable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

EXPECTED_ROM = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "release/alpha/Private-Release-Manifest.psd1"
DEFAULT_QA = ROOT / "release/product/QA_CONTROLLER_DMA.md"
RUNTIME = (
    "jp_akumajou_densetsu.exe", "SDL2.dll", "CVIII-Assets.bin",
    "CVIII-CHR-Index.dat", "Launch-Alpha.ps1", "README_ALPHA.md",
    "ALPHA_BUILD.json",
    "licenses/NESRecomp-LICENSE.txt", "licenses/SDL2-COPYING.txt",
)
ENTRYPOINTS = {"Play-CVIII.bat", "Build-And-Play.bat", "Build-And-Play.ps1",
               "Resolve-Python.ps1"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bundled_scripts(manifest: Path) -> list[str]:
    source = manifest.read_text(encoding="utf-8")
    names = re.findall(r"^\s*'([A-Za-z0-9_.-]+\.(?:ps1|bat|py|lua))'\s*$",
                       source, re.MULTILINE)
    if len(names) < len(ENTRYPOINTS) or len(names) != len(set(names)):
        raise ValueError("Release manifest has missing or duplicated script names")
    if not ENTRYPOINTS.issubset(names):
        raise ValueError("Release manifest is missing required player entrypoints")
    return names


def safe_regular(source: Path, relative: str) -> Path:
    path = source
    for component in Path(relative).parts:
        if component in (".", ".."):
            raise ValueError("Unsafe source path")
        path = path / component
        if path.is_symlink():
            raise ValueError("Symlink in release payload: " + relative)
    if not path.is_file():
        raise ValueError("Required private build file missing: " + relative)
    return path


def check_build(source: Path) -> dict:
    info = json.loads(safe_regular(source, "ALPHA_BUILD.json").read_text(encoding="utf-8-sig"))
    if (info.get("schema") != "CVIII-windows-alpha-candidate/v2" or
            info.get("original_rom_sha256") != EXPECTED_ROM or
            info.get("original_rom_included") is not False):
        raise ValueError("Unrecognized, unauthenticated or unsafe private AlphaCandidate")
    for name, key in (
        ("jp_akumajou_densetsu.exe", "game_exe_sha256"),
        ("CVIII-Assets.bin", "assets_sha256"),
        ("CVIII-CHR-Index.dat", "asset_chr_index_sha256"),
    ):
        actual = digest(safe_regular(source, name))
        if actual != info.get(key):
            raise ValueError("Private AlphaCandidate checksum mismatch: " + name)
    return info


def stage(source: Path, destination: Path, manifest: Path, qa_doc: Path) -> dict:
    source = source.resolve(strict=True)
    destination = destination.absolute()
    if not source.is_dir() or destination.exists():
        raise ValueError("Need an existing AlphaCandidate and a NEW output directory")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Private build and product stage cannot contain one another")
    info = check_build(source)
    scripts = bundled_scripts(manifest)
    files = sorted(set(RUNTIME).union(scripts))
    for relative in files:
        safe_regular(source, relative)
    if not qa_doc.is_file() or qa_doc.is_symlink():
        raise ValueError("Missing trusted controller/DMA QA instructions")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="." + destination.name + "-stage-",
                                 dir=destination.parent))
    try:
        game = temp / "game"
        qa = temp / "qa"
        metadata = temp / "metadata"
        game.mkdir()
        qa.mkdir()
        metadata.mkdir()
        records: dict[str, str] = {}
        for relative in files:
            target = game / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe_regular(source, relative), target)
            recorded = digest(target)
            if recorded != digest(source / relative):
                raise ValueError("Staging checksum changed: " + relative)
            records[relative] = recorded
        shutil.copy2(qa_doc, qa / "CONTROLLER_DMA.md")
        summary = {
            "schema": "cviii.jp.private-product-candidate/v1",
            "status": "qa_pending_not_certified",
            "edition": "Enhanced",
            "layout": {"game": "game/", "metadata": "metadata/", "qa": "qa/"},
            "entrypoint": "game/Play-CVIII.bat",
            "original_japanese_rom_sha256": EXPECTED_ROM,
            "original_rom_included": False,
            "private_executable_included": True,
            "original_alpha_schema": info["schema"],
            "original_alpha_version": info.get("version", ""),
            "controller_gameplay_verified": False,
            "independent_mesen_dma_parity_verified": False,
            "runtime_files_sha256": records,
        }
        (metadata / "PRODUCT_CANDIDATE.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp.rename(destination)
        return summary
    except BaseException:
        shutil.rmtree(temp)
        raise


def smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="cviii-product-stage-") as root:
        root = Path(root)
        alpha, output = root / "AlphaCandidate", root / "ProductCandidate"
        alpha.mkdir()
        (alpha / "licenses").mkdir()
        manifest = root / "Private-Release-Manifest.psd1"
        manifest.write_text(
            "@{\n launchers = @(\n" +
            "".join(f"  '{name}'\n" for name in sorted(ENTRYPOINTS)) +
            " )\n}\n", encoding="utf-8")
        qa = root / "QA.md"
        qa.write_text("private validation instructions\n", encoding="utf-8")
        for filename in set(RUNTIME).union(ENTRYPOINTS) - {"ALPHA_BUILD.json"}:
            p = alpha / filename
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(("fixture:" + filename).encode())
        (alpha / "config.ini").write_text("private controls\n")
        (alpha / "saves").mkdir()
        (alpha / "saves" / "private.cycstate").write_bytes(b"private save")
        (alpha / "private.nes").write_bytes(b"never package a ROM")
        details = {
            "schema": "CVIII-windows-alpha-candidate/v2",
            "original_rom_sha256": EXPECTED_ROM,
            "original_rom_included": False,
            "version": "0.2.0-alpha.1",
            "game_exe_sha256": digest(alpha / "jp_akumajou_densetsu.exe"),
            "assets_sha256": digest(alpha / "CVIII-Assets.bin"),
            "asset_chr_index_sha256": digest(alpha / "CVIII-CHR-Index.dat"),
        }
        (alpha / "ALPHA_BUILD.json").write_text(json.dumps(details))
        out = stage(alpha, output, manifest, qa)
        assert out["status"] == "qa_pending_not_certified"
        assert all((output / "game" / p).is_file() for p in out["runtime_files_sha256"])
        assert (output / "qa/CONTROLLER_DMA.md").is_file()
        assert (output / "metadata/PRODUCT_CANDIDATE.json").is_file()
        for prohibited in ("private.nes", "config.ini", "saves/private.cycstate"):
            assert not (output / "game" / prohibited).exists()
        for action in (
            lambda: stage(alpha, output, manifest, qa),
            lambda: stage(alpha, alpha / "nested", manifest, qa),
        ):
            try:
                action()
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid product stage was accepted")
        (alpha / "jp_akumajou_densetsu.exe").write_bytes(b"tampered")
        try:
            stage(alpha, root / "tampered", manifest, qa)
        except ValueError:
            pass
        else:
            raise AssertionError("Tampered original game executable was accepted")
    print("PASS private product layout, hashes, entrypoints, and no-ROM/no-save isolation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--qa-doc", type=Path, default=DEFAULT_QA)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        smoke()
        return
    if args.candidate is None or args.out is None:
        parser.error("--candidate and --out are required")
    result = stage(args.candidate, args.out, args.manifest, args.qa_doc)
    print("STAGED PRIVATE QA-PENDING PRODUCT CANDIDATE: " + str(args.out))
    print("COPY COUNT: " + str(len(result["runtime_files_sha256"])))
    print("NOT CERTIFIED: original gameplay and Mesen controller/DMA parity pending")


if __name__ == "__main__":
    main()
