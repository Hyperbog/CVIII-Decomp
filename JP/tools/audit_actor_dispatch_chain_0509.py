#!/usr/bin/env python3
"""Step the original-JP $8501 two-level object-event dispatcher and three
raw-$0A actor-creation handlers through authentic source instructions.

This does NOT establish reset/NMI gameplay reachability: $07C2,X, $07C8,X,
$53, $07E0,X and slot occupancies are explicit synthetic initial inputs.
All fetched instructions and indexed source data are read from the source ROM.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from audit_actor_cpu_abi_0509 import authenticated_prg, BoundedCpu, ROM_SHA

ROM_BANK=0x0A
END=0xD000
# Selected *verified* rows of the $8523 object-event base-word table:
# row 8 -> $90C1, 9 -> $90BD, 10 -> $912F; do not treat the row
# count or unsampled selectors as a proven live domain.
ROUTES={
  (8,0):(0x90DF,2,0x68),
  (9,0):(0x90C5,1,0x13),
  (9,2):(0x90DF,2,0x68),
  (10,0):(0x9133,3,0x12),
}

class ChainCpu(BoundedCpu):
    def __init__(self, prg, ram, incoming_x, parent=False):
        super().__init__(prg,0x84EA if parent else 0x8501,ram,incoming_x)
        self.parent=parent
        self.y=0x77
        self.p=0xA5
        self.path=[]
        self.jumps=[]
        self.stores=[]
        self.initial_x=incoming_x

    def read(self,addr):
        addr &= 0xffff
        if addr < 0x2000: return self.ram[addr & 0x7ff]
        if 0x8000 <= addr < 0xC000:
            return self.prg[ROM_BANK*0x4000 + addr-0x8000]
        if 0xE000 <= addr <= 0xFFFF:
            return self.prg[31*0x2000 + addr-0xE000]
        raise ValueError(f'Unmapped original source read ${addr:04X}')

    def write(self,addr,value):
        if addr >= 0x800: raise ValueError(f'Unexpected original source write ${addr:04X}')
        self.ram[addr]=value&255
        self.stores.append((addr,value&255))

    def absaddr(self): return self.fetch() | (self.fetch()<<8)

    def execute(self):
        while self.pc != (0x84F8 if self.parent else END):
            at=self.pc
            if not (0x84EA<=at<=0x8500 or 0x8501<=at<=0x8522 or 0x8CDD<=at<=0x8CE9
                    or 0x90C5<=at<=0x9128 or 0x9133<=at<=0x917B
                    or 0xFF06<=at<=0xFF14):
                raise ValueError(f'Unknown source instruction PC ${at:04X}; parent={self.parent}; last path={self.path[-15:]} ; sp={self.sp:02X}')
            self.path.append(at)
            self.steps+=1
            if self.steps>350: raise ValueError('Actor event exceeds bound')
            op=self.fetch()
            if op in (0xA9,0xA2,0xA0):
                value=self.fetch()
                if op==0xA9:self.a=value
                elif op==0xA2:self.x=value
                else:self.y=value
                self.nz(value)
            elif op in (0xA5,0xA6,0xA4):
                value=self.read(self.fetch())
                if op==0xA5:self.a=value
                elif op==0xA6:self.x=value
                else:self.y=value
                self.nz(value)
            elif op==0xBD:  # LDA absolute,X
                self.a=self.read((self.absaddr()+self.x)&0xffff);self.nz(self.a)
            elif op==0xB9:  # LDA absolute,Y
                self.a=self.read((self.absaddr()+self.y)&0xffff);self.nz(self.a)
            elif op==0xB1:  # LDA (zero page),Y with 6502 ZP high wrap
                z=self.fetch()
                base=self.read(z)|(self.read((z+1)&255)<<8)
                self.a=self.read((base+self.y)&0xffff);self.nz(self.a)
            elif op in (0x85,0x84,0x86):
                z=self.fetch();self.write(z,self.a if op==0x85 else self.y if op==0x84 else self.x)
            elif op==0x9D:
                self.write((self.absaddr()+self.x)&0xffff,self.a)
            elif op in (0x29,0x09):
                rhs=self.fetch()
                self.a=(self.a&rhs) if op==0x29 else (self.a|rhs)
                self.nz(self.a)
            elif op==0x0A:
                self.p=(self.p&~1)|int(bool(self.a&0x80))
                self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0xA8:
                self.y=self.a;self.nz(self.y)
            elif op==0x98:
                self.a=self.y;self.nz(self.a)
            elif op==0xC8:
                self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0xE8:
                self.x=(self.x+1)&255;self.nz(self.x)
            elif op==0xE0:
                rhs=self.fetch();self.p=(self.p&~1)|int(self.x>=rhs)
                self.nz((self.x-rhs)&255)
            elif op==0xC6:
                z=self.fetch();value=(self.read(z)-1)&255
                self.write(z,value);self.nz(value)
            elif op==0xFE:
                address=(self.absaddr()+self.x)&65535
                value=(self.read(address)+1)&255
                self.write(address,value);self.nz(value)
            elif op in (0xD0,0xF0,0x90,0x10):
                offset=self.fetch()
                if op==0xD0: take=not bool(self.p&2)
                elif op==0xF0:take=bool(self.p&2)
                elif op==0x90:take=not bool(self.p&1)
                else:take=not bool(self.p&0x80)
                if take:self.pc=(self.pc+(offset if offset<128 else offset-256))&0xffff
            elif op==0x20:
                target=self.absaddr()
                self.push((self.pc-1)>>8);self.push((self.pc-1)&255)
                self.pc=target
            elif op in (0x4C,0x6C):
                if op==0x4C:target=self.absaddr()
                else:
                    ptr=self.absaddr()
                    target=self.read(ptr)|(self.read((ptr&0xff00)|((ptr+1)&255))<<8)
                self.jumps.append((at,target))
                self.pc=target
            elif op==0x60:
                self.pc=((self.pop()|(self.pop()<<8))+1)&65535
            else:
                raise ValueError(f'Unimplemented opcode ${op:02X} at ${at:04X}')
        if self.sp != (0xFB if self.parent else 0xFD):
            raise ValueError(f'Unbalanced event stack SP=${self.sp:02X}')

def simulate(prg, row, selector, mask, guard, origin_x, initial_10, parent=False):
    ram=bytearray([0xA5]*0x800)
    # active scan slots 1..12 use RAM at $054E+X
    for i in range(12): ram[0x054F+i]=0x81 if mask&(1<<i) else 0
    ram[0x07C2+origin_x]=row
    if parent:
        for i in range(origin_x):ram[0x07C2+i]=0
    selector_byte=selector | (0xF0 if (mask ^ guard)&1 else 0)
    ram[0x07C8+origin_x]=selector_byte
    ram[0x69]=0xA5 if parent else origin_x
    ram[0x53]=1 if guard==1 else 0
    ram[0x07E0+origin_x]=1 if guard==2 else 0
    ram[0x10]=initial_10
    baseline=bytes(ram)
    cpu=ChainCpu(prg,ram,origin_x,parent=parent)
    cpu.execute()
    route, requested, actor_type=ROUTES[(row,selector)]
    if cpu.jumps[0] != (0x8520,route):
        raise ValueError(f'Original indirect dispatcher target wrong: {cpu.jumps[:2]}')
    # One guarded precheck; if passed, allocate up to 1/2/3 slots.
    free=[i+1 for i in range(12) if not(mask&(1<<i))]
    slots=free[:requested] if guard==0 else []
    mutated=set((0,1,2,3))  # ($8501 loads the two nested pointer words)
    if parent:mutated.add(0x69)
    if slots:
        # source routines all use selected actor X and final index increments
        for n,slot in enumerate(slots):
            if ram[0x054E+slot] != actor_type:
                raise ValueError(f'Incorrect actor kind at row={row} slot={slot}')
            if ram[0x05EF+slot] != (0x60 if actor_type==0x68 else 0):
                raise ValueError('Incorrect original actor script field')
            mutated.add(0x054E+slot)
            mutated.add(0x05EF+slot)
            fixture_xy={0x13:[(0x80,0x40)],
                        0x68:[(0xC0,0x40),(0x40,0x50)],
                        0x12:[(0xD0,0x50),(0xB0,0x50),(0x30,0x50)]}
            if (ram[0x0438+slot],ram[0x041C+slot])!=fixture_xy[actor_type][n]:
                raise ValueError('Original encoded source position offsets mismatch')
            for base in (0x0438,0x041C,0x0470,0x04F2,0x0509,0x0520,0x0537)+(() if actor_type==0x12 else (0x05C1,)):
                mutated.add(base+slot)
                if base in (0x04F2,0x0509,0x0520,0x0537,0x05C1) and ram[base+slot]!=0:
                    raise ValueError(f'Actor initialize field not cleared ${base+slot:04X}')
            if actor_type==0x12:
                mutated.add(0x0645+slot)
                if ram[0x0645+slot] != (0x82-n):
                    raise ValueError('Three-spawn actor subindex flag mismatch')
            if actor_type==0x68:
                mutated.add(0x05C1+slot)
                if ram[0x05C1+slot]!=0:
                    raise ValueError('Two-spawn actor subscript field not reset')
                if ram[0x0470+slot] != 0xC8:
                    raise ValueError('Two-spawn actor attribute mismatch')
            elif actor_type==0x12:
                if ram[0x0470+slot] != 0x88:
                    raise ValueError('Three-spawn actor attribute mismatch')
            else:
                if ram[0x0470+slot]!=0xC8:
                    raise ValueError('Single-spawn actor attribute mismatch')
    # Only complete success reaches original indexed $07C8 increment; all
    # successful $90C5 single-slot calls use $10=0, $90DF uses $10=2,1,
    # $9133 uses $10=2,1,0. On partial failures, prior actors remain initialized.
    completed=(guard==0 and len(free)>=requested)
    # Source $90C5 branch is special: on free, it sets $10=0. Other branches
    # set $10=2 and then update via decrement inside successful loop.
    if guard==0:
        if row==9 and selector==0 and slots:expected_10=0
        elif slots: expected_10=(requested-len(slots)) if actor_type==0x68 else (2-len(slots))&255
        else: expected_10=initial_10
    else: expected_10=initial_10
    if ram[0x10] != expected_10:
        raise ValueError(f'Unexpected scratch $10: {ram[0x10]:02X} vs {expected_10:02X}')
    if ram[0x07C8+origin_x] != ((selector_byte+1)&255 if completed else selector_byte):
        raise ValueError('Original event-state increment mismatch')
    if completed:mutated.add(0x07C8+origin_x)
    # Byte-accurate RAM store ordering is checked independently of the mutable
    # field assertions above. This catches accidental extra/omitted stores and
    # malformed partial-commit event progression, even when values coincide.
    expected_stores=([(0x69,origin_x)] if parent else []) + [
        (0x00, {8:0xC1,9:0xBD,10:0x2F}[row]),
        (0x01, {8:0x90,9:0x90,10:0x91}[row]),
        (0x02, route&255), (0x03,route>>8)]
    if guard==0 and slots:
        if actor_type==0x13:expected_stores.append((0x10,0))
        else:expected_stores.append((0x10,2))
        for n,slot in enumerate(slots):
            fields=([(0x054E+slot,actor_type),
                     (0x05EF+slot,0x60 if actor_type==0x68 else 0)])
            if actor_type==0x12:fields.append((0x0645+slot,0x82-n))
            offset_xy={0x13:[(0x80,0x40)],0x68:[(0xC0,0x40),(0x40,0x50)],
                       0x12:[(0xD0,0x50),(0xB0,0x50),(0x30,0x50)]}[actor_type][n]
            fields.extend(((0x0438+slot,offset_xy[0]),(0x041C+slot,offset_xy[1])))
            if actor_type==0x12:fields.append((0x0470+slot,0x88))
            fields.extend((base+slot,0) for base in (0x04F2,0x0509,0x0520,0x0537))
            if actor_type!=0x12:fields.append((0x05C1+slot,0))
            if actor_type!=0x12:fields.append((0x0470+slot,0xC8))
            expected_stores.extend(fields)
            if actor_type!=0x13:expected_stores.append((0x10,(1-n)&255))
    if completed: expected_stores.append((0x07C8+origin_x,(selector_byte+1)&255))
    if cpu.stores!=expected_stores:
        for j,(a,b) in enumerate(zip(cpu.stores,expected_stores)):
            if a!=b:break
        raise ValueError(f'Original source ordered stores differ at {j}: '
                         f'observed={cpu.stores[j:j+2]}, expected={expected_stores[j:j+2]}')
    if guard==0 and slots:mutated.add(0x10)
    if ram[0x69]!=origin_x:raise ValueError('Object dispatch index $69 overwritten')
    # All old bytes except exact source stores and JSR stack frames survive.
    changed={j for j in range(0x800) if ram[j]!=baseline[j]}
    if not changed.issubset(mutated|{0x1f8,0x1f9,0x1fa,0x1fb,0x1fc,0x1fd}):
        raise ValueError(f'Unexpected RAM changes: {sorted(changed-mutated-set((0x1f8,0x1f9,0x1fa,0x1fb,0x1fc,0x1fd)))[:8]}')
    return cpu,slots,completed,changed

def audit(prg):
    raw=prg[ROM_BANK*0x4000:(ROM_BANK+1)*0x4000]
    def sha(start,end): return hashlib.sha256(raw[start-0x8000:end-0x8000]).hexdigest()
    hashes={
        'dispatcher_8501_8522':sha(0x8501,0x8523),
        'parent_84EA_8500':sha(0x84EA,0x8501),
        'pointer_rows_8533_8538':sha(0x8533,0x8539),
        'spawn_handlers_90BC_917B':sha(0x90BC,0x917C),
        'guard_8CDD_8CE9':sha(0x8CDD,0x8CEA),
    }
    # Pin original source; no pattern-only inferred dispatcher.
    expected={
        'dispatcher_8501_8522':'ad5600da3247b263c60371b9cca117cbcb2b77d37087b7de0318b6de525e26d3',
        'parent_84EA_8500':'cc4f1153896f3e321872a7a92c70b0b3b9ef868bca258fa6ba1eb28856d9f6f7',
        'pointer_rows_8533_8538':'09149bb0f11b4d7717c4742fea2a436904555c67f37b9191a77d2361d100b99e',
        'spawn_handlers_90BC_917B':'9c3f69c360eb93021f7b602b89d061dd9d0e2ec731643e8c25d8f08f86627038',
        'guard_8CDD_8CE9':'c1cd8387e6e6a0d5b7b460de3b869f77a2df3f3e15debfca42152acb85a65b06'
    }
    if hashes!=expected:raise ValueError(f'Original ROM instruction block changed: {hashes}')
    digest=hashlib.sha256(); total=0; pcs=set(); observed=Counter(); unique_slots=Counter();
    # Four genuine dispatch options, 4096 occupancy masks and 3 guards;
    # vary original object actor X=0,2,5 to cover indexed memory aliasing.
    for parent in (False,True):
        for (row,selector),(entry,n,kind) in ROUTES.items():
            for mask in range(4096):
                for guard in (0,1,2):
                    x=(0,2,5)[(mask+row+guard)%3]
                    cpu,slots,complete,_=simulate(prg,row,selector,mask,guard,x,0x7E,parent)
                    if parent:
                        if 0x84F3 not in cpu.path or cpu.pc!=0x84F8:
                            raise ValueError('Upstream 6-object scheduler call was not executed')
                        if cpu.x!=x:
                            raise ValueError('Source $84F6 did not restore original object X')
                    observed[f'{int(parent)}:{row:02X}:{selector:X}:{guard}:{len(slots)}:{int(complete)}']+=1
                    unique_slots[len(slots)]+=1
                    digest.update(bytes((int(parent),row,selector,mask&255,mask>>8,guard,x,
                                         len(slots),int(complete),cpu.x,cpu.y,cpu.a,
                                         cpu.p,cpu.sp))+cpu.steps.to_bytes(2,'little'))
                    pcs.update(cpu.path);total+=cpu.steps
    return {
        'schema':'JP-0509-raw0A-original-actor-indirect-dispatch-chain/v1',
        'rom_sha256':ROM_SHA,
        'source_sha256':hashes,
        'event_selector_high_nibbles_tested':['00','F0'],
        'routes':[{'row_07C2':f'{r:02X}','selector_07C8_low_nibble':s,
                   'entry_cpu':f'{v[0]:04X}','requested_actor_count':v[1],
                   'actor_type':f'{v[2]:02X}'} for (r,s),v in ROUTES.items()],
        'occupancy_masks_per_route':4096,
        'entry_modes':['direct $8501 dispatcher','six-object parent $84EA to $84F8'],
        'guard_states_per_mask':3,
        'origin_object_slot_values':[0,2,5],
        'total_execution_cases':4096*3*len(ROUTES)*2,
        'total_source_instructions':total,
        'distinct_instruction_pcs':len(pcs),
        'number_of_new_actors_histogram':dict(sorted(unique_slots.items())),
        'outcome_categories':len(observed),
        'outcome_digest_sha256':digest.hexdigest(),
        'scope':'authentic source instructions with synthetic dispatcher RAM; no real-play event liveness or mapper/IRQ proof',
        'new_strict_prg_bytes':0,'new_vpp_points':0,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_jp_rom',type=Path)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    result=audit(authenticated_prg(a.original_jp_rom))
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS 0509 original indirect actor dispatch:',result['total_execution_cases'],
          'cases,',result['total_source_instructions'],'instructions')

if __name__=='__main__':main()
