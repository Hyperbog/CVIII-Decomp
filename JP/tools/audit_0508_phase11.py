#!/usr/bin/env python3
"""0508 Phase 11: execute $6B sound metadata installation through natural RTS.

Exact JP-ROM fetched 6502 subset. Runs bank-$0A room state 1 through $E249,
raw bank-$0C metadata walker, six temporary raw-bank-$05 instrument reads,
proper $E19F/$8850 return and $B591-B596 transition. No frame liveness.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from audit_0508_phase10 import CPU as Parent, EXPECTED_SOUND, ROM_SHA

SOUND_ID=0x6B
META_PTR=0x94B5
INSTRUMENTS=((0,0xBB48),(1,0xBBEA),(2,0xBD42),
             (3,0xB90A),(4,0xBA14),(7,0xBAC9))

class CPU(Parent):
    def __init__(self,prg:bytes,seed:int):
        super().__init__(prg,seed)
        self.trace=[]
        self.metareads=[]
        self.instreads=[]
        self.origin=bytes(self.ram)
    def rd(self,addr:int)->int:
        if self.ram[0x23]==0x05 and 0x8000<=addr<0xC000:
            self.instreads.append((self.pc,addr))
        if self.ram[0x23]==0x0C and META_PTR<=addr<META_PTR+20:
            self.metareads.append((self.pc,addr))
        return super().rd(addr)
    def step(self):
        pc=self.pc;op=self.rd(pc);v=self.rd(pc+1)
        target=v|(self.rd(pc+2)<<8)
        nxt=pc+1
        if op==0x0A:                     # ASL A
            self.c=bool(self.a&0x80);self.a=(self.a<<1)&255;self.nz(self.a)
        elif op==0xB9:                   # LDA abs,Y
            self.a=self.rd((target+self.y)&0xFFFF);self.nz(self.a);nxt=pc+3
        elif op==0xDD:                   # CMP abs,X
            val=self.rd((target+self.x)&0xFFFF)
            self.c=self.a>=val;self.nz((self.a-val)&255);nxt=pc+3
        elif op==0xC6:                   # DEC zp
            value=(self.rd(v)-1)&255;self.wr(v,value);self.nz(value);nxt=pc+2
        elif op==0x30:                   # BMI
            nxt=(pc+2+((v if v<128 else v-256) if self.n else 0))&0xFFFF
        elif op==0xA8:                   # TAY
            self.y=self.a;self.nz(self.y)
        elif op==0x98:                   # TYA
            self.a=self.y;self.nz(self.a)
        elif op==0x8A:                   # TXA
            self.a=self.x;self.nz(self.a)
        elif op==0xA1:                   # LDA (zp,X)
            zz=(v+self.x)&255;addr=self.rd(zz)|(self.rd((zz+1)&255)<<8)
            self.a=self.rd(addr);self.nz(self.a);nxt=pc+2
        else:
            return super().step()
        self.pc=nxt;self.steps+=1
    def run_to_parent(self):
        while self.pc!=0x9000:
            if self.steps>=5000:raise AssertionError((hex(self.pc),self.steps))
            self.trace.append((self.pc,self.ram[0x23],self.sp))
            self.step()

def audit(path:str)->dict:
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    rd=lambda bank,a,n:prg[bank*0x4000+a-0x8000:bank*0x4000+a-0x8000+n]
    assert int.from_bytes(rd(12,0x8F5E+2*SOUND_ID,2),'little')==META_PTR
    header=rd(12,META_PTR,20)
    assert header[:3]==bytes([5,5,0])
    expected=((header[2+3*i],header[3+3*i]|header[4+3*i]<<8) for i in range(6))
    assert tuple(expected)==INSTRUMENTS
    assert rd(5,0xBB48,1)==bytes([0xD9])
    all_counts=[];run_count=256
    for seed in range(run_count):
        c=CPU(prg,seed)
        c.run_to_parent()
        assert c.sp==0xFD,(seed,c.sp)
        assert c.ram[0x23]==0x0A and c.ram[0x25]==0x0A
        assert c.ram[0x26]==0 and c.ram[0x19]==2 and c.ram[0x68]==0
        assert c.ram[0x18]==0x0D and c.ram[0xEF]==0x6B
        assert c.ram[0xEB]==5 and c.ram[0xEA]==0xFF
        assert c.ram[0xE8]==(META_PTR&255) and c.ram[0xE9]==(META_PTR>>8)
        assert c.x==c.entry_x and c.y==c.entry_y
        assert [(a,v) for _,a,v in c.sound_writes]==EXPECTED_SOUND
        assert all(c.ram[0x0109+i]==(0x6B if i in (0,1,2,3,4,7) else 0)
                   for i in range(9))
        for slot,ptr in INSTRUMENTS:
            assert c.ram[0x06D3+slot]==5
            assert c.ram[0x012D+slot]==(ptr&255)
            assert c.ram[0x0136+slot]==(ptr>>8)
            assert c.ram[0x011B+slot]==0
        assert c.ram[0x7A0]==c.origin[0x7A0] and c.ram[0x7A6]==c.origin[0x7A6]
        assert c.ram[0x10]==c.origin[0x10]
        assert c.banks==[(0xE2D2,12)]+[(0xE2D2,b) for _ in INSTRUMENTS for b in (5,12)]+[(0xE2D2,10)],c.banks
        assert not any(b not in (5,10,12) for _,b,_ in c.trace)
        # ROM reads through helper must use the six stream first bytes, not
        # an invented per-stream bank or an extra parse of stream records.
        assert [a for _,a in c.metareads]==list(range(META_PTR,META_PTR+20))
        assert len(c.instreads)==6,c.instreads
        assert [a for _,a in c.instreads]==[p for _,p in INSTRUMENTS],c.instreads
        assert sum(1 for pc,bank,_ in c.trace if pc==0xE19F)==6
        assert sum(1 for pc,bank,_ in c.trace if pc==0x8907)==1
        assert sum(1 for pc,bank,_ in c.trace if pc==0xB594)==1
        all_counts.append(c.steps)
    assert len(set(all_counts))==1,set(all_counts)
    result={
      'checkpoint':'0508 phase11 provisional', 'jp_rom_sha256':ROM_SHA,
      'status':'conditional state-one sound command closure through natural RTS',
      'seed_cases':run_count,'instruction_steps_per_case':all_counts[0],
      'metadata_ptr':f'{META_PTR:04X}', 'sound_id':f'{SOUND_ID:02X}',
      'metadata_bytes':len(header),
      'metadata_sha256':hashlib.sha256(header).hexdigest(),
      'metadata_consumed_bytes_per_case':20,
      'instrument_source_bank':'05',
      'instrument_roots':[{'slot':slot,'pointer':f'{p:04X}'} for slot,p in INSTRUMENTS],
      'temporary_bank_reads_per_case':6,
      'bank_writes_per_case':14,
      'sound_reset_apu_vrc6_writes_per_case':len(EXPECTED_SOUND),
      'room_state_19_exit':'02','room_secondary_68_exit':'00',
      'mapper_bank_exit':'0A', 'helper_bank25_exit':'0A',
      'limits':['Conditional B58C entry; does not prove live prior NMI state',
         'No sound parser update per game frame or actual APU playback parity',
         'No IRQ/cycle simulation or downstream state-two handler execution'],
      'strict_new_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24
    }
    return result

if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_0508_phase11.py JP_ROM.nes [report.json]')
    r=audit(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('0508 Phase11 PASS',r['seed_cases'],'cases,',r['instruction_steps_per_case'],'instructions/case')