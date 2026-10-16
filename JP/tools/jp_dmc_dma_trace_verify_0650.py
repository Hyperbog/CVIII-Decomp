#!/usr/bin/env python3
"""JP0650 owner-private DMC DMA CSV validator; no ROM/sample bytes output.

Requires exact Japanese ROM for real logs; --smoke uses synthetic bytes.
A recorded fetch is a real pinned-runtime hw_bus_read, NOT independent
Mesen reference execution or proof of real game Music/SFX separation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
COLUMNS=["event","epoch","cycle","cpu_addr","physical","byte","bank8",
         "bytes_before","requested_bank8"]
KIND={"power_on","state_loaded","bank_request","dma_fetch"}
PRG_SIZE=262144

def parse(stream, prg:bytes, require_byte_match:bool=False)->dict:
    if len(prg)!=PRG_SIZE:
        raise ValueError("JP0650 requires an exact 256 KiB PRG image")
    reader=csv.DictReader(stream)
    if reader.fieldnames!=COLUMNS:
        raise ValueError("JP0650 malformed or incompatible private DMA trace schema")
    epoch=0
    last_cycle=None
    expected_bank=None
    fetches=bank_requests=matched_bytes=mismatched_bytes=bank_disagreements=0
    candidates=outside=0
    observed_banks=set()
    rows=0
    for row in reader:
        rows+=1
        if None in row or any(value is None for value in row.values()):
            raise ValueError("CSV row has missing/extra fields")
        name=row["event"]
        if name=="trace_limit":
            raise ValueError("Trace was truncated at the recorder row cap")
        if name not in KIND:
            raise ValueError("Trace contains invalid or unrecognized event "+name)
        try:
            e,cycle,addr,physical,value,bank8,remaining,request=(
                int(row[k]) for k in COLUMNS[1:])
        except (ValueError,TypeError) as exc:
            raise ValueError("Bad numeric field in DMC trace") from exc
        if not 0<=cycle<=0xffffffffffffffff:
            raise ValueError("Cycle outside unsigned 64-bit domain")
        if name in {"power_on","state_loaded"}:
            if e!=epoch+1 or any(x!=-1 for x in (addr,physical,value,bank8,remaining,request)):
                raise ValueError("Invalid epoch boundary or extra guest data")
            epoch=e;last_cycle=cycle;expected_bank=None
            continue
        if epoch==0 or e!=epoch:
            raise ValueError("DMA event without matching power/load epoch")
        if cycle<last_cycle:
            raise ValueError("Events regress CPU cycle within an epoch")
        last_cycle=cycle
        if name=="bank_request":
            if not 0xC000<=addr<=0xCFFF or not 0<=request<32 or \
               (physical,value,bank8,remaining)!=(-1,-1,-1,-1):
                raise ValueError("Invalid mapper24 PRG8 bank-write intent")
            expected_bank=request
            bank_requests+=1
            continue
        if not (0x8000<=addr<=0xFFFF and 0<=physical<PRG_SIZE and
                0<=value<=255 and 0<=remaining<=65535 and request==-1):
            raise ValueError("Invalid actual sample DMA address/data/physical mapping")
        if (physical&0xFFF)!=(addr&0xFFF):
            raise ValueError("DMC DMA physical bank contradicts 4 KiB slot offset")
        if 0xC000<=addr<0xE000:
            actual=physical//8192
            if bank8!=actual or physical%8192!=addr-0xC000:
                raise ValueError("Recorded VRC6 $C000 PRG8 bank is not physical source")
            observed_banks.add(actual)
            candidates+=1
            if expected_bank is not None and expected_bank!=actual:
                bank_disagreements+=1
        elif addr>=0xE000:
            if bank8!=-1 or physical!=31*8192+addr-0xE000:
                raise ValueError("Mapper24 fixed $E000-$FFFF bank mapping violation")
            outside+=1
        else:
            if bank8!=-1:
                raise ValueError("Switchable $8000-$BFFF sample fetch mislabeled as PRG8")
            outside+=1
        if prg[physical]==value:
            matched_bytes+=1
        else:
            mismatched_bytes+=1
        fetches+=1
    if epoch==0 or rows==0:
        raise ValueError("Missing private game power/load observation epoch")
    if require_byte_match and mismatched_bytes:
        raise ValueError("DMC DMA bus-read values differ from authenticated PRG bytes")
    return {
        "schema":"CVIII-JP0650-DMC-DMA-audit/v1",
        "epochs":epoch,"rows":rows,"actual_dma_fetches":fetches,
        "mapper_bank_write_intents":bank_requests,
        "actual_c000_dma_fetches":candidates,
        "other_prg_dma_fetches":outside,
        "observed_bank8_values":sorted(observed_banks),
        "rom_byte_matches":matched_bytes,
        "rom_byte_mismatches":mismatched_bytes,
        "mapper_write_fetch_disagreements":bank_disagreements,
        "matched_independent_mesen_reference":False,
        "cpu_cycle_exact_dmc_parity_proven":False,
        "retail_music_sfx_independent_playback_proven":False,
    }

def row(event:str,e:int,cy:int,addr:int=-1,physical:int=-1,
        value:int=-1,bank8:int=-1,bytes_before:int=-1,
        requested:int=-1)->list:
    return [event,e,cy,addr,physical,value,bank8,bytes_before,requested]

def fixture(rows:list[list],prg:bytes,strict=False)->dict:
    out=io.StringIO()
    writer=csv.writer(out,lineterminator="\n")
    writer.writerow(COLUMNS)
    writer.writerows(rows)
    out.seek(0)
    return parse(out,prg,strict)

def reject(rows,prg,label)->None:
    try:fixture(rows,prg)
    except ValueError:return
    raise AssertionError("JP0650 accepted corrupt synthetic "+label)

def smoke()->None:
    prg=bytes(i&255 for i in range(PRG_SIZE))
    good=[
        row("power_on",1,100),
        row("bank_request",1,101,0xC003,requested=17),
        row("dma_fetch",1,120,0xC040,17*8192+64,64,17,17),
        row("dma_fetch",1,121,0xD000,17*8192+4096,0,17,16),
        row("dma_fetch",1,122,0xE001,31*8192+1,1,-1,1),
        row("state_loaded",2,10),
        row("dma_fetch",2,11,0xC000,3*8192,0,3,1),
    ]
    ok=fixture(good,prg,True)
    assert ok["actual_dma_fetches"]==4 and ok["actual_c000_dma_fetches"]==3
    assert ok["rom_byte_mismatches"]==0 and ok["observed_bank8_values"]==[3,17]
    for column,value,label in [
        (4,17*8192+65,"physical displacement"),
        (6,18,"wrong physical bank"),
        (2,99,"cycle regression"),
        (3,0xB000,"wrong CPU region"),
        (1,3,"unannounced epoch"),
    ]:
        broken=[x[:] for x in good]
        broken[2][column]=value
        reject(broken,prg,label)
    broken=[x[:] for x in good]
    broken[2][5]=1
    report=fixture(broken,prg)
    assert report["rom_byte_mismatches"]==1
    try:fixture(broken,prg,True)
    except ValueError:pass
    else:raise AssertionError("byte mismatch not rejected in strict mode")
    broken=[x[:] for x in good];broken[1][8]=16
    report=fixture(broken,prg)
    assert report["mapper_write_fetch_disagreements"]==2
    broken=[x[:] for x in good];broken[2][0]="invalid_fetch_map"
    reject(broken,prg,"invalid logger event")
    broken=[x[:] for x in good];broken[2][0]="trace_limit"
    reject(broken,prg,"truncated capped capture")
    broken=[x[:] for x in good];broken[5][1]=3
    reject(broken,prg,"bad new load epoch")
    reject(good,prg[:-1],"wrong PRG length")
    print("PASS JP0650 strict private DMC DMA CSV parser, bank mapping, ROM-byte checks, epochs and negatives")

def real(path:Path,trace:Path,require_match:bool)->dict:
    data=path.read_bytes()
    if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=ROM_SHA:
        raise ValueError("Only authenticated original Japanese mapper24 ROM accepted")
    if data[:4]!=b"NES\x1a" or data[4:6]!=bytes((16,16)) or \
       ((data[6]>>4)|(data[7]&0xF0))!=24:
        raise ValueError("Unexpected original Japanese mapper24 iNES header")
    with trace.open("r",encoding="utf-8",newline="") as f:
        result=parse(f,data[16:16+PRG_SIZE],require_match)
    result["original_jp_rom_sha256"]=ROM_SHA
    return result

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--rom",type=Path)
    p.add_argument("--trace",type=Path)
    p.add_argument("--strict-byte-match",action="store_true")
    p.add_argument("--json",type=Path)
    a=p.parse_args()
    if a.smoke:smoke()
    if bool(a.rom)!=bool(a.trace):
        p.error("--rom and --trace must be provided together")
    if not a.smoke and not a.trace:
        p.error("provide --smoke or --rom plus --trace")
    if a.trace:
        result=real(a.rom,a.trace,a.strict_byte_match)
        if a.json:a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                                    encoding="utf-8")
        print("PASS JP0650 private native DMA structure:",
              result["actual_dma_fetches"],"actual reads,",
              result["actual_c000_dma_fetches"],"C000 reads,",
              result["rom_byte_mismatches"],"ROM byte divergences; NOT Mesen parity")

if __name__=="__main__":main()
