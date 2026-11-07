#!/usr/bin/env python3
"""JP0651: compare an independent, pinned MesenCE DMC DMA reference to
JP0650 native actual DMA-get events. Fail closed on all deviations.

A pair of matching CSVs is consistent EVIDENCE, not automatic Mesen binary
attestation or a claim real-JP gameplay was executed. No raw sample bytes
are exported in JSON reports or test fixtures.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from jp_dmc_dma_trace_verify_0650 import ROM_SHA, PRG_SIZE, parse as native_parse
from jp_dmc_dma_trace_verify_0650 import COLUMNS as NATIVE_COLUMNS
from jp_dmc_conflict_sidecar_0651 import classified_ordinals

MESEN_COLUMNS=["event","cycle","cpu_addr","physical","byte"]
CAP=200000

def table(data:str,expected:list[str])->list[dict[str,str]]:
    source=io.StringIO(data)
    reader=csv.DictReader(source,strict=True)
    if reader.fieldnames!=expected:
        raise ValueError("Invalid or incompatible source-specific CSV schema")
    rows=[]
    try:
        for row in reader:
            if None in row or any(x is None for x in row.values()):
                raise ValueError("Missing/extra fields in trace")
            rows.append(row)
            if len(rows)>CAP+1:
                raise ValueError("Oversized / truncated observation")
    except csv.Error as exc:
        raise ValueError("Malformed CSV quoting") from exc
    return rows

def number(s:str)->int:
    if not s or s.strip()!=s or (s.startswith("+")) or not s.isdecimal():
        raise ValueError("Noncanonical unsigned integer field")
    n=int(s)
    if not 0<=n<=0xFFFFFFFFFFFFFFFF:
        raise ValueError("Numeric source value overflows uint64")
    return n

def mesen_decode(text:str,prg:bytes,classified:frozenset[int]=frozenset())->list[tuple[int,int,int,int]]:
    if len(prg)!=PRG_SIZE:raise ValueError("Need authenticated 256-KiB original PRG")
    rows=table(text,MESEN_COLUMNS)
    if len(rows)<2:raise ValueError("At least two real DMC events required for timing comparison")
    result=[]
    for row in rows:
        if row["event"]=="trace_limit":
            raise ValueError("Truncated MesenCE source, no parity claim")
        if row["event"]!="dma_fetch":
            raise ValueError("Non-DMC or unrecognized MesenCE reference event")
        cycle=number(row["cycle"])
        addr=number(row["cpu_addr"])
        physical=number(row["physical"])
        byte=number(row["byte"])
        if not(0x8000<=addr<=0xFFFF and 0<=physical<PRG_SIZE and 0<=byte<=255):
            raise ValueError("Invalid independently observed DMA source")
        if physical%4096!=addr%4096:
            raise ValueError("Mesen reference CPU address disagrees with physical slot")
        if 0xC000<=addr<0xE000:
            if physical%8192!=addr-0xC000:
                raise ValueError("Mesen physical bank8 address mismatch")
        elif addr>=0xE000:
            if physical!=31*8192+addr-0xE000:
                raise ValueError("Mesen fixed PRG31 physical mapping mismatch")
        if prg[physical]!=byte and len(result) not in classified:
            raise ValueError("Unclassified independent MesenCE ROM-byte difference")
        if result and cycle<=result[-1][0]:
            raise ValueError("Mesen DMA cycle did not increase")
        result.append((cycle,addr,physical,byte))
    return result

def native_decode(
    text:str,prg:bytes,conflicts:str|None=None
)->tuple[list[tuple[int,int,int,int]],frozenset[int]]:
    # Keep JP0650's original structure, exact ROM physical offsets,
    # per-epoch ordering and mapper-intent checks. Only the explicit,
    # independently classified register-conflict byte check is relaxed.
    summary=native_parse(io.StringIO(text),prg,False)
    rows=table(text,NATIVE_COLUMNS)
    if summary["epochs"]!=1 or not rows or rows[0]["event"]!="power_on":
        raise ValueError("Require one native power-on epoch with no state loads")
    if summary["mapper_write_fetch_disagreements"]:
        raise ValueError("Native mapper bank-request inconsistency must be investigated")
    results=[]
    for row in rows:
        if row["event"]=="dma_fetch":
            n=tuple(number(row[key]) for key in ("cycle","cpu_addr","physical","byte"))
            if results and n[0]<=results[-1][0]:
                raise ValueError("Native DMA fetch cycle did not increase")
            results.append(n)
    if len(results)<2:
        raise ValueError("Native trace has too few actual DMA gets to compare timing")
    if len(results)!=summary["actual_dma_fetches"]:
        raise ValueError("Native declared DMA count disagrees with data")
    classified=classified_ordinals(results,prg,conflicts)
    if len(classified)!=summary["rom_byte_mismatches"]:
        raise ValueError("JP0650 native ROM-byte discrepancy count is inconsistent")
    return results,classified


def compare(native:str,mesen:str,prg:bytes,conflicts:str|None=None)->dict:
    n,classified=native_decode(native,prg,conflicts)
    m=mesen_decode(mesen,prg,classified)
    if len(n)!=len(m):
        raise ValueError(f"DMC DMA event count mismatch: native {len(n)}, reference {len(m)}")
    for i,(a,b) in enumerate(zip(n,m)):
        # Do NOT normalize or substitute original ROM bytes in conflict cases.
        # The independently returned Mesen DMA byte must equal the native
        # bus-returned byte, even when both differ from the cartridge PRG.
        if a[1:]!=b[1:]:
            raise ValueError(f"Independent DMC CPU/physical/byte mismatch at fetch #{i}")
        if i and a[0]-n[i-1][0]!=b[0]-m[i-1][0]:
            raise ValueError(f"DMC inter-fetch CPU cycle gap mismatch at fetch #{i}")
    offset=n[0][0]-m[0][0]
    banks=sorted({event[2]//8192 for event in n if 0xC000<=event[1]<0xE000})
    return {
        "schema":"CVIII-JP0651-independent-MesenCE-DMC-pair/v1",
        "paired_dma_fetches":len(n),
        "observed_switchable_dmc_banks":banks,
        "native_minus_mesen_cycle_offset":offset,
        "cpu_address_and_physical_prg_sequence_match":True,
        "original_rom_byte_sequence_match":len(classified)==0,
        "native_verified_register_conflict_fetches":len(classified),
        "nonconflict_rom_byte_fetches":len(n)-len(classified),
        "actual_returned_dma_byte_sequence_match":True,
        "verified_conflict_bytes_match_mesen":True,
        "inter_fetch_cpu_cycle_gaps_match":True,
        "full_gameplay_execution_reproduced":False,
        "mesen_executable_original_rom_attested":False,
        "controller_input_and_save_epoch_attested":False,
        "music_sfx_source_ownership_proven":False,
        "audible_pcm_parity_proven":False
    }

def csv_rows(cols, rows):
    f=io.StringIO()
    writer=csv.writer(f,lineterminator="\n")
    writer.writerow(cols)
    writer.writerows(rows)
    return f.getvalue()

def smoke():
    # Invented memory and timing, NOT original Japanese sample bytes.
    prg=bytes(i%256 for i in range(PRG_SIZE))
    n=[
        ["power_on",1,100,-1,-1,-1,-1,-1,-1],
        ["bank_request",1,105,0xC000,-1,-1,-1,-1,17],
        ["dma_fetch",1,120,0xC040,17*8192+64,64,17,17,-1],
        ["dma_fetch",1,232,0xC041,17*8192+65,65,17,16,-1],
        ["bank_request",1,300,0xC000,-1,-1,-1,-1,3],
        ["dma_fetch",1,345,0xD000,3*8192+4096,0,3,5,-1],
        ["dma_fetch",1,460,0xE001,31*8192+1,1,-1,1,-1],
    ]
    m=[
        ["dma_fetch",1000,0xC040,17*8192+64,64],
        ["dma_fetch",1112,0xC041,17*8192+65,65],
        ["dma_fetch",1225,0xD000,3*8192+4096,0],
        ["dma_fetch",1340,0xE001,31*8192+1,1],
    ]
    def invoke(nx=n,mx=m):
        return compare(csv_rows(NATIVE_COLUMNS,nx),csv_rows(MESEN_COLUMNS,mx),prg)
    good=invoke()
    assert good["paired_dma_fetches"]==4
    assert good["observed_switchable_dmc_banks"]==[3,17]
    assert good["native_minus_mesen_cycle_offset"]==-880
    assert good["inter_fetch_cpu_cycle_gaps_match"]
    def fail(nx,mx,label):
        try:invoke(nx,mx)
        except ValueError:return
        raise AssertionError("JP0651 wrongly certified "+label)
    for idx,col,value,label in [
        (2,3,0xD040,"different CPU address"),
        (2,4,17*8192+65,"physical offset changed"),
        (3,5,0,"original sample byte corruption"),
        (3,2,234,"cycle gap drift"),
        (5,1,2,"hidden state load epoch"),
        (5,8,7,"wrong bank-write intent"),
    ]:
        corrupt=[r[:] for r in n]
        corrupt[idx][col]=value
        fail(corrupt,m,label)
    for idx,col,value,label in [
        (1,1,1113,"independent cycle drift"),
        (2,2,0xC000,"independent CPU source mismatch"),
        (2,3,3*8192+4095,"independent physical bank drift"),
        (0,4,63,"independent original sample byte drift"),
        (1,0,"trace_limit","Mesen truncated"),
        (0,1,1000+1,"nonconstant cycle offset"),
    ]:
        corrupt=[r[:] for r in m]
        corrupt[idx][col]=value
        fail(n,corrupt,label)
    fail(n,m[:-1],"missing Mesen DMC fetch")
    fail(n[:-1],m,"missing native DMC fetch")
    fail(n+[n[-1][:]],m,"duplicate native DMA fetch")
    fail(n,m+[m[-1][:]],"extra Mesen DMC fetch")
    fail([["power_on",1,10,-1,-1,-1,-1,-1,-1]],m,"zero native fetches")
    fail(n,m[:1],"single Mesen event")
    fail(n+[["trace_limit",1,999,-1,-1,-1,-1,-1,-1]],m,"native incomplete")
    # JP0651 conflict-aware synthetic cases: never substitute expected ROM
    # bytes for observed values, and never permit an unsupported exception.
    n2=[r[:] for r in n]
    m2=[r[:] for r in m]
    n2[3][3]=m2[1][2]=0xC055
    n2[3][4]=m2[1][3]=17*8192+0x55
    n2[3][5]=m2[1][4]=0x54  # Synthetic bus-conflict value; PRG has 0x55.
    sidecars=[[1,232,0xC055,17*8192+0x55,0x4016,1,0x4015,1]]
    from jp_dmc_conflict_sidecar_0651 import COLUMNS as CONFLICT_COLUMNS
    def pair(ns=n2,ms=m2,cs=sidecars):
        return compare(csv_rows(NATIVE_COLUMNS,ns),
                       csv_rows(MESEN_COLUMNS,ms),prg,
                       csv_rows(CONFLICT_COLUMNS,cs) if cs is not None else None)
    proof=pair()
    assert proof["paired_dma_fetches"]==4
    assert proof["native_verified_register_conflict_fetches"]==1
    assert proof["nonconflict_rom_byte_fetches"]==3
    assert proof["actual_returned_dma_byte_sequence_match"]
    assert not proof["original_rom_byte_sequence_match"]
    assert not proof["mesen_executable_original_rom_attested"]
    def conflict_fail(ns,ms,cs,label):
        try:pair(ns,ms,cs)
        except ValueError:return
        raise AssertionError("JP0651 wrongly approved "+label)
    conflict_fail(n2,m2,None,"missing required sidecar")
    conflict_fail(n2,m2,[],"missing conflict row")
    conflict_fail(n2,m2,sidecars+sidecars,"duplicate conflict row")
    for col,val,label in [
        (0,2,"wrong power epoch"),(1,233,"wrong cycle"),
        (2,0xC056,"wrong DMC address"),(3,17*8192+86,"wrong PRG offset"),
        (4,0x6000,"non-IO held CPU address"),(5,0,"CPU writing"),
        (6,0x4016,"forged register alias"),(7,0,"missing alias condition"),
    ]:
        bad=[r[:] for r in sidecars]
        bad[0][col]=val
        conflict_fail(n2,m2,bad,label)
    bad=[r[:] for r in m2];bad[1][4]=0x55
    conflict_fail(n2,bad,sidecars,"Mesen substituted original ROM byte")
    bad=[r[:] for r in m2];bad[1][4]=0x53
    conflict_fail(n2,bad,sidecars,"Mesen disagreement with native conflict byte")
    bad=[r[:] for r in m2];bad[0][4]=63
    conflict_fail(n2,bad,sidecars,"unclassified Mesen ROM-byte change")
    bad=[r[:] for r in m2];bad[2][1]+=1
    conflict_fail(n2,bad,sidecars,"conflict trace CPU-cycle gap drift")
    bad=[r[:] for r in n2];bad[3][5]=0x55
    conflict_fail(bad,m2,sidecars,"sidecar attached to ordinary ROM byte")
    bad=[r[:] for r in n2];bad[2][8]=19
    conflict_fail(bad,m2,sidecars,"mapper intent mismatch concealed by sidecar")
    conflict_fail(n2,m2,[sidecars[0][:-1]],"truncated sidecar record")
    conflict_fail(n2,m2,[sidecars[0]+[0]],"extra sidecar column")
    empty=compare(csv_rows(NATIVE_COLUMNS,n),csv_rows(MESEN_COLUMNS,m),
                  prg,csv_rows(CONFLICT_COLUMNS,[]))
    assert empty["native_verified_register_conflict_fetches"]==0
    print("PASS JP0651 strict independent DMC pairs, conflict classification, returned-byte fidelity and adversarial negatives")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--rom",type=Path)
    p.add_argument("--native",type=Path)
    p.add_argument("--mesen",type=Path)
    p.add_argument("--conflicts",type=Path,help="JP0650 same-session held-CPU conflict sidecar (required for ROM-byte differences)")
    p.add_argument("--json",type=Path)
    a=p.parse_args()
    if a.smoke:smoke()
    if a.conflicts and not all(x is not None for x in (a.rom,a.native,a.mesen)):
        p.error("--conflicts requires --rom, --native and --mesen")
    if any(x is not None for x in (a.rom,a.native,a.mesen)):
        if not all(x is not None for x in (a.rom,a.native,a.mesen)):
            p.error("Need --rom, --native, --mesen together")
        rom=a.rom.read_bytes()
        if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=ROM_SHA:
            raise ValueError("Only the exact authenticated Japanese mapper24 ROM is eligible")
        if rom[:4]!=b"NES\x1a" or rom[4:6]!=bytes((16,16)) or \
           ((rom[6]>>4)|(rom[7]&0xF0))!=24:
            raise ValueError("Cartridge NES mapper24 header does not match")
        result=compare(a.native.read_text(encoding="utf-8"),
                       a.mesen.read_text(encoding="utf-8"),rom[16:16+PRG_SIZE],
                       a.conflicts.read_text(encoding="utf-8") if a.conflicts else None)
        if a.json:
            a.json.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print("JP0651 private pair passes structural source and cycle-delta checks; external original-reference provenance requires owner confirmation")
    elif not a.smoke:
        p.error("--smoke or --rom plus --native plus --mesen required")
if __name__=="__main__":main()
