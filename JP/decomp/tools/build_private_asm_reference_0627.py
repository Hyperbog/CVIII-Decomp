#!/usr/bin/env python3
"""Build a private, lossless, physically indexed JP cartridge assembly reference.

The output contains original copyrighted bytes. Never commit the generated
bank sources or distribute them; this tool and its non-byte indexes are safe.
A .byte listing is a reference, NOT proof a byte is an instruction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

JP_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_SIZE = 393232
HEADER_SIZE = 16
PRG_SIZE = 0x40000
CHR_SIZE = 0x20000
BANK_SIZE = 0x2000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jp_rom(path: Path) -> bytes:
    rom = path.read_bytes()
    if len(rom) != ROM_SIZE or digest(rom) != JP_SHA256:
        raise ValueError("Not the authenticated original Japanese retail ROM")
    header = rom[:HEADER_SIZE]
    if header[:4] != b"NES\x1a" or ((header[6] >> 4) | (header[7] & 0xF0)) != 24:
        raise ValueError("Invalid iNES header or wrong VRC6 mapper")
    if header[4] != 16 or header[5] != 16 or header[6] & 4:
        raise ValueError("Unexpected PRG/CHR sizes or trainer")
    return rom


def byte_rows(data: bytes, offset: int, group: str, physical_bank: int) -> list[str]:
    lines = []
    for i in range(0, len(data), 16):
        # Physical file identity is always authoritative; CPU addresses are
        # possible mappings unless PRG31 is in the fixed $E000-$FFFF window.
        file_at = offset + i
        slot = f"PRG{physical_bank:02d}" if group == "PRG" else f"CHR{physical_bank:02d}"
        physical = physical_bank * BANK_SIZE + i
        cpu = f" fixed ${0xE000 + i:04X}" if group == "PRG" and physical_bank == 31 else " mapper-dependent"
        values = ", ".join(f"${x:02X}" for x in data[i:i + 16])
        lines.append(f".byte {values} ; {slot}+${i:04X} {group}+${physical:05X} file+${file_at:06X}{cpu}")
    return lines


def prg_listing(data: bytes, bank: int) -> str:
    if len(data) != BANK_SIZE:
        raise ValueError("Expected exact 8 KiB physical PRG bank")
    offset = HEADER_SIZE + bank * BANK_SIZE
    lines = [f"; JP PRG{bank:02d}: physical 8 KiB bank, ROM file +${offset:06X}",
             "; All .byte contents are UNCLASSIFIED except the hardware vectors below.",
             "; Do not treat switchable physical offsets as proven CPU addresses."]
    if bank != 31:
        lines.extend(byte_rows(data, offset, "PRG", bank))
    else:
        lines.extend(byte_rows(data[:-6], offset, "PRG", bank))
        # The final six bytes are structurally known iNES 6502 vectors. They
        # are not six newly certified executable instruction bytes.
        for label, i in (("NMI", BANK_SIZE - 6), ("RESET", BANK_SIZE - 4),
                         ("IRQ_BRK", BANK_SIZE - 2)):
            target = int.from_bytes(data[i:i + 2], "little")
            lines.append(f".word ${target:04X} ; {label} hardware vector; PRG31+${i:04X} file+${offset+i:06X}")
    return "\n".join(lines) + "\n"


def chr_listing(data: bytes, bank: int) -> str:
    offset = HEADER_SIZE + PRG_SIZE + bank * BANK_SIZE
    return "\n".join([
        f"; JP CHR{bank:02d}: physical 8 KiB original graphics data, ROM file +${offset:06X}",
        "; Data only: not 6502 program instructions.",
        *byte_rows(data, offset, "CHR", bank), ""])


def _parse_assembly(out: Path, name: str, seen: set[str]) -> bytes:
    if name in seen:
        raise ValueError("Recursive include in generated listing")
    if not re.fullmatch(r"(?:ROM\.asm|header\.asm|PRG/prg_[0-3][0-9]\.asm|CHR/chr_[0-1][0-9]\.asm)", name):
        raise ValueError("Unsafe include in generated listing")
    result = bytearray()
    for source_line in (out / name).read_text(encoding="ascii").splitlines():
        line = source_line.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith(".include "):
            part = re.fullmatch(r'\.include "([^"]+)"', line)
            if not part:
                raise ValueError("Invalid .include format")
            result.extend(_parse_assembly(out, part.group(1), seen | {name}))
            continue
        match = re.fullmatch(r"\.(byte|word) (\$[0-9A-F]+(?:, \$[0-9A-F]+)*)", line)
        if not match:
            raise ValueError("Unsupported assembly statement: " + line)
        values = [int(s[1:], 16) for s in match.group(2).split(", ")]
        for v in values:
            if match.group(1) == "byte":
                if v > 0xFF:
                    raise ValueError("Invalid byte literal")
                result.append(v)
            else:
                if v > 0xFFFF:
                    raise ValueError("Invalid word literal")
                result.extend(v.to_bytes(2, "little"))
    return bytes(result)


def build(rom: bytes, out: Path, *, expected_sha256: str = JP_SHA256) -> dict:
    # Refuse accidental generation directly into a Git checkout. These files
    # are ROM-equivalent, even if their assembly is still mostly .byte.
    out = out.resolve()
    if any((p / ".git").exists() for p in (out, *out.parents)):
        raise ValueError("Private source output may not be inside a Git checkout")
    out.mkdir(parents=True, exist_ok=True)
    (out / "PRG").mkdir(exist_ok=True)
    (out / "CHR").mkdir(exist_ok=True)
    (out / "header.asm").write_text("; Original iNES header; data, not executable code.\n" +
        ".byte " + ", ".join(f"${x:02X}" for x in rom[:HEADER_SIZE]) + "\n", encoding="ascii")
    manifest = {"schema": 1, "rom_sha256": expected_sha256, "retail_file_bytes": ROM_SIZE,
                "prg_bytes": PRG_SIZE, "chr_bytes": CHR_SIZE,
                "bank_size": BANK_SIZE, "prg_banks": [], "chr_banks": [],
                "classification": "unclassified-by-default; structural hardware vectors only",
                "certification_delta_bytes": 0}
    index = ["region\tbank\tbank_offset\tphysical_offset\tfile_offset\taddress_note"]
    for kind, count, base in (("PRG", 32, HEADER_SIZE),
                              ("CHR", 16, HEADER_SIZE + PRG_SIZE)):
        for bank in range(count):
            part = rom[base + bank * BANK_SIZE:base + (bank + 1) * BANK_SIZE]
            filename = f"{kind}/{'prg' if kind=='PRG' else 'chr'}_{bank:02d}.asm"
            text = prg_listing(part, bank) if kind == "PRG" else chr_listing(part, bank)
            (out / filename).write_text(text, encoding="ascii")
            cpu_window = "fixed_E000_FFFF" if kind == "PRG" and bank == 31 else (
                "mapper_dependent" if kind == "PRG" else "ppu_chr_not_cpu")
            manifest[kind.lower() + "_banks"].append({
                "bank": bank, "size": len(part), "file_offset": base + bank * BANK_SIZE,
                "sha256": digest(part), "asm": filename, "address_context": cpu_window})
            for i in range(0, BANK_SIZE, 16):
                index.append(f"{kind}\t{bank:02d}\t{i:04X}\t{bank*BANK_SIZE+i:05X}\t"
                             f"{base+bank*BANK_SIZE+i:06X}\t{cpu_window}")
    manifest["vectors"] = {}
    for label, pos in (("nmi", 0x3FFFA), ("reset", 0x3FFFC), ("irq_brk", 0x3FFFE)):
        target = int.from_bytes(rom[HEADER_SIZE + pos:HEADER_SIZE + pos + 2], "little")
        if not 0xE000 <= target <= 0xFFFF:
            raise ValueError("Fixed-vector target unexpectedly outside bank31")
        manifest["vectors"][label] = {"physical_prg_offset": pos,
                                      "file_offset": HEADER_SIZE + pos,
                                      "target_cpu": f"{target:04X}",
                                      "classification": "vector_pointer_structural"}
    (out / "ROM.asm").write_text("; Private complete ROM byte reference, not all 6502 instructions.\n"+
        ".include \"header.asm\"\n" + "".join(
            f'.include "PRG/prg_{i:02d}.asm"\n' for i in range(32)) + "".join(
            f'.include "CHR/chr_{i:02d}.asm"\n' for i in range(16)), encoding="ascii")
    (out / "physical_offsets.tsv").write_text("\n".join(index) + "\n", encoding="ascii")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="ascii")
    reconstructed = _parse_assembly(out, "ROM.asm", set())
    if reconstructed != rom or digest(reconstructed) != expected_sha256:
        raise ValueError("Full bank source did not reproduce authoritative JP retail ROM")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    manifest = build(read_jp_rom(args.rom), args.out)
    print("PASS JP0627 full 393232-byte ROM assembly representation round-trip")
    print("PRG banks:", len(manifest["prg_banks"]), "CHR banks:", len(manifest["chr_banks"]))
    print("Fixed vectors:", manifest["vectors"])
    print("Unclassified source bytes are NOT verified code; strict PRG progress unchanged.")


if __name__ == "__main__":
    main()
