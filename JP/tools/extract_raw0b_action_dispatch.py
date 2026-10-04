#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAW_BANK=0x0B
PRIMARY=0xBD67
SECONDARY=0xBE67

def load(path: Path):
    rom=path.read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    raw=prg[RAW_BANK*0x4000:(RAW_BANK+1)*0x4000]
    assert len(raw)==0x4000
    return raw

def word(raw: bytes, cpu: int) -> int:
    o=cpu-0x8000
    return raw[o] | raw[o+1]<<8

def build(raw: bytes) -> dict:
    rows=[]
    for action in range(256):
        high=bool(action&0x80)
        idx=action&0x7F
        entry=(SECONDARY if high else PRIMARY)+2*idx
        target=word(raw,entry)
        rows.append({
            "action": action,
            "table": "secondary" if high else "primary",
            "entry_cpu": entry,
            "target_cpu": target,
            "target_in_raw_bank_0b_window": 0x8000 <= target <= 0xBFFF,
        })
    blob=raw[PRIMARY-0x8000:PRIMARY-0x8000+0x200]
    return {
        "rom_sha256":ROM_SHA,
        "raw_vrc6_bank":"0B",
        "dispatcher_rule":"ASL action; carry selects BD67 vs BE67; Y=(action&7F)*2; JMP through fetched word",
        "primary_table":{"start_cpu":PRIMARY,"entries":128},
        "secondary_interpretation":{"start_cpu":SECONDARY,"entries":128},
        "raw_512_byte_table_sha256":hashlib.sha256(blob).hexdigest(),
        "distinct_targets":len(set(r["target_cpu"] for r in rows)),
        "all_targets_inside_8000_BFFF":all(r["target_in_raw_bank_0b_window"] for r in rows),
        "rows":rows,
        "semantic_status":"structural dispatch atlas; action liveness is not inferred from table shape",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("rom",type=Path)
    ap.add_argument("--output",type=Path)
    ns=ap.parse_args()
    report=build(load(ns.rom))
    text=json.dumps(report,indent=2)+"\n"
    if ns.output:
        ns.output.write_text(text,encoding="utf-8")
    else:
        print(text,end="")

if __name__=="__main__":
    main()
