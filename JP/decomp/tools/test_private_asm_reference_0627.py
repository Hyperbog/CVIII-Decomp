#!/usr/bin/env python3
"""ROM-free generator tests; optional authenticated ROM integration via --rom."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import build_private_asm_reference_0627 as ref


def check_fake() -> None:
    # Synthetic deterministic 32 physical PRG + 16 CHR, with 6502 vectors.
    fake = bytearray(ref.ROM_SIZE)
    fake[:16] = bytes.fromhex("4E45531A101080100000000000000000")
    for i in range(ref.HEADER_SIZE, ref.ROM_SIZE):
        fake[i] = (i * 17 + (i >> 9) * 11 + 23) % 256
    for offset, address in ((0x3FFFA, 0xE057), (0x3FFFC, 0xE00B),
                            (0x3FFFE, 0xE0F5)):
        fake[16 + offset:18 + offset] = address.to_bytes(2, "little")
    b = bytes(fake)
    with tempfile.TemporaryDirectory(prefix="jp0627_rom_free_") as root:
        a, c = Path(root) / "a", Path(root) / "b"
        record = ref.build(b, a, expected_sha256=ref.digest(b))
        ref.build(b, c, expected_sha256=ref.digest(b))
        assert (a / "ROM.asm").read_text() == (c / "ROM.asm").read_text()
        assert (a / "manifest.json").read_bytes() == (c / "manifest.json").read_bytes()
        assert len(record["prg_banks"]) == 32 and len(record["chr_banks"]) == 16
        assert len((a / "physical_offsets.tsv").read_text().splitlines()) == 1 + 48 * 512
        assert record["vectors"]["reset"]["target_cpu"] == "E00B"
        assert record["certification_delta_bytes"] == 0
        assert (a / "PRG/prg_31.asm").read_text().count(".word $") == 3
        assert "fixed $F000" in (a / "PRG/prg_31.asm").read_text()
        assert "mapper-dependent" in (a / "PRG/prg_00.asm").read_text()
        assert ref._parse_assembly(a, "ROM.asm", set()) == b
        # Tampering with an asm listing is caught by exact reconstruction.
        bank = a / "PRG/prg_01.asm"
        bank.write_text(bank.read_text().replace(".byte $", ".byte $00, $", 1))
        assert ref._parse_assembly(a, "ROM.asm", set()) != b
        for bad in (a / "../evil.asm",):
            try:ref._parse_assembly(a, "../evil.asm", set())
            except ValueError:pass
            else:raise AssertionError("Unsafe include accepted")
        # Refuse generating a ROM-equivalent bank listing in a Git checkout.
        gitroot = Path(root) / "git"
        gitroot.mkdir(); (gitroot / ".git").mkdir()
        try:ref.build(b, gitroot / "generated", expected_sha256=ref.digest(b))
        except ValueError:pass
        else:raise AssertionError("Leakage into Git checkout accepted")
    print("PASS JP0627 synthetic full-cartridge source, bank/index/vectors, replay and guards")


def check_authentic(path: Path) -> None:
    original = ref.read_jp_rom(path)
    with tempfile.TemporaryDirectory(prefix="jp0627_authentic_") as root:
        m = ref.build(original, Path(root))
        assert m["rom_sha256"] == ref.JP_SHA256
        assert m["vectors"]["nmi"]["target_cpu"] == "E057"
        assert m["vectors"]["reset"]["target_cpu"] == "E00B"
        assert m["vectors"]["irq_brk"]["target_cpu"] == "E0F5"
        assert ref._parse_assembly(Path(root), "ROM.asm", set()) == original
        bad=Path(root).parent/"corrupt_0627.nes"
        try:
            bad.write_bytes(original[:-1] + bytes([original[-1]^1]))
            try:ref.read_jp_rom(bad)
            except ValueError:pass
            else:raise AssertionError("Corrupt ROM passed authentication")
        finally:bad.unlink(missing_ok=True)
    print("PASS JP0627 authenticated 393232-byte source recreation and vectors")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    args=p.parse_args()
    check_fake()
    if args.rom:check_authentic(args.rom)


if __name__ == "__main__":
    main()
