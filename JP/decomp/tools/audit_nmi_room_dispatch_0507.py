#!/usr/bin/env python3
"""0507 exact NMI bank-$0A entry + conditional state-target graph.

Only raw-$0A:B4CC-B4D0 is promoted to the strict ROM coverage ledger.
All other decoded bytes require selector, helper, and mapper provenance.
"""
from __future__ import annotations
import hashlib,json,sys
from collections import deque
from pathlib import Path
from audit_nmi_fixed_scheduler_banked import OPS,BR,TERM

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ENTRY_SHA="0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7"
CANDIDATE_SHA="807363d09368f7ae6ceaeae000df0fc50f56bba5bd2871ca749d7236ec9f3828"
ROOTS=[0xB570,0xB58C,0xB597,0xB5A3,0xB5CC,0xB5DA,
       0xB614,0xB622,0xB64E,0xB5CC,0xB5DA,0xB662]
RANGES=[[0xB49A,0xB4B1],[0xB4CC,0xB4D1],[0xB4E9,0xB502],
        [0xB570,0xB68E],[0xB6A4,0xB6E8],[0xB7F7,0xB8A6]]
def candidate_graph(bank):
    q=deque([0xB4CC,*ROOTS,0xB6A4]);seen={};external=[]
    while q:
        pc=q.popleft()
        if pc in seen:continue
        assert 0x8000<=pc<0xC000,hex(pc)
        op=bank[pc-0x8000]
        assert op in OPS,(hex(pc),hex(op))
        mn,mode,n=OPS[op]
        raw=bank[pc-0x8000:pc-0x8000+n]
        assert len(raw)==n
        arg=raw[1] if n==2 else raw[1]|(raw[2]<<8) if n==3 else None
        if mode=='rel':arg=(pc+n+(arg if arg<128 else arg-256))&65535
        seen[pc]=(mn,mode,n,arg,raw)
        if pc in (0xB4CE,0xB68B):
            # E7FB consumes caller return; inline pointer bytes are DATA.
            assert mn=='JSR' and arg==0xE7FB
            external.append(('inline',pc,arg))
            continue
        if mn in BR:q.extend((arg,pc+n))
        elif mn=='JSR':
            if arg>=0xE000:external.append(('fixed-jsr',pc,arg))
            elif arg>=0x8000:q.append(arg)
            else:external.append(('nonprg-jsr',pc,arg))
            q.append(pc+n)
        elif mn=='JMP':
            if mode=='abs':
                if arg>=0xE000:external.append(('fixed-jmp',pc,arg))
                elif arg>=0x8000:q.append(arg)
                else:external.append(('nonprg-jmp',pc,arg))
            else:external.append(('indirect',pc,arg))
        elif mn not in TERM:q.append(pc+n)
        assert len(seen)<=500
    consumed={byte for pc,(_,_,n,_,_) in seen.items() for byte in range(pc,pc+n)}
    assert len(consumed)==sum(n for _,_,n,_,_ in seen.values())
    return seen,consumed,external

def audit(rom_path):
    rom=Path(rom_path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+262144]
    fixed=prg[31*8192:32*8192]
    bank=prg[10*16384:11*16384]
    rf=lambda a,n:fixed[a-0xE000:a-0xE000+n]
    rb=lambda a,n:bank[a-0x8000:a-0x8000+n]
    assert rf(0xE526,8)==bytes.fromhex("a9 0a 20 d0 e2 4c cc b4")
    assert rf(0xE2D0,6)==bytes.fromhex("85 23 8d 00 80 60")
    assert rf(0xE360,3)==bytes.fromhex("20 fb e7")
    ptrs=[int.from_bytes(rf(0xE363+2*i,2),'little') for i in range(16)]
    assert ptrs[13]==0xE526
    assert rb(0xB4CC,5)==bytes.fromhex("a5 19 20 fb e7")
    assert hashlib.sha256(rb(0xB4CC,5)).hexdigest()==ENTRY_SHA
    assert [int.from_bytes(rb(0xB4D1+2*i,2),'little') for i in range(12)]==ROOTS
    assert rb(0xB689,5)==bytes.fromhex("a5 68 20 fb e7")
    assert int.from_bytes(rb(0xB68E,2),'little')==0xB6A4
    assert rb(0xB58C,11)==bytes.fromhex("a9 6b 20 49 e2 20 e9 b4 e6 19 60")
    assert rb(0xB4E9,5)==bytes.fromhex("a9 00 85 68 60")
    assert rb(0xB597,12)==bytes.fromhex("20 89 b6 a5 68 c9 ff d0 02 e6 19 60")
    assert rb(0xB6A8,12)==bytes.fromhex("20 73 b8 b0 01 60 20 85 e7 20 f7 b7")
    assert rb(0xB808,3)==bytes.fromhex("20 96 fb")
    nodes,used,exits=candidate_graph(bank)
    assert (len(nodes),len(used))==(281,582)
    assert len([x for x in exits if x[0]=='inline'])==2
    assert not (set(range(0xB4D1,0xB4E9))&used)
    assert len([pc for pc,(mn,mode,n,arg,raw) in nodes.items()
        if mn=='JSR' and arg==0xFB96])==11
    ss=sorted(used);actual=[]
    for a in ss:
        if not actual or a!=actual[-1][1]:actual.append([a,a+1])
        else:actual[-1][1]=a+1
    assert actual==RANGES
    ranges=[{'start_cpu':f'{lo:04X}',
          'end_cpu_inclusive':f'{hi-1:04X}',
          'length':hi-lo,'sha256':hashlib.sha256(rb(lo,hi-lo)).hexdigest()}
        for lo,hi in RANGES]
    digest=hashlib.sha256(json.dumps(ranges,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==CANDIDATE_SHA
    # One five-byte raw-0A interval is NEW. Fixed caller and other roots not counted.
    assert all(not (lo<=addr<hi) for lo,hi in ((0x83D1,0x8411),(0x84EA,0x8524))
        for addr in range(0xB4CC,0xB4D1))
    # Tempting raw-$0B immediate values are NOT direct script-ID producers.
    other=prg[11*16384:12*16384]
    read0b=lambda a,n:other[a-0x8000:a-0x8000+n]
    assert read0b(0x863B,5)==bytes.fromhex("a9 24 9d 06 06")
    assert read0b(0x9234,5)==bytes.fromhex("a9 25 9d c1 05")
    assert read0b(0x9531,5)==bytes.fromhex("a9 26 20 49 e2")
    assert read0b(0xB4BC,5)==bytes.fromhex("a9 24 20 49 e2")
    return {'checkpoint':'0507','jp_rom_sha256':ROM_SHA,
      'strict_new_bytes':5,'strict_new_mapping':'raw VRC6 0A, physical PRG21',
      'strict_new_cpu_range':'B4CC-B4D0','strict_new_sha256':ENTRY_SHA,
      'strict_cumulative_prg_bytes':49404,
      'first_level_nmi_target':'selector index 0D -> fixed E526 (bank 0A) -> B4CC',
      'candidate_only':{'encoded_state_words':12,'instruction_starts':281,
        'code_and_operand_bytes':582,'range_fingerprint_sha256':digest,
        'candidate_ranges':ranges,'jsr_fixed_FB96_sites':11,
        'selector_18_and_19_domains':'UNPROVED'},
      'open_edges':['selector $18 index 0D liveness and $19 producer domain',
        'cross-frame $19/$68 mutation and $B6A4 carry precheck',
        'helper PRG-return contexts and $07A0-indexed room pointer table',
        'AI-script IDs $24/$25/$26 actual producers and FC17',
        'FD62,Y and renderer $10 last-writer'],
      'native_test_cases':65536}
if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_nmi_room_dispatch_0507.py JP.nes [report.json]')
    report=audit(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('0507 JP ROM PASS',report['jp_rom_sha256'])
    print('strict B4CC-B4D0: PASS 5 bytes',ENTRY_SHA,'cumulative 49404')
    print('conditional CFG: 281 starts / 582 candidate bytes / 12 encoded slots')
    print('candidate range fingerprint',CANDIDATE_SHA)
    print('selector $18/$19 and cross-frame paths: OPEN')
