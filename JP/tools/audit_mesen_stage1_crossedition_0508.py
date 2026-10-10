#!/usr/bin/env python3
"""Exact 16-byte physical PRG matches of independently observed original JP code.
Candidate transfer discovery ONLY: matching bytes cannot establish US mapper,
live callers, instruction boundaries or semantic certification.
"""
import argparse,json
from pathlib import Path
from audit_mesen_stage1_branch_0508 import RUNS,JP_SHA,PRG,sha,filebase,read_mask
US_SHA="1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6"
WINDOW=16
def code_runs(mask):
    if len(mask)!=PRG:raise ValueError("bad mask size")
    for base in range(0,PRG,8192):
        i=base
        while i<base+8192:
            if mask[i]:
                start=i
                while i<base+8192 and mask[i]:i+=1
                if i-start>=WINDOW:yield start,i
            else:i+=1
def cross(jp,us,mask):
    if len(jp)!=PRG or len(us)!=PRG or len(mask)!=PRG:
        raise ValueError("physical PRG or CDL mask length mismatch")
    unique=bytearray(PRG);ambiguous=bytearray(PRG);runs=list(code_runs(mask))
    full=[];runbytes=0
    for lo,hi in runs:
        runbytes+=hi-lo
        for i in range(lo,hi-WINDOW+1):
            token=jp[i:i+WINDOW]
            first=us.find(token)
            if first<0:continue
            target=unique if us.find(token,first+1)<0 else ambiguous
            target[i:i+WINDOW]=bytes([1])*WINDOW
        source=jp[lo:hi];target=us.find(source)
        if target>=0:
            full.append({"jp_physical_offset":lo,"us_physical_offset":target,
                "size":hi-lo,"sha256":sha(source),
                "unique_full_run":us.find(source,target+1)<0})
    return {"minimum_window":WINDOW,"code_bit_runs_ge16":len(runs),
       "code_flag_bytes_in_qualifying_runs":runbytes,
       "code_flag_bytes_in_shorter_runs":sum(mask)-runbytes,
       "unique_exact_source_bytes":unique.count(1),
       "ambiguous_only_source_bytes":sum(bool(ambiguous[i]) and not unique[i] for i in range(PRG)),
       "exact_whole_code_bit_runs":len(full),
       "unique_exact_whole_code_bit_runs":sum(x["unique_full_run"] for x in full),
       "longest_exact_whole_runs":sorted(full,key=lambda x:-x["size"])[:12],
       "unique_exact_source_mask_sha256":sha(unique),
       "ambiguous_source_mask_sha256":sha(ambiguous),
       "physical_bank_breakdown":[
           {"bank":b,
            "executed_source_code":sum(mask[b*8192:(b+1)*8192]),
            "unique_exact_source_code":sum(unique[b*8192:(b+1)*8192])}
           for b in range(32) if any(mask[b*8192:(b+1)*8192])]}
def audit(jp_path,us_path,cdl_dir):
    ja=jp_path.read_bytes();ua=us_path.read_bytes()
    if len(ja)!=393232 or sha(ja)!=JP_SHA or len(ua)!=393232 or sha(ua)!=US_SHA:
        raise ValueError("original retail ROM SHA mismatch")
    mask=bytearray(PRG)
    for name,_,_,parent in RUNS:
        code,_,_=read_mask(cdl_dir/(filebase(name,parent)+".cdl"))
        for i,v in enumerate(code):
            if v&1:mask[i]=1
    result=cross(ja[16:16+PRG],ua[16:16+PRG],bytes(mask))
    result.update({"schema":"original-JP-Mesen-physical-code-US-exact-match/v1",
       "source_jp_sha256":JP_SHA,"comparison_us_sha256":US_SHA,
       "observed_code_mask_sha256":sha(mask),"independent_mesen_source":True,
       "us_runtime_mapping_or_liveness_proved":False,
       "all_instruction_boundaries_proved":False,
       "source_rom_or_cdl_exported":False,
       "new_strict_prg_bytes":0,"strict_total":49404,"vpp_total":26})
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("jp_rom",type=Path)
    p.add_argument("us_rom",type=Path);p.add_argument("private_cdl_directory",type=Path)
    p.add_argument("report_json",type=Path);a=p.parse_args()
    v=audit(a.jp_rom,a.us_rom,a.private_cdl_directory)
    a.report_json.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print("PASS",v["unique_exact_source_bytes"],"unique cross-edition code-bit candidates")
if __name__=="__main__":main()
