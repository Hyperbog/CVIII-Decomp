#!/usr/bin/env python3
"""Original-Mesen Stage 1 branch CDLv2 census (physical 8 KiB PRG offsets).
NO commercial ROM/CDL/savestate/frame payload is written to the report.
Fork executions are distinct simulations, NOT a contiguous long playthrough.
"""
import argparse,hashlib,json,re
from pathlib import Path

JP_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
MESEN_SHA="95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0"
CORE_SHA="fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1"
PRG=262144;CHR=131072
# Checkpoint 0501's hash-pinned 4,364-byte subset, NOT the full 0507 ledger.
C0501=((261604,262),(261974,36),(147457,335),(147794,17),
 (148048,207),(148311,195),(148540,169),(149138,44),(149520,83),
 (164817,63),(165098,57),(180225,74),(180403,360),(180819,62),
 (180941,34),(181001,9),(181013,9),(182339,41),(188756,9),
 (189129,6),(189225,61),(189350,6),(192774,538),(193315,113),
 (193430,319),(193751,338),(194098,65),(194254,180),(194533,399),
 (194950,186),(195856,87))
assert len(C0501)==31 and sum(n for _,n in C0501)==4364
# Segment, frames, start frame, state-source parent; relative controller inputs
# are documented in SharedNES/0508_STAGE1_MULTIBRANCH_REFERENCE.md.
RUNS=(("play520",520,1,None),("stage220",220,521,"play520"),
 ("stage360",360,741,"stage220"),("right",1200,1101,"stage360"),
 ("idle",1200,1101,"stage360"),("right_jump",1200,1101,"stage360"),
 ("right_whip",1200,1101,"stage360"),("keepjump",1200,2301,"right_jump"),
 ("keepwhip",1200,2301,"right_jump"),("holdjump",1200,2301,"right_jump"))
STATE=re.compile(r"^STATE frame=(\d+) s=([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{2})$")
def sha(b):return hashlib.sha256(b).hexdigest()
def bits(mask,flag):return sum(bool(x&flag) for x in mask)
def filebase(name,parent):
    return name if name in ("play520","stage220","stage360") else name+"_1200"
def read_mask(path,crc=None):
    raw=path.read_bytes()
    if len(raw)!=9+PRG+CHR or raw[:5]!=b"CDLv2":
        raise ValueError("invalid Mesen2 CDLv2 size/header")
    if crc is not None and raw[5:9]!=crc:
        raise ValueError("cross-run CDL ROM header CRC differs")
    return raw[9:9+PRG],raw[5:9],sha(raw)
def read_log(path,frames,start):
    raw=path.read_bytes()
    rows=[json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    loaded=[x for x in rows if x.get("event")=="loaded"]
    summary=[x for x in rows if x.get("event")=="summary"]
    if len(loaded)!=1 or len(summary)!=1 or loaded[0].get("mesen_version")!="2.1.1" or loaded[0].get("console")!="Nes":
        raise ValueError("missing or wrong independent Mesen load/summary")
    s=summary[0]
    if not s.get("ok") or s.get("reason")!="frame_limit" or (s.get("frames_executed"),s.get("start_frame"),s.get("final_frame"))!=(frames,start,start+frames):
        raise ValueError("segment not an exact successful savestate-based frame run")
    if not any(x.get("event")=="cdl_saved" and x.get("type")=="NesPrgRom" for x in rows):
        raise ValueError("Mesen did not save PRG CDL")
    if any(x.get("error_count",0) for x in rows if x.get("event")=="lua_log"):
        raise ValueError("Mesen Lua logger errors")
    states=[]
    for row in rows:
        if row.get("event")=="lua_log":
            for line in row.get("text","").splitlines():
                m=STATE.fullmatch(line)
                if m:states.append([int(m.group(1))]+[int(m.group(i),16) for i in range(2,8)])
    if not states:raise ValueError("no sampled original RAM states")
    return {"state_samples":len(states),
       "firstlevel_18":sorted({x[1] for x in states[1:]}),
       "room_19":sorted({x[2] for x in states[1:]}),
       "secondary_68":sorted({x[3] for x in states[1:]}),
       "progress_2C":sorted({x[4] for x in states[1:]}),
       "final_sample_hex":" ".join(f"{v:02X}" for v in states[-1][1:]),
       "log_sha256":sha(raw)}
def audit(rom,emulator,directory):
    j=rom.read_bytes()
    if len(j)!=393232 or sha(j)!=JP_SHA:raise ValueError("wrong original Japanese ROM")
    if sha((emulator/"mesen-agent").read_bytes())!=MESEN_SHA or sha((emulator/"MesenCore.so").read_bytes())!=CORE_SHA:
        raise ValueError("wrong external Mesen emulator core/build")
    union=bytearray(PRG);baseline=None;crc=None;results=[]
    for name,frames,start,parent in RUNS:
        key=filebase(name,parent)
        m,c,digest=read_mask(directory/(key+".cdl"),crc)
        if crc is None:crc=c
        note=read_log(directory/(key+".jsonl"),frames,start)
        before=bits(union,1);before_data=bits(union,2)
        for i,v in enumerate(m):union[i]|=v
        results.append({"run":name,"parent_savestate":parent,"frames":frames,
          "start_frame":start,"end_frame":start+frames,
          "CDL_sha256":digest,"code":bits(m,1),"data":bits(m,2),
          "new_observed_code_vs_prior_union":bits(union,1)-before,
          "new_observed_data_vs_prior_union":bits(union,2)-before_data,**note})
        if name=="stage360":
            baseline=bytes(union)
            if (bits(union,1),bits(union,2))!=(12885,7890) or sha(bytes(v&1 for v in union))!="f3c53d374c8727d813fd526d11d2c00bc904902a139caa9e2370ae7f57042c9f":
                raise ValueError("published first 1100 Mesen frame reference drift")
    old=bytearray(PRG)
    for start,n in C0501:
        for i in range(start,start+n):
            if old[i]:raise ValueError("overlapping checkpoint-0501 manifest")
            old[i]=1
    assert baseline is not None
    banks=[]
    for b in range(32):
        i=b*8192;m=union[i:i+8192];prior=baseline[i:i+8192]
        if not bits(m,3):continue
        banks.append({"physical_bank":b,"code_bytes":bits(m,1),"data_bytes":bits(m,2),
          "code_added_since_first_1100_frames":sum(bool(v&1) and not prior[k]&1 for k,v in enumerate(m)),
          "previously_certified_0501_code_overlap":sum(bool(v&1) and old[i+k] for k,v in enumerate(m))})
    return {"schema":"jp-mesen-stage1-branch-cdl-census/v1",
      "evidence":"genuine Mesen2 mapped-ROM execution; NOT static code closure or native parity",
      "source_rom_sha256":JP_SHA,"mesen_sha256":MESEN_SHA,"core_sha256":CORE_SHA,
      "branch_runs":len(RUNS),"total_frame_executions":sum(x[1] for x in RUNS),
      "original_contiguous_playthrough_frames":1100,"fork_trajectories":7,
      "baseline_code":bits(baseline,1),"observed_unique_code":bits(union,1),
      "observed_unique_data":bits(union,2),
      "new_code_observed_after_prior_gameplay_reference":bits(union,1)-bits(baseline,1),
      "new_data_observed_after_prior_gameplay_reference":bits(union,2)-bits(baseline,2),
      "observed_0501_already_credited_code_bytes":sum(bool(union[i]&1) and old[i] for i in range(PRG)),
      "code_mask_sha256":sha(bytes(x&1 for x in union)),
      "data_mask_sha256":sha(bytes((x&2)>>1 for x in union)),
      "first_0501_proven_regions_only":4364,"complete_0507_overlap":"NOT RECONCILED",
      "per_bank":banks,"runs":results,
      "user_observed_stage":"Playable Stage 1-02 reached by right_jump branch; manually inspected original Mesen screenshot; not scene-classified",
      "new_strict_prg_bytes":0,"strict_prg_total":49404,"vpp_total":26,"checkpoint":"0507",
      "limitations":["9500 total frame executions include divergent savestate forks, not a contiguous playthrough",
        "CDL code bits do not establish control-flow closure or operand boundaries",
        "full strict 0507 physical byte ledger not yet subtracted",
        "no original-versus-native CPU/PPU/audio parity demonstrated"],
      "no_rom_or_cdl_or_savestate_or_screenshot_exported":True}
def main():
    p=argparse.ArgumentParser();p.add_argument("jp_rom",type=Path)
    p.add_argument("emulator_directory",type=Path);p.add_argument("private_run_directory",type=Path)
    p.add_argument("report_json",type=Path);a=p.parse_args()
    report=audit(a.jp_rom,a.emulator_directory,a.private_run_directory)
    a.report_json.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("PASS",report["branch_runs"],"runs",report["observed_unique_code"],"mapped code bytes")
if __name__=="__main__":main()
