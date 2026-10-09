#!/usr/bin/env python3
"""0508 Phase 6: ROM-locked IRQ preservation of room-loader RAM and VRC6 PRG bank.

Static proof over the already-admitted 04F2 IRQ state domain (38 unique bank-01
roots plus high-bit bypass), not a trace proving that room loading runs. Reuses
original 04F2 IRQ scope and exact 6502 decoder; disallows unclassified writes.
"""
from __future__ import annotations
from collections import deque
from pathlib import Path
import hashlib, json, sys
try:
    from audit_nmi_fixed_scheduler_banked import OPS,BR,TERM
except ImportError:
    from audit_0508_expanded import OPS,BR,TERM

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
REGION_SHA='fb0f709699ad64b6cb49fa4eaeb2de8e1a260e23745341fc2f48b38fedd8ded3'
IRQ_ROOTS=(0x9F99,0x9FA1,0x9FD5,0x9FE3,0xA01C,0xA078,0xA0A8,0xA0CF,
 0xA102,0xA10D,0xA120,0xA14B,0xA16F,0xA18B,0xA1B1,0xA1D5,
 0xA1FA,0xA235,0xA243,0xA249,0xA293,0xA2DD,0xA2E2,0xA2EA,
 0xA310,0xA316,0xA323,0xA340,0xA357,0xA36B,0xA3A8,0xA3ED,
 0xA405,0xA420,0xA497,0xA4B2,0xA4DF,0xA4EC)
FIXED_ROOTS=(0xE001,0xE005,0xE2FA,0xE30B,0xE316,0xE32B,
             0xE331,0xE33C,0xE347,0xE351)
ALLOWED_OUT={0x9F5B,*FIXED_ROOTS,0xE118,0xE11D}
WATCH=(0x08,0x09,0x10,0x18,0x19,0x23,0x54,0x68,0x07A0,0x07A6)
WR={'STA','STX','STY','INC','DEC','ASL','LSR','ROL','ROR'}

def analyze(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    p=rom[16:16+262144]
    def rd(pc,n=1):
        if 0x8000<=pc<0xC000:
            off=0x4000+(pc-0x8000)  # raw PRG bank $01, PRG02/03
            assert pc+n<=0xC000
        else:
            assert 0xE000<=pc and pc+n<=0x10000
            off=31*0x2000+pc-0xE000
        return p[off:off+n]
    assert hashlib.sha256(rd(0x9F99,1422)).hexdigest()==REGION_SHA
    assert rd(0xE0F5,16)==bytes.fromhex('48 8a 48 98 48 a5 00 48 a5 01 48 a9 01 20 d2 e2')
    assert rd(0xE100,5)==bytes.fromhex('a9 01 20 d2 e2')
    assert rd(0xE120,17)==bytes.fromhex('a5 23 20 d0 e2 68 85 01 68 85 00 68 a8 68 aa 68 40')
    assert rd(0xE2D0,6)==bytes.fromhex('85 23 8d 00 80 60')
    assert rd(0xE2D2,4)==bytes.fromhex('8d 00 80 60')
    assert rd(0xFB96,15)==bytes.fromhex('a9 0e 20 d0 e2 b1 08 48 a9 0a 20 d0 e2 68 60')
    assert rd(0x9F5B,3)==bytes.fromhex('ce 81 07')
    assert rd(0xA323,12)==bytes.fromhex('a2 02 bd 82 07 9d 89 07 ca 10 f7 a8')
    assert rd(0xA4A0,11)==bytes.fromhex('a2 07 bd 82 07 9d 89 07 ca 10 f7')
    assert rd(0xA302,8)==bytes.fromhex('a5 1b 29 03 f0 eb d0 e6')
    ptrs=[int.from_bytes(rd(0x9F01+2*i,2),'little') for i in range(45)]
    assert 0x9F5B not in ptrs and set(ptrs)-{0xE118}==set(IRQ_ROOTS)
    assert rd(0x9F5B,1)==b'\xce' # pointer-data stops before executable helper

    def decode(pc):
        op=rd(pc)[0]
        assert op in OPS,(hex(pc),hex(op))
        mn,mode,n=OPS[op]
        raw=rd(pc,n)
        arg=raw[1] if n==2 else (raw[1]|raw[2]<<8 if n==3 else None)
        if mode=='rel':arg=(pc+2+(arg if arg<128 else arg-256))&65535
        return mn,mode,n,arg

    def walk(roots,window):
        seen={}; q=deque(roots); exits=set();writes=[]
        while q:
            pc=q.popleft()
            if pc in seen:continue
            if not window(pc):
                exits.add(pc);continue
            mn,mode,n,arg=decode(pc)
            seen[pc]=(mn,mode,n,arg)
            if mn in WR and mode!='acc':writes.append((pc,mn,mode,arg))
            def edge(pc2):q.append(pc2)
            if pc==0x9F89:
                # Immediately prior LDY #01 forces Z=0: BNE $9F7B is unconditional.
                assert mn=='BNE' and arg==0x9F7B
                edge(arg)
            elif pc==0xA308:
                # A304 AND #03 sets Z, A306 BEQ and A308 BNE are complementary.
                assert mn=='BNE' and arg==0xA2F0
                edge(arg)
            elif mn in BR:q.extend((arg,pc+n))
            elif mn=='JSR':q.extend((arg,pc+n))
            elif mn=='JMP':
                assert mode=='abs',hex(pc)
                edge(arg)
            elif mn not in TERM:edge(pc+n)
            assert len(seen)<1000
        return seen,exits,writes

    handler,exits,writes=walk(IRQ_ROOTS,lambda a:0x9F99<=a<=0xA526)
    assert len(handler)==558, len(handler)
    assert exits==ALLOWED_OUT,(sorted(exits-ALLOWED_OUT),sorted(ALLOWED_OUT-exits))
    assert not any(pc in handler for pc in range(0xA30A,0xA310))
    assert not any(mo in ('zpx','zpy','indx','indy') for _,_,mo,_ in writes)
    dynamic=[(pc,mn,mo,op) for pc,mn,mo,op in writes if mo in ('absx','absy')]
    assert dynamic==[(0xA328,'STA','absx',0x0789),
                     (0xA4A5,'STA','absx',0x0789)],dynamic
    xdomains={0xA328:set(range(3)),0xA4A5:set(range(8))}
    # Fixed / local helper side effects must also be closed, not just the IRQ body.
    helper,h_ex,h_w=walk([0x9F5B],lambda a:0x9F5B<=a<=0x9F8A)
    assert not h_ex,h_ex
    assert 0x9F87 in helper and 0x9F89 in helper
    assert 0x9F8B not in helper  # pointer words and stream bytes, not code
    fixed,f_ex,f_w=walk(FIXED_ROOTS,lambda a:0xE001<=a<=0xE00A or 0xE2FA<=a<=0xE35B)
    assert not f_ex,f_ex
    assert not any(mo in ('zpx','zpy','indx','indy','absx','absy') for _,_,mo,_ in h_w+f_w)
    full=writes+h_w+f_w
    touched=set()
    for pc,mn,mode,arg in full:
        if mode in ('zp','abs'):
            touched.add(arg)
        elif mode in ('absx','absy'):
            touched.update((arg+x)&65535 for x in xdomains[pc])
        else:raise AssertionError((hex(pc),mn,mode,arg))
    assert touched.isdisjoint(WATCH),sorted(touched.intersection(WATCH))
    # All handler writes to the $0789 table are bounded before $07A0.
    assert all((0x0789+x)<0x07A0 for xs in xdomains.values() for x in xs)
    assert all(a!=0x8000 for a in touched) # only IRQ prologue / exit map the PRG window
    # IRQ frame writes $00/$01 only through saved scratch / dispatch; exit restores.
    assert rd(0xE105,16)==bytes.fromhex('a5 6a 0a b0 0e a8 b9 01 9f 85 00 b9 02 9f 85 01')
    assert rd(0xE115,3)==bytes.fromhex('6c 00 00')
    assert rd(0xE11D,3)==bytes.fromhex('8d 02 f0')
    # Direct program-bank writes in IRQ frame are only the two documented sites.
    # E102 calls E2D2, which writes $8000 *without* changing RAM $23.
    # E120 reloads $23 and calls E2D0, which restores $23 and $8000.
    unprotected=[a for a in WATCH if a in touched]
    assert not unprotected
    return {'status':'VERIFIED_STATIC_IRQ_GRAPH_CONDITIONAL_NO_NMI_REENTRY',
      'jp_rom_sha256':ROM_SHA,'mapped_irq_bank':'raw $01 (physical PRG02/03)',
      'irq_states':45,'distinct_irq_roots':len(IRQ_ROOTS),
      'irq_instruction_starts':len(handler),'irq_handler_write_sites':len(writes),
      'local_helper_starts':len(helper),'fixed_helper_starts':len(fixed),
      'external_targets': [f'{a:04X}' for a in sorted(exits)],
      'indexed_write_sites': [{'cpu':f'{pc:04X}','base':f'{base:04X}',
          'x_min':min(xdomains[pc]),'x_max':max(xdomains[pc])}
          for pc,_,_,base in dynamic],
      'watch_addresses_preserved':[f'{v:04X}' for v in WATCH],
      'irq_track_byte_23':'unchanged; E2D2 temporarily maps 01, E2D0 restores tracked bank',
      'irq_prologue_scratch_00_01':'pushed before dispatch, popped before RTI',
      'limitations':'Committed 04F2 IRQ state domain only; no nested NMI, CPU cycles, full emulator, arbitrary RAM alias, or room path liveness',
      'strict_new_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24}

if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: audit_0508_phase6.py JP_ROM.nes [report.json]')
    report=analyze(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('0508 Phase6 IRQ graph PASS:',report['irq_instruction_starts'],'handler starts;',
          report['irq_handler_write_sites'],'write sites')
    print('watched room-loader RAM addresses untouched; PRG IRQ save/restore contract PASS')
    print('PRG strict coverage remains',report['strict_cumulative_prg_bytes'])
