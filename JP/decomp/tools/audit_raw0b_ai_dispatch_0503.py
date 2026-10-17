#!/usr/bin/env python3
"""ROM-locked JP bank-$0B AI-script dispatcher audit; liveness stays open."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED_TABLE_SHA = "eb075c21401906325dc497d6537978590dccf193abc3897d42a4935533800a13"
PATTERNS = {
    "STA_abs_X_05EF": bytes.fromhex("9d ef 05"),
    "STA_abs_Y_05EF": bytes.fromhex("99 ef 05"),
    "STA_abs_05EF": bytes.fromhex("8d ef 05"),
    "STY_abs_05EF": bytes.fromhex("8c ef 05"),
    "ORA_abs_X_05EF": bytes.fromhex("1d ef 05"),
}
COUNTS = {"STA_abs_X_05EF": 96, "STA_abs_Y_05EF": 23,
          "STA_abs_05EF": 5, "STY_abs_05EF": 2, "ORA_abs_X_05EF": 1}

def audit(path: Path) -> dict:
    rom = path.read_bytes()
    assert len(rom) == 0x60010
    assert hashlib.sha256(rom).hexdigest() == ROM_SHA
    assert rom[6] & 0xF0 == 0x80 and rom[7] & 0xF0 == 0x10
    prg = rom[16:16+0x40000]
    bank = prg[0x0B*0x4000:0x0C*0x4000]
    def read(cpu: int, n: int) -> bytes:
        assert 0x8000 <= cpu and cpu+n <= 0xC000
        return bank[cpu-0x8000:cpu+n-0x8000]
    assert read(0xBD11, 0x19) == bytes.fromhex(
        "a5 a8 f0 05 20 44 e7 b0 f6 bd ef 05 f0 f1 c9 27 d0 05 "
        "20 cd 82 f0 e8 0a a8")
    assert read(0xBD2A, 0x1E) == bytes.fromhex(
        "b9 a3 be 85 02 b9 a4 be 85 03 bd c1 05 0a 0a 18 65 02 "
        "85 02 a5 03 69 00 85 03 a0 00 b1 02")
    assert read(0xBD48, 0x1F) == bytes.fromhex(
        "0a b0 0e a8 b9 67 bd 85 00 b9 68 bd 85 01 6c 00 00 "
        "a8 b9 67 be 85 00 b9 68 be 85 01 6c 00 00")
    assert read(0xBF79, 4) == bytes.fromhex("19 00 00 00")
    assert hashlib.sha256(read(0xBD67, 0x200)).hexdigest() == EXPECTED_TABLE_SHA
    targets=[]
    for action in range(256):
        entry=(0xBE67 if action & 0x80 else 0xBD67) + ((action << 1) & 0xFF)
        target=int.from_bytes(read(entry,2), "little")
        assert 0x8000 <= target < 0xC000
        targets.append(target)
    assert len(set(targets)) == 217
    assert int.from_bytes(read(0xBEA3,2),"little") == targets[0x9E] == 0xBF79
    assert int.from_bytes(read(0xBEA5,2),"little") == 0xA61A
    census={}
    for name, pattern in PATTERNS.items():
        locations=[]
        for raw_bank in range(16):
            region=prg[raw_bank*0x4000:(raw_bank+1)*0x4000]
            i=0
            while True:
                i=region.find(pattern,i)
                if i<0: break
                locations.append({"raw_bank":f"{raw_bank:02X}","cpu":f"{0x8000+i:04X}"})
                i+=1
        assert len(locations)==COUNTS[name],(name,len(locations))
        census[name]={"count":len(locations),"locations":locations}
    return {
        "jp_rom_sha256":ROM_SHA,
        "dispatch_code_BD11_BD66_sha256":hashlib.sha256(read(0xBD11,0x56)).hexdigest(),
        "mechanical_action_slots":256,
        "distinct_mechanical_targets":217,
        "action_9E_alias":"BEA3 -> BF79 (script data, not proved executable)",
        "script_id_01_pointer_candidate":"A61A",
        "global_raw_pattern_candidate_writers":census,
        "live_script_action_domain":"UNRESOLVED",
        "strict_new_rom_bytes":0,
    }

def main() -> None:
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: audit_raw0b_ai_dispatch_0503.py JP.nes [candidates.json]")
    report=audit(Path(sys.argv[1]))
    if len(sys.argv)==3:
        Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("JP ROM: OK",report["jp_rom_sha256"])
    print("JP $BD11-$BD66: OK",report["dispatch_code_BD11_BD66_sha256"])
    print("mechanical action slots:",report["mechanical_action_slots"])
    print("distinct targets:",report["distinct_mechanical_targets"])
    print("STA $05EF,X raw candidates:",report["global_raw_pattern_candidate_writers"]["STA_abs_X_05EF"]["count"])
    print("new semantic ROM bytes: 0; live producer domain remains open")

if __name__ == "__main__":
    main()
