#!/usr/bin/env python3
"""JP0741: compare COMPLETE JP0740 original/native observed CPU bus traces.

Never assume same-numbered frames mean CPU alignment. Requires exactly
one matching 32-event mapped-instruction-PC, bus data and relative-cycle
trajectory. Only identifies the next *observed* event difference, not
necessarily the earliest incorrect CPU instruction (unwatched state).
Original cartridge, input recordings and traces remain PRIVATE.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from jp0740_trace_verify import read_trace

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
WATCH={0x62,0x53,0x54,0x55,0x63,0x6b,0x41c,0x438,
       0x4c4,0x4f2,0x509,0x520,0x565,0x5c1}
PRIMARY={0x62,0x41c,0x520,0x565}
MIN_ANCHOR=32
MISSING_PRG=0xfffff

@dataclass(frozen=True)
class Event:
    ordinal:int
    frame:int
    cycle:int
    kind:str
    addr:int
    old:int|None
    value:int
    bus:int
    pc:int
    phys:int
    opcode:int|None
    def identity(self):
        return (self.kind,self.addr,self.old,self.value,
                self.bus,self.pc,self.phys)
    def report(self):
        return {'ordinal':self.ordinal,'frame':self.frame,
                'cycle':self.cycle,'kind':self.kind,
                'address':f'{self.addr:04X}',
                'old':None if self.old is None else f'{self.old:02X}',
                'new':f'{self.value:02X}','cpu_pc':f'{self.pc:04X}',
                'physical_prg':None if self.phys==MISSING_PRG else f'{self.phys:05X}',
                'opcode':None if self.opcode is None else f'{self.opcode:02X}'}

def authentic_image(path):
    b=path.read_bytes()
    if (len(b)!=393232 or b[:4]!=b'NES\x1a' or
        ((b[6]>>4)|(b[7]&0xf0))!=24 or
        hashlib.sha256(b).hexdigest()!=ROM_SHA):
        raise ValueError('original Japanese Mapper24 ROM identity mismatch')
    return b

def extract(path,kind,image):
    # Existing JP0740 parser checks COMPLETE footer, source replay anchors,
    # ordered event numbers/cycles and physical-PC low 12-bit identity.
    read_trace(path,kind,image)
    seq=[]
    for row in path.read_text(encoding='ascii').splitlines()[1:-1]:
        f=row.split('\t')
        if f[0] not in ('W','R'):
            continue
        if f[0]=='W':
            _,n,frame,cyc,addr,old,value,bus,pc,phys=f
            old=int(old,16);value=int(value,16)
        else:
            _,n,frame,cyc,addr,value,pc,phys=f
            old=None;value=int(value,16);bus=addr
        frame=int(frame);addr=int(addr,16);bus=int(bus,16)
        pc=int(pc,16);phys=int(phys,16)
        if not 9370<=frame<=9600:
            raise ValueError('outside JP0740 bounded recorder window')
        if (f[0]=='W' and addr!=0x4016 and addr not in WATCH or
            f[0]=='R' and addr not in (0x4016,0x4017)):
            raise ValueError('unwatched address in bounded bus record')
        if phys==MISSING_PRG or not (0x8000<=pc<=0xffff and
                                    0<=phys<262144):
            opcode=None
        else:
            if (pc&0xfff)!=(phys&0xfff):
                raise ValueError('unmapped PRG instruction address')
            opcode=image[16+phys]
        seq.append(Event(int(n),frame,int(cyc),f[0],addr,old,
                         value,bus,pc,phys,opcode))
    return seq

def window(seq,index,length):
    sub=seq[index:index+length]
    if len(sub)!=length or any(e.opcode is None for e in sub):
        return None
    initial=sub[0].cycle
    return tuple((e.identity(),e.cycle-initial) for e in sub)

def align(original,native,min_anchor=MIN_ANCHOR):
    if min_anchor<2:raise ValueError('invalid minimum anchor size')
    base={'schema':'JP0741-observed-first-bus-divergence/v1',
          'first_incorrect_cpu_write_certified':False,
          'original_events':len(original),'native_events':len(native),
          'original_primary_writes':sum(e.kind=='W' and e.addr in PRIMARY for e in original),
          'native_primary_writes':sum(e.kind=='W' and e.addr in PRIMARY for e in native),
          'minimum_matching_events':min_anchor}
    if min(len(original),len(native))<min_anchor:
        return {**base,'status':'INSUFFICIENT_EVENTS'}
    keys={}
    for i in range(len(original)-min_anchor+1):
        k=window(original,i,min_anchor)
        if k is not None: keys.setdefault(k,[]).append(i)
    trajectories={}
    for j in range(len(native)-min_anchor+1):
        k=window(native,j,min_anchor)
        if k is None:continue
        for i in keys.get(k,()):
            if abs(original[i].frame-native[j].frame)>32:continue
            # Consecutive overlapping windows in the same trajectory are
            # expected. Independent index/cycle offsets are ambiguous.
            ep=(i-j,native[j].cycle-original[i].cycle)
            trajectories.setdefault(ep,[]).append((i,j))
            if len(trajectories)>1:
                return {**base,'status':'AMBIGUOUS_CPU_BUS_ANCHOR',
                        'independent_trajectories_at_least':2}
    if not trajectories:
        return {**base,'status':'NO_MAPPED_CYCLE_BUS_ANCHOR',
                'note':'Approximate frame numbers are not accepted as a substitute'}
    i,j=min(next(iter(trajectories.values())))
    delta=native[j].cycle-original[i].cycle
    matched=0
    while i+matched<len(original) and j+matched<len(native):
        a=original[i+matched];b=native[j+matched]
        if a.identity()!=b.identity() or b.cycle-a.cycle!=delta:break
        matched+=1
    result={**base,'status':'ALIGNED_WATCHED_EVENT_PREFIX',
            'original_anchor':original[i].report(),
            'native_anchor':native[j].report(),
            'native_minus_original_cycles':delta,
            'matched_observed_events':matched,
            'proof_limit':'Only first observed watched bus-event difference; upstream unwatched execution may be causal'}
    if i+matched<len(original) or j+matched<len(native):
        a=original[i+matched] if i+matched<len(original) else None
        b=native[j+matched] if j+matched<len(native) else None
        result['first_observed_difference']={
            'original':None if a is None else a.report(),
            'native':None if b is None else b.report(),
            'involves_primary_target':any(x and x.kind=='W' and
                                          x.addr in PRIMARY for x in (a,b))}
    else:
        result['status']='MATCHED_ALL_RECORDED_EVENTS_AFTER_ANCHOR'
    return result

def smoke():
    # Entirely invented mapped-instruction and bus events.
    def sample(i,side,changed=False):
        addr=(0x62,0x565,0x520,0x41c)[i%4]
        return Event(i+1,9400+i//6,1000+7*i+401*side,'W',
                     addr,i%4,i%251+int(changed),addr,
                     0x8000+i,0x38000+i,0xa9)
    a=[sample(i,0) for i in range(46)]
    b=[sample(i,1,i==35) for i in range(46)]
    result=align(a,b)
    assert result['status']=='ALIGNED_WATCHED_EVENT_PREFIX'
    assert result['matched_observed_events']==35
    assert result['first_observed_difference']['original']['ordinal']==36
    assert result['first_incorrect_cpu_write_certified'] is False
    assert align(a,[])['status']=='INSUFFICIENT_EVENTS'
    drift=list(b)
    drift[10]=Event(**{**asdict(drift[10]),'cycle':drift[10].cycle+1})
    assert align(a,drift)['status']=='NO_MAPPED_CYCLE_BUS_ANCHOR'
    doubled=b+[Event(**{**asdict(x),'ordinal':i+47})
               for i,x in enumerate(b[:33])]
    assert align(a,doubled)['status']=='AMBIGUOUS_CPU_BUS_ANCHOR'
    print('PASS JP0741 synthetic unique 32-event mapped/cycle alignment, first observed mismatch, ambiguity and drift; NOT original game parity')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--original-trace',type=Path)
    p.add_argument('--native-trace',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not(a.rom and a.original_trace and a.native_trace):
        p.error('need --rom --original-trace --native-trace')
    image=authentic_image(a.rom)
    result=align(extract(a.original_trace,'mesen',image),
                 extract(a.native_trace,'native',image))
    result.update(original_rom_sha256=ROM_SHA,
                  original_trace_sha256=hashlib.sha256(a.original_trace.read_bytes()).hexdigest(),
                  native_trace_sha256=hashlib.sha256(a.native_trace.read_bytes()).hexdigest(),
                  last_owner_test='JP0722',
                  vpp=31,strict_prg_bytes=49504,new_certified_bytes=0)
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(output,encoding='utf8')
    else:print(output,end='')

if __name__=='__main__':main()
