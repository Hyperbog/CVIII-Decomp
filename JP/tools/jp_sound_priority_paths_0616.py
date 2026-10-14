#!/usr/bin/env python3
"""JP0616: ROM-locked symbolic execution of original sound-dispatch gates.

Executes only the precisely SHA-locked branch spans of raw bank $0C.
Does not assert caller liveness, classify music/SFX or change game behavior.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK = 24
RANGES = (
    (0x8842, 0x8860, "3740c210ea0222afcc41d04a7cfaf2280647d10e0ec29e33ec2083f3b7ef1183"),
    (0x8908, 0x8928, "e6866421087126362134c804a4f0abdbdd96beb19dfc910f35c66444038650b8"),
    (0x8928, 0x8954, "b6f771d46d16919b2a00a8505ad3a5ddca3cffc75ccaafe6750df524804dde70"),
)
ROM_LENGTH = 393232
PRG_LENGTH = 262144
ANCHORS = {
    0x8842: "ad0901c950d017", 0x8849: "a5efc906901160",
    0x8850: "85efc96f90034c0889c95090e5", 0x885D: "20ae87",
    0x8908: "38e96f85efc90d9003eedd06", 0x8914: "ad9e01c9059008",
    0x891B: "a5efcd9e01b00360", 0x8923: "a5ef8d9e01",
    0x8934: "8d1540", 0x893A: "8d1040", 0x8940: "8d1140",
    0x8946: "8d1240", 0x894C: "8d1340", 0x8951: "8d1540",
}


def validated(rom: bytes) -> bytes:
    if len(rom) != ROM_LENGTH or sha256(rom).hexdigest() != ROM_SHA:
        raise ValueError("Original JP ROM required")
    prg = rom[16:16 + PRG_LENGTH]
    bank = prg[BANK * 8192:(BANK + 1) * 8192]
    for start, end, digest in RANGES:
        if sha256(bank[start - 0x8000:end - 0x8000]).hexdigest() != digest:
            raise ValueError(f"Original sound branch witness changed at {start:04X}")
    for pc, opcodes in ANCHORS.items():
        raw = bytes.fromhex(opcodes)
        if bank[pc - 0x8000:pc - 0x8000 + len(raw)] != raw:
            raise ValueError(f"Original sound control-flow anchor changed at {pc:04X}")
    return bank


def branch(bank: bytes, command: int, state: int, old_priority: int) -> dict:
    """Bounded 2A03 gate VM; stops before reset, pointer and chip side effects."""
    if not all(0 <= v <= 255 for v in (command, state, old_priority)):
        raise ValueError("Inputs must be bytes")
    pc, a, carry, zero = 0x8850, command, 0, 0
    ram = {0x0109: state, 0x019E: old_priority, 0x06DD: 0, 0xEF: 0}
    stops = {
        0x884F: "low_state_guard_return",
        0x885D: "metadata_reset_then_install",
        0x8860: "record_install_without_reset",
        0x8922: "dmc_priority_return",
        0x8928: "dmc_register_programming",
    }
    for step in range(36):
        if pc in stops:
            return {
                "decision": stops[pc], "stop_pc": f"{pc:04X}",
                "dmc_index": ram[0xEF] if command >= 0x6F else None,
                "dmc_priority_after_gate": ram[0x019E],
                "dmc_dd06_increments": ram[0x06DD],
                "instructions": step,
            }
        if not 0x8000 <= pc < 0xA000:
            raise ValueError("Unexpected branch target")
        op = bank[pc - 0x8000]
        def word():
            return bank[pc + 1 - 0x8000] | (bank[pc + 2 - 0x8000] << 8)
        if op == 0x85:  # STA zp
            ram[bank[pc + 1 - 0x8000]] = a
            pc += 2
        elif op == 0x8D:  # STA absolute
            ram[word()] = a
            pc += 3
        elif op == 0xA5:  # LDA zp
            a = ram[bank[pc + 1 - 0x8000]]
            zero = int(a == 0)
            pc += 2
        elif op == 0xAD:  # LDA absolute
            a = ram[word()]
            zero = int(a == 0)
            pc += 3
        elif op in (0xC9, 0xCD):  # CMP # / CMP absolute
            if op == 0xC9:
                operand = bank[pc + 1 - 0x8000]
                pc += 2
            else:
                operand = ram[word()]
                pc += 3
            carry, zero = int(a >= operand), int(a == operand)
        elif op == 0x38:  # SEC
            carry = 1
            pc += 1
        elif op == 0xE9:  # SBC immediate, binary 2A03 semantics
            value = bank[pc + 1 - 0x8000]
            result = a - value - (1 - carry)
            carry, a = int(result >= 0), result & 255
            zero, pc = int(a == 0), pc + 2
        elif op == 0xEE:  # INC absolute
            address = word()
            ram[address] = (ram[address] + 1) & 255
            pc += 3
        elif op == 0x4C:  # JMP absolute
            pc = word()
        elif op in (0x90, 0xB0, 0xD0):  # BCC/BCS/BNE
            offset = bank[pc + 1 - 0x8000]
            taken = ((op == 0x90 and not carry) or
                     (op == 0xB0 and carry) or
                     (op == 0xD0 and not zero))
            pc = (pc + 2 + ((offset + 128) % 256 - 128) if taken else pc + 2) & 65535
        else:
            raise ValueError(f"Unexpected opcode {op:02X} at {pc:04X}")
    raise ValueError("Original dispatch evaluator step cap exceeded")


def expected(command: int, state: int, priority: int) -> str:
    if command < 0x50:
        if state == 0x50 and command >= 0x06:
            return "low_state_guard_return"
        return "record_install_without_reset"
    if command < 0x6F:
        return "metadata_reset_then_install"
    idx = command - 0x6F
    return ("dmc_priority_return" if priority >= 5 and idx < priority
            else "dmc_register_programming")


def survey(bank: bytes) -> dict:
    counts = Counter()
    examples = {}
    for cmd in range(256):
        for prior in range(256):
            for state in (0x50, 0x00):
                r = branch(bank, cmd, state, prior)
                if r["decision"] != expected(cmd, state, prior):
                    raise AssertionError((cmd, state, prior, r))
                if cmd >= 0x6F:
                    idx = cmd - 0x6F
                    assert r["dmc_index"] == idx
                    assert r["dmc_dd06_increments"] == int(idx >= 13)
                    new = prior if r["decision"] == "dmc_priority_return" else idx
                    assert r["dmc_priority_after_gate"] == new
                counts[r["decision"]] += 1
                if cmd in (0x05, 0x06, 0x4F, 0x50, 0x6A, 0x6B, 0x6E,
                           0x6F, 0x7C, 0x7D, 0xFF) and prior in (0, 5, 13, 255) and state == 0x50:
                    examples[f"{cmd:02X}:{prior:02X}"] = r["decision"]
    return {
        "schema": "CVIII-JP-original-sound-dispatch-domain/v1",
        "original_rom_sha256": ROM_SHA,
        "authenticated_physical_prg_bank": BANK,
        "symbolic_branch_input_cases": sum(counts.values()),
        "state_0109_samples": ["00", "50"],
        "all_old_019E_byte_values_tested": True,
        "decision_counts_over_synthetic_inputs": dict(sorted(counts.items())),
        "selected_examples": examples,
        "dmc_reject_predicate": "A>=6F and $019E>=05 and (A-6F)<$019E",
        "low_guard_predicate": "A<50 and $0109==50 and A>=06",
        "dmc_inc_06DD_before_gate": "A>=7C including rejected DMC requests",
        "proves_executed_gameplay_or_dropped_sfx": False,
        "source_driver_modified": False,
        "new_strict_prg_bytes": 0,
    }


def synthetic_bank() -> bytes:
    """Synthetic opcode-domain fixture; no whole original ROM data."""
    bank = bytearray(8192)
    for pc, opcodes in ANCHORS.items():
        if pc >= 0x8928:
            continue
        raw = bytes.fromhex(opcodes)
        bank[pc - 0x8000:pc - 0x8000 + len(raw)] = raw
    return bytes(bank)


def self_test(rom: bytes, bank: bytes) -> None:
    for cmd, state, old, decision in (
        (0x05, 0x50, 0, "record_install_without_reset"),
        (0x06, 0x50, 0, "low_state_guard_return"),
        (0x06, 0x00, 0, "record_install_without_reset"),
        (0x50, 0x50, 0, "metadata_reset_then_install"),
        (0x6E, 0x50, 0, "metadata_reset_then_install"),
        (0x6F, 0x50, 5, "dmc_priority_return"),
        (0x6F, 0x50, 4, "dmc_register_programming"),
        (0x7C, 0x50, 255, "dmc_priority_return"),
        (0xFF, 0x50, 0, "dmc_register_programming"),
    ):
        assert branch(bank, cmd, state, old)["decision"] == decision
    for pc in (0x8842, 0x8849, 0x8850, 0x885D, 0x8908, 0x891B, 0x8923, 0x8934):
        damaged = bytearray(rom)
        damaged[16 + BANK * 8192 + pc - 0x8000] ^= 1
        try:
            validated(bytes(damaged))
        except ValueError:
            continue
        raise AssertionError("Damaged original witness accepted")
    print("PASS JP0616 original ROM branch witnesses, nine cases and eight corruptions")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path, nargs="?")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()
    if args.smoke:
        report = survey(synthetic_bank())
        assert report["symbolic_branch_input_cases"] == 131072
        assert report["decision_counts_over_synthetic_inputs"] == {
            "dmc_priority_return": 53050,
            "dmc_register_programming": 21190,
            "low_state_guard_return": 18944,
            "metadata_reset_then_install": 15872,
            "record_install_without_reset": 22016,
        }
        print("PASS JP0616 ROM-free 131072-input original-gate branch fixture")
        return
    if args.rom is None:
        p.error("Exact original Japanese ROM required without --smoke")
    source = args.rom.read_bytes()
    bank = validated(source)
    if args.self_test:
        self_test(source, bank)
    report = survey(bank)
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS JP0616 original sound-dispatch branch domain:",
          report["symbolic_branch_input_cases"], "synthetic inputs")
    print("Branch counts:", report["decision_counts_over_synthetic_inputs"])
    print("NOT real request liveness, actual dropped SFX, or strict PRG certification")


if __name__ == "__main__":
    main()
