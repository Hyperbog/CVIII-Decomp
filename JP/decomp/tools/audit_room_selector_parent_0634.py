#!/usr/bin/env python3
"""JP0634: ROM-authenticated conditional raw01 selector clamp/caller audit.

Static physical-bank evidence only. Does not prove actual gameplay, NMI/IRQ
ordering, or a link from raw01 $07A0 writes to raw0A room parsing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
WINDOWS = {
    (0xB87A, 0xB886): "f40344796f2beccf46d6d465f2a2130cb866a1d0da7c50c1bef6c99a8289e553",
    (0xB919, 0xB955): "0149731415bec9b7d36267e88a8d225523a853f2cf96b527ed931a6f5f5b7562",
    (0xB955, 0xB981): "1961f4591cac4e62843b22bb5681162aca889f4f33928b22a1da7becca2355b1",
    (0xBAEF, 0xBB62): "f397027b9277b28bb943dbbe1962c14905e3b1277b9cee58c26280ea2f845be7",
}
TABLE_SHA = "5dc2cd33cc3315a52720f845da6d9ad4af1b4f18fef32d6bf8629390e1cd6944"

def b(bank: bytes, address: int, size: int) -> bytes:
    if not 0x8000 <= address < 0xC000 or address+size > 0xC000:
        raise ValueError("address outside physical raw01 CPU window")
    return bank[address-0x8000:address-0x8000+size]

def clamp_instructions(code: bytes, initial: int) -> int:
    """Instruction-step the original $B91E-$B927 LDA/CMP/BCC/LDA/STA."""
    if len(code) != 10 or not 0 <= initial <= 255:
        raise ValueError("bad clamp input")
    pc = 0
    a = 0
    carry = False
    ram30 = initial
    steps = 0
    while pc < len(code):
        op = code[pc]
        steps += 1
        if steps > 5:
            raise ValueError("clamp instruction limit exceeded")
        if op == 0xA5 and code[pc+1] == 0x30:
            a = ram30
            pc += 2
        elif op == 0xC9:
            carry = a >= code[pc+1]
            pc += 2
        elif op == 0x90:
            delta = code[pc+1] if code[pc+1] < 128 else code[pc+1]-256
            pc = pc+2+(delta if not carry else 0)
        elif op == 0xA9:
            a = code[pc+1]
            pc += 2
        elif op == 0x85 and code[pc+1] == 0x30:
            ram30 = a
            pc += 2
        else:
            raise ValueError("original 6502 clamp opcode/operand mismatch")
    if pc != 10:
        raise ValueError("clamp did not reach next instruction")
    return ram30

def audit_bank(bank: bytes, *, original: bool) -> dict:
    if len(bank) != 0x4000:
        raise ValueError("requires complete physical raw01 16KiB")
    for (start, end), expected in WINDOWS.items():
        if hashlib.sha256(b(bank,start,end-start)).hexdigest() != expected:
            raise ValueError("authenticated physical original code window changed")
    if b(bank,0xB87A,12) != bytes.fromhex(
        "20 f8 b8 8d 8a 07 20 19 b9 4c ef ba"):
        raise ValueError("parent JSR/clamp/JMP chain changed")
    if b(bank,0xB91E,10) != bytes.fromhex(
        "a5 30 c9 11 90 02 a9 11 85 30"):
        raise ValueError("unsigned clamp source changed")
    if b(bank,0xB94E,3) != bytes.fromhex("20 55 b9"):
        raise ValueError("clamp helper call changed")
    if b(bank,0xBB57,11) != bytes.fromhex(
        "a5 30 4a a8 b9 62 bb 8d a0 07 60"):
        raise ValueError("source-table producer changed")
    table = b(bank,0xBB62,9)
    if original and hashlib.sha256(table).hexdigest() != TABLE_SHA:
        raise ValueError("retail source table changed")
    counts = {}
    clamp = b(bank,0xB91E,10)
    for i in range(256):
        value = clamp_instructions(clamp,i)
        if value != min(i,0x11):
            raise AssertionError("clamp not min(input,$11)")
        index = value >> 1
        if index > 8:
            raise AssertionError("nine-cell indexed read exceeded boundary")
        counts[index] = counts.get(index,0)+1
    return {
        "schema": 1,
        "kind": "ROM_STATIC_CONDITIONAL_PATH_NO_GAMEPLAY",
        "physical_bank": "raw01",
        "caller": "$B87A JSR $B8F8; STA $078A; JSR $B919; JMP $BAEF",
        "clamp": "$B91E-$B927: $30=min($30,$11)",
        "source_tail": "$BAEF-$BB61 includes contiguous $BB57 selector read",
        "all_256_clamp_inputs_stepped": True,
        "post_clamp_ram30_range": "00-11",
        "BB62_index_range_on_this_route": "00-08",
        "table_cells_reachable_from_this_route": counts,
        "authenticated_code_window_sha256": {
            "%04X-%04X" % (start,end-1):digest
            for (start,end),digest in WINDOWS.items()
        },
        "live_gameplay_route_proved": False,
        "interrupt_writer_exclusion_proved": False,
        "all_alternate_entries_excluded": False,
        "crossbank_room_loader_link_proved": False,
        "strict_new_prg_bytes": 0,
    }

def smoke() -> None:
    code = bytes.fromhex("a5 30 c9 11 90 02 a9 11 85 30")
    assert [clamp_instructions(code,i) for i in range(256)] == [
        min(i,0x11) for i in range(256)]
    for broken in (code[:4]+bytes([0])+code[5:],
                   code[:8]+bytes([0])+code[9:],
                   code[:-1]):
        try:
            clamp_instructions(broken,0x20)
        except ValueError:
            continue
        raise AssertionError("modified clamp instructions accepted")
    print("PASS JP0634 ROM-free original 6502 clamp steps and tamper refusal")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--smoke",action="store_true")
    args = p.parse_args()
    if args.smoke:
        smoke()
        return
    if not args.rom:
        p.error("--rom is required for original-ROM evidence")
    rom = args.rom.read_bytes()
    if len(rom)!=393232 or rom[:4]!=b"NES\x1a" or hashlib.sha256(rom).hexdigest()!=ROM_SHA:
        raise ValueError("original JP retail ROM identity rejected")
    report = audit_bank(rom[16+0x4000:16+0x8000],original=True)
    output = json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.write_text(output,encoding="utf-8")
    print(output,end="")

if __name__ == "__main__":
    main()
