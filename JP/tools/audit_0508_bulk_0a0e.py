#!/usr/bin/env python3
"""JP checkpoint 0508: ROM-locked bulk 32-KiB raw banks $0A and $0E.

This is a provenance/manifest + bounded reset-clear audit, NOT frame liveness
or promotion of provisional code/stream bytes. The published 0508 candidate
control-flow audit is reused and replayed instead of re-invented.

Run from JP/tools: python3 audit_0508_bulk_0a0e.py JP_ROM.nes report.json
Requires co-located audited 0508_expanded and 0508_phase5 modules.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

from audit_0508_expanded import audit as previous_graph, walk, decode, OPS, INLINE
from audit_0508_phase5 import audit as previous_streams

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RESET_CLEAR_SHA = None  # exact prefix asserted below, not a guessed digest
WATCH = (0x0018, 0x0019, 0x0068, 0x07A0, 0x07A6)
WRITE = {'STA', 'STX', 'STY', 'INC', 'DEC', 'ASL', 'LSR', 'ROL', 'ROR'}
DIRECT_ZP = {0x84,0x85,0x86,0x06,0x26,0x46,0x66,0xC6,0xE6}
DIRECT_ABS = {0x8C,0x8D,0x8E,0x0E,0x2E,0x4E,0x6E,0xCE,0xEE}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def phys_offset(bank: int, pc: int) -> int:
    assert bank in (10,14) and 0x8000 <= pc < 0xC000
    return 16384 * bank + (pc-0x8000)


def verify_reset_ram_clear(fixed: bytes) -> dict:
    """Execute original $E020-$E035 clearing loop after verified X=$FF.

    Original RESET $E017 LDX #FF / $E019 TXS / $E01A JSR E16C /
    $E01D JSR E151 enter E020 with X=FF. Both fixed callees contain
    no X writers. PPUSTATUS timing, NMI timing and later E211 are NOT run.
    """
    def rd(pc: int) -> int:
        assert 0xE000 <= pc <= 0xFFFF
        return fixed[pc-0xE000]
    assert bytes(rd(p) for p in range(0xE017,0xE020)) == bytes.fromhex(
        'a2 ff 9a 20 6c e1 20 51 e1')
    assert bytes(rd(p) for p in range(0xE020,0xE035)) == bytes.fromhex(
        'e8 8a 85 00 85 01 a0 00 a2 08 91 00 c8 d0 fb e6 01 e4 01 d0 f5')
    cases = 0
    steps = None
    for seed in range(32):
        ram = bytearray((seed + i*11) & 0xFF for i in range(0x800))
        x, y, a, pc, z = 0xFF, seed, 0xA5, 0xE020, False
        touched = set(); nins = 0; writes_indirect = 0
        while pc != 0xE035:
            nins += 1
            assert nins < 40000, ('loop runaway', hex(pc))
            op = rd(pc)
            if op == 0xE8:  # INX
                x = (x+1) & 255; z = x == 0; pc += 1
            elif op == 0x8A: # TXA
                a=x; z=a==0; pc+=1
            elif op == 0x85: # STA zp
                addr=rd(pc+1);ram[addr]=a;touched.add(addr);pc+=2
            elif op == 0xA0: # LDY immediate
                y=rd(pc+1);z=y==0;pc+=2
            elif op == 0xA2: # LDX immediate
                x=rd(pc+1);z=x==0;pc+=2
            elif op == 0x91: # STA ($00),Y
                assert rd(pc+1)==0
                addr=((ram[0] | (ram[1]<<8))+y) & 0xFFFF
                assert addr<0x800
                ram[addr]=a;touched.add(addr);writes_indirect+=1;pc+=2
            elif op == 0xC8: # INY
                y=(y+1)&255;z=y==0;pc+=1
            elif op == 0xD0: # BNE rel
                off=rd(pc+1);off=off if off<128 else off-256
                pc=(pc+2+(off if not z else 0)) & 0xFFFF
            elif op == 0xE6: # INC zp
                addr=rd(pc+1);ram[addr]=(ram[addr]+1)&255
                z=ram[addr]==0;touched.add(addr);pc+=2
            elif op == 0xE4: # CPX zp
                z=(x==ram[rd(pc+1)]);pc+=2
            else:raise AssertionError(('unexpected reset opcode',hex(pc),hex(op)))
        assert writes_indirect==2048, writes_indirect
        assert set(range(2048)) == touched
        # $00 and $01 hold the final buffer pointer, not zeros.
        assert ram[0]==0 and ram[1]==8
        assert all(ram[i]==0 for i in range(2,2048))
        assert all(ram[i]==0 for i in WATCH)
        assert x==8 and y==0 and a==0
        assert steps is None or steps == nins
        steps=nins; cases+=1
    return {
       'proof_scope':'fixed RESET $E020-$E034 after both preceding X-preserving fixed helpers',
       'case_count':cases, 'original_instruction_steps_per_case':steps,
       'indirect_zero_stores_per_case':2048,
       'cleared_RAM_except_pointer':'0002-07FF',
       'final_reset_pointer_zp_00_01':'00 08',
       'watchlist_zero_after_reset_clear':[f'{x:04X}' for x in WATCH],
       'not_proved':'actual PPU vblank timing / NMI timing / later arbitrary game-state mutations'
    }


def census(prg: bytes) -> dict:
    """All-offset encoded direct write candidates across all *physical* PRG.

    This deliberately permits operand/data false positives. Per-8K boundary
    containment avoids constructing instructions spanning unrelated banks.
    """
    out = {}
    for addr in WATCH:
        pattern = {op:bytes((op,addr)) for op in DIRECT_ZP} if addr<256 else {
            op:bytes((op,addr&255,addr>>8)) for op in DIRECT_ABS}
        length=2 if addr<256 else 3
        candidates=[]
        for bank in range(32):
            for pos in range(8192-length+1):
                off=bank*8192+pos
                raw=prg[off:off+length]
                if raw in pattern.values():
                    cpu=(0xE000+pos if bank==31 else 0x8000+(bank&1)*8192+pos)
                    candidates.append((bank,cpu,raw[0]))
        out[f'{addr:04X}'] = {
            'all_offset_encoding_candidates':len(candidates),
            'per_physical_bank':{f'{k:02X}':v for k,v in sorted(Counter(k for k,_,_ in candidates).items())},
            'only_three_abs_candidates' : [
                {'physical_prg':b,'cpu':f'{cpu:04X}','opcode':f'{op:02X}'}
                for b,cpu,op in candidates
            ] if addr in (0x07A0,0x07A6) else None,
            'classification':'RAW ENCODING CANDIDATES; not proof of instruction alignment/liveness'
        }
    assert out['07A0']['all_offset_encoding_candidates']==3
    assert out['07A6']['all_offset_encoding_candidates']==3
    assert [(c['physical_prg'],c['cpu']) for c in out['07A0']['only_three_abs_candidates']]==[
        (1,'A09B'),(3,'BB5E'),(21,'B7E3')]
    assert [(c['physical_prg'],c['cpu']) for c in out['07A6']['only_three_abs_candidates']]==[
        (21,'B628'),(21,'B7E0'),(21,'B89F')]
    return out


def scan_raw(bank: bytes, physical_offset: int) -> dict:
    legal=0;ctl=0;jsr_e7fb=[];write_apu=[]
    for pos in range(16384):
        op=bank[pos]
        if op not in OPS:continue
        mn,mod,n=OPS[op]
        if pos+n>16384:continue
        legal+=1
        if mn in {'JSR','JMP','BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}:ctl+=1
        if n==3 and bank[pos:pos+3]==b'\x20\xfb\xe7':jsr_e7fb.append(f'{0x8000+pos:04X}')
        if n==3 and mn in WRITE and mod=='abs':
            addr=bank[pos+1]|bank[pos+2]<<8
            if addr in (0x8000,0xC000,0xD000,0xF000,0xF001,0xF002):
                write_apu.append((0x8000+pos,addr,mn))
    return {
      'physical_prg': [physical_offset,physical_offset+1],
      'sha256':sha(bank), 'bytes_examined':len(bank),
      'all_offset_official_opcode_candidates':legal,
      'all_offset_control_flow_candidates':ctl,
      'all_offset_jsr_E7FB_patterns':jsr_e7fb,
      'all_offset_mapper_write_patterns_count':len(write_apu),
      'classification':'all-offset discovery; code/data and mapper context not proven'
    }


def audit(path: str) -> dict:
    rom=Path(path).read_bytes();assert len(rom)==393232 and sha(rom)==ROM_SHA
    prg=rom[16:16+0x40000]
    raw10=prg[10*0x4000:11*0x4000]
    raw14=prg[14*0x4000:15*0x4000]
    fixed=prg[31*8192:]
    assert sha(raw10)=='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
    assert sha(raw14)=='9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5'
    assert sha(fixed[0xFB76-0xE000:0xFB96-0xE000])=='e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7'
    assert sha(fixed[0xFB96-0xE000:0xFBB6-0xE000])=='a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157'
    prior=previous_graph(Path(path))
    room=previous_streams(path)
    assert prior['new_candidate_control_flow_atlas']['instruction_starts']==935
    assert prior['new_candidate_control_flow_atlas']['instruction_operand_bytes']==2042
    assert room['distinct_stream_source_bytes']==175
    assert room['unique_objects']==30

    bword=lambda pc:int.from_bytes(raw10[pc-0x8000:pc-0x8000+2],'little')
    roots=[0xAFA4,0xB4CC]
    ptrs=[]
    for call,(base,count) in INLINE.items():
        assert raw10[call-0x8000:call-0x8000+3]==b'\x20\xfb\xe7'
        ptrs.extend(range(base,base+2*count))
        roots.extend(bword(base+2*i) for i in range(count))
    codes, code_bytes, external, inline, writes=walk(raw10,roots)
    legacy_starts, legacy_bytes, legacy_edges, _, _ = walk(raw10,[0x84EA])
    assert len(legacy_starts)==57 and len(legacy_bytes)==120
    assert legacy_edges==[('indirect',0x8520,0x0002)]
    assert not(legacy_bytes & code_bytes)
    assert len(codes)==935 and len(code_bytes)==2042
    assert len(ptrs)==130 and not(set(ptrs)&code_bytes)
    descriptor=set(range(0xB8A6,0xB8C2))
    assert len(descriptor)==28 and raw10[0xB8C1-0x8000]==0xFF
    room_ptrs=set(range(0xB8C2,0xB8CC))
    assert len(room_ptrs)==10
    source=set(range(0xBE8B,0xBF3A));assert len(source)==175
    assert not (descriptor & code_bytes or room_ptrs & code_bytes)
    assert not (descriptor & set(ptrs) or room_ptrs & set(ptrs))
    table=prior['new_candidate_control_flow_atlas']['all_4_inline_tables']
    assert sum(t['encoded_words'] for t in table.values())==65

    producer={}
    for watched in WATCH:
        w=[{'cpu':f'{pc:04X}','operation':name,'mode':mode,'encoded_operand':f'{arg:04X}'}
           for pc,name,mode,arg in sorted(writes) if arg==watched and mode in ('zp','abs')]
        producer[f'{watched:04X}']={'candidate_graph_direct_writers':w,
                     'quantity':len(w), 'scope':'conditional 0A decode, NOT live global writers'}
    assert [producer[k]['quantity'] for k in ('0018','0019','0068','07A0','07A6')]==[2,16,11,1,3]

    # Actual fixed updater: INC $18; LDA #00; STA $19; RTS.
    fixed_inc=fixed[0xE551-0xE000:0xE558-0xE000]
    assert fixed_inc == bytes.fromhex('e6 18 a9 00 85 19 60')
    assert all(((n+1)&255)==((n+1)%256) for n in range(256))
    # No direct literal pair. This is a raw byte-pattern negative, not a
    # claim that a wider data-flow producer cannot set $18=0C.
    assert bytes.fromhex('a9 0c 85 18') not in prg
    assert bytes.fromhex('a9 0c 8d 18 00') not in prg
    return {
      'status':'BULK_0508_0A_0E_CANDIDATE_AND_RESET_CLEAR_NO_PROMOTION',
      'jp_rom_sha256':ROM_SHA, 'scoped_raw_vrc6_banks':['0A','0E'],
      'scoped_physical_prg_banks':[20,21,28,29],
      'unique_8K_banks_examined':4,'total_raw_bank_bytes_examined':32768,
      'bank0A_discovery':scan_raw(raw10,20),'bank0E_discovery':scan_raw(raw14,28),
      'candidate_root_code':{
        '0A_instruction_starts':len(codes), '0A_code_operand_bytes':len(code_bytes),
        '0A_new_conditional_code_in_physical_bank_20':sum(0x8000<=x<0xA000 for x in code_bytes),
        '0A_0501_previously_admitted_bank20_instruction_starts':len(legacy_starts),
        '0A_0501_previously_admitted_bank20_bytes':len(legacy_bytes),
        '0A_previously_admitted_legacy_indirect_exit':'raw 0A CPU $8520 -> ($0002); live target context is not retested',
        '0A_code_only_physical_bank_21':sum(0xA000<=x<0xC000 for x in code_bytes),
        '0A_inline_table_bytes':len(ptrs),'0A_descriptor_bytes':len(descriptor),
        '0A_room_pointer_bytes':len(room_ptrs),
        '0E_conditional_stream_source_bytes':len(source),
        'new_conditional_distinct_labeled_bytes':len(code_bytes)+len(ptrs)+len(descriptor)+len(room_ptrs)+len(source),
        'total_distinct_labeled_including_120_previously_credited_bank20_bytes':len(code_bytes)+len(ptrs)+len(descriptor)+len(room_ptrs)+len(source)+len(legacy_bytes),
        'nonoverlap_assertions_passed':True, 'mapper':'raw 0A PRG20/21; raw 0E PRG28/29',
        'liveness':'UNPROVED, CODE AND DATA CLAIMS ARE CONDITIONAL'
      },
      'nested_tables':{pc:{'words':item['encoded_words'],'sha256':item['sha256']}
                       for pc,item in table.items()},
      'local_graph_direct_writer_candidates':producer,
      'whole_256KiB_physical_PRG_direct_writer_encoding_census':census(prg),
      'reset_ram_clear':verify_reset_ram_clear(fixed),
      'fixed_E551_effect':{'bytes':fixed_inc.hex(' ').upper(),
         'incoming_18_0B_to_0C':'yes if entered at $0B; $19 reset to 0',
         'live_call_path_to_0C':'not demonstrated'},
      'raw_direct_immediate_0C_to_18_encoding_count':0,
      'mapped_bank0E_loader_case_regression':room['complete_loader_cases'],
      'not_proved':['RESET-to-$18=$0C first-level NMI trace','full $19=$13 liveness',
        'external NMI producer order','global $07A0/$07A6 indexed/indirect alias domain',
        'B6A4 gate and actual room-loader occurrence','all 0E source material interpreted',
        'native CPU/PPU/APU frame parity'],
      'strict_new_unique_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24,
      'recovery_last_completed_checkpoint':'0507','fixed_cpu_frontier':'FB96'
    }

if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: audit_0508_bulk_0a0e.py JP_ROM.nes [report.json]')
    report=audit(sys.argv[1])
    if len(sys.argv)==3:
        Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('BULK PASS: 32KiB raw 0A+0E source-index sweep; 256KiB writer encoding census')
    print('0A conditional graph: 935 starts / 2042 operand bytes; source 0E 175 bytes')
    print('Reset-clear tests', report['reset_ram_clear']['case_count'], 'cases')
    print('strict unique PRG added 0; VPP 24; no reset/frame liveness certificate')
