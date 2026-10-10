#!/usr/bin/env python3
"""Checkpoint 0508 fixed-PRG31 live-executed micrographs, hash-only admission.

ROM-fixed CPU code is admitted ONLY when its exact bytes, instruction
boundaries, prior-gap exclusion and independent Mesen2 game execution are
checked. No whole-frame/native parity or room-$0D reachability is claimed.
Source-only audit may be replayed without private savestates; use --reference
for the complete external-execution witness.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
JP="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EMULATOR="95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0"
CORE="fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1"
BASE=31*8192
# Only these intervals are physically outside the last 0507 credited ledger.
UNCLAIMED=((0xFB96,0xFBF5),(0xFEEA,0xFF55))
# Four disjoint instruction-aligned spans = exactly 100 previously uncredited bytes.
LIVE=(
 ("intro_stream",0xFBA5,0xFBAF,"play520"),
 ("prayer_stream",0xFBB0,0xFBBA,"stage220"),
 ("active_object_slot_scan",0xFF06,0xFF11,"right_jump_1200"),
 ("object_clear_helpers",0xFF14,0xFF55,"right_jump_1200"))
SHA22="9cf1d69458fdade60302e7c95f6606e29e3a01cafec0ac79961d7c9410596608"
SHA12="c75f2332e11e13763245741d3f4ddb690f63dce3930c946cae3160090ac1488c"
SHA66="9f4374fdf490e30015a28e44abdc20c87259b501064c1d8eb9f4fee353d40d1a"
def sha(b):return hashlib.sha256(b).hexdigest()
def prg_at(prg,cpu,n):return prg[BASE+cpu-0xE000:BASE+cpu-0xE000+n]
def original_data(rom):
    image=rom.read_bytes()
    if len(image)!=393232 or sha(image)!=JP:raise ValueError("JP ROM identity failure")
    return image[16:16+262144]
def static_audit(rom):
    prg=original_data(rom)
    assert sha(prg_at(prg,0xFBA5,22))==SHA22
    assert sha(prg_at(prg,0xFF06,12))==SHA12
    assert sha(prg_at(prg,0xFF14,66))==SHA66
    # Bank selector saves previous bank before raw bank-00 call; control returns
    # via fixed E62D mapper restoration, not a game-agnostic subroutine call.
    assert prg_at(prg,0xFBA5,22)==bytes.fromhex("a9 00 20 ca e2 20 b6 8a 4c 2d e6 a9 00 20 ca e2 20 ba 8a 4c 2d e6")
    assert prg_at(prg,0xE2CA,13)==bytes.fromhex("48 a5 23 85 24 68 85 23 8d 00 80 60") or prg_at(prg,0xE2CA,12)==bytes.fromhex("48 a5 23 85 24 68 85 23 8d 00 80 60")
    assert prg_at(prg,0xE62D,5)==bytes.fromhex("a5 24 4c d0 e2")
    assert prg_at(prg,0xFF06,12)==bytes.fromhex("a2 01 bd 4e 05 f0 07 e8 e0 0d 90 f6")
    assert prg_at(prg,0xFF14,1)==bytes.fromhex("60")
    assert prg_at(prg,0xFF24,3)==bytes.fromhex("20 15 ff")
    assert prg_at(prg,0xFF55,1)==bytes.fromhex("60")
    # $FF12-$FF13 (LDA #1) was NOT executed in the scoped Mesen branches.
    assert prg_at(prg,0xFF12,2)==bytes.fromhex("a9 01")
    coverage=set()
    manifest=[]
    for name,start,end,witness in LIVE:
        if not any(lo<=start and end<=hi for lo,hi in UNCLAIMED):
            raise ValueError("outside last checkpoint unclaimed fixed gaps")
        for cpu in range(start,end+1):
            if cpu in coverage:raise ValueError("double credited byte")
            coverage.add(cpu)
        buf=prg_at(prg,start,end-start+1)
        manifest.append({"routine":name,"physical_bank":31,
            "start_cpu":f"{start:04X}","end_cpu":f"{end:04X}",
            "prg_physical_offset":BASE+start-0xE000,
            "length":len(buf),"sha256":sha(buf),"original_mesen_witness":witness})
    if len(coverage)!=100:raise ValueError("code accounting should total exactly 100")
    return prg,manifest
def disassemble(emulator,rom,first,last,private):
    result=subprocess.run([str(emulator/"mesen-agent"),str(rom),"--home",
       str(private/("disasm_%04X"%first)),"--frames","0",
       "--disassemble",str(first)+":70"],capture_output=True,text=True,check=True,timeout=45)
    entries=[json.loads(s) for s in result.stdout.splitlines() if s.strip()]
    pc=first;starts=[]
    for row in entries:
        if row.get("event")!="disassembly":continue
        if pc>last:break
        size=len(bytes.fromhex(row["bytes"]))
        if row["address"]!=pc or row["absolute_type"]!="NesPrgRom" or row["absolute_address"]!=BASE+pc-0xE000 or size not in (1,2,3):
            raise ValueError("Mesen instruction/physical-bank proof failure at %04X"%pc)
        starts.append(f"{pc:04X}/{size}/{row['text'].split()[0]}")
        pc+=size
    if pc!=last+1:raise ValueError("partial decode or instruction split")
    return starts
def reference_audit(rom,emulator,private,manifest):
    if sha((emulator/"mesen-agent").read_bytes())!=EMULATOR or sha((emulator/"MesenCore.so").read_bytes())!=CORE:
        raise ValueError("incorrect independent Mesen2 release")
    for row in manifest:
        start=int(row["start_cpu"],16);last=int(row["end_cpu"],16)
        cdl=(private/(row["original_mesen_witness"]+".cdl")).read_bytes()
        if len(cdl)!=9+262144+131072 or cdl[:5]!=b"CDLv2":raise ValueError("wrong original CDL")
        code=cdl[9:9+262144]
        for pc in range(start,last+1):
            f=code[BASE+pc-0xE000]
            if not f&1 or f&2:raise ValueError("new byte not definitely executed as CODE")
        starts=disassemble(emulator,rom,start,last,private)
        row["independent_disassembler_instruction_starts"]=len(starts)
        row["instruction_start_digest_sha256"]=sha(";".join(starts).encode())
    observed=[]
    for tag,pc,frame in (("FBA5",0xFBA5,314),("FBB0",0xFBB0,605),("FF06",0xFF06,2030)):
        path=private/(tag+"_break.jsonl")
        ev=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
        pp=[x for x in ev if x.get("event")=="program_counter"]
        ss=[x for x in ev if x.get("event")=="summary"]
        if len(pp)!=1 or pp[0]["value"]!=pc or len(ss)!=1 or ss[0]["reason"]!="debugger_break" or ss[0]["final_frame"]!=frame:
            raise ValueError("real Mesen code-entry breakpoint not reproduced")
        observed.append({"pc":f"{pc:04X}","frame":frame,"private_log_sha256":sha(path.read_bytes())})
    for tag,entry,tail in (("FBA5","FBAD","E62D"),("FBB0","FBB8","E62D")):
        data=(private/(tag+"_3000.trace")).read_bytes()
        lines=data.decode().splitlines()
        ordered=[line[:4] for line in lines if re.match(r"^[0-9A-F]{4} ",line)]
        if not (entry in ordered and tail in ordered and ordered.index(entry)<ordered.index(tail)):
            raise ValueError("actual stream walker did not return through mapper-restore exit")
        observed.append({"entry":tag,"3000_step_source_trace_sha256":sha(data),
            "fixed_mapper_restore_observed":True})
    lines=(private/"FF06_160.trace").read_text().splitlines()
    pcs={line[:4] for line in lines if re.match(r"^[0-9A-F]{4} ",line)}
    if not {"FF06","FF14","FF15","FF24","FF55"}.issubset(pcs):
        raise ValueError("incomplete actual object-slot and field-clear trace")
    observed.append({"object_slot_160_step_trace_sha256":sha((private/"FF06_160.trace").read_bytes())})
    return observed
def audit(rom,emulator=None,private=None):
    _,ranges=static_audit(rom)
    witness=None
    if emulator is not None:
        if private is None:raise ValueError("private source CDL/trace directory required")
        witness=reference_audit(rom,emulator,private,ranges)
    return {"checkpoint":"0508","original_jp_rom_sha256":JP,
        "evidence":"ROM-exact fixed byte and instruction proof; independent Mesen original-execution records",
        "reference_execution_rechecked_this_run":witness is not None,
        "new_unique_strict_prg_bytes":100,"prior_strict_prg_bytes":49404,
        "reconciled_strict_prg_bytes":49504,
        "verified_prg_percent":49504*100/262144,
        "fixed_physical_prg_frontier":"FB96","VPP":26,
        "new_code_ranges":ranges,"independent_witnesses":witness,
        "unclaimed":["FF12-FF13 absent from reference code mask","FB96-FBA4 and FBBB-FBF5 remain uncredited",
            "FEEA-FF05 remains uncredited","FBA5 raw-bank0 stream data and callers not globally closed",
            "FF06 alternative object ID/slot inputs not exhausted",
            "room state 18=0C/0D and full native game/audio parity remain open"],
        "ROM_CDL_savestates_instructions_not_exported":True}
def main():
    p=argparse.ArgumentParser();p.add_argument("rom",type=Path)
    p.add_argument("report",type=Path,nargs="?")
    p.add_argument("--reference-emulator",type=Path);p.add_argument("--private-evidence",type=Path)
    x=p.parse_args()
    out=audit(x.rom,x.reference_emulator,x.private_evidence)
    if x.report:x.report.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("0508 fixed live code:",out["new_unique_strict_prg_bytes"],"new bytes; cumulative",
          out["reconciled_strict_prg_bytes"],"reference replay",out["reference_execution_rechecked_this_run"])
if __name__=="__main__":main()
