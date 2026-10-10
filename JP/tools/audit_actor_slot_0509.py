#!/usr/bin/env python3
"""ROM-locked source audit of the already certified native object field lifts.

Hashes/field addresses only. Strict source verification was credited to the
previous 0508 checkpoint; no new PRG bytes or VPP points are awarded here.
"""
from pathlib import Path
import hashlib,json,sys
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RANGES=((0xFF06,12,'c75f2332e11e13763245741d3f4ddb690f63dce3930c946cae3160090ac1488c'),
        (0xFF14,66,'9f4374fdf490e30015a28e44abdc20c87259b501064c1d8eb9f4fee353d40d1a'))
FIELDS4=(0x04F2,0x0509,0x0520,0x0537)
FIELDS14=(0x067B,0x068D,0x0454,0x0470,0x0565,0x04C4,0x04DB,
          0x05C1,0x05D8,0x05EF,0x0606,0x061D,0x0633,0x0645)

def audit(image:bytes):
    if len(image)!=393232 or hashlib.sha256(image).hexdigest()!=ROM_SHA:
        raise ValueError('Not the correct original JP mapper24 ROM')
    prg=image[16:16+262144]
    def block(pc,n):return prg[31*8192+(pc-0xE000):31*8192+(pc-0xE000)+n]
    for pc,n,digest in RANGES:
        if hashlib.sha256(block(pc,n)).hexdigest()!=digest:
            raise ValueError('Previous checkpoint hash mismatch')
    if block(0xFF06,14)!=bytes.fromhex('A2 01 BD 4E 05 F0 07 E8 E0 0D 90 F6 A9 01'):
        raise ValueError('Incorrect scanner or nonempty-branch bytes')
    if block(0xFF14,1)!=b'\x60' or block(0xFF23,1)!=b'\x60' or block(0xFF55,1)!=b'\x60':
        raise ValueError('Object-clear return ABI mismatch')
    if block(0xFF24,3)!=bytes.fromhex('20 15 FF'):
        raise ValueError('18-field helper does not call 4-field helper')
    def read_indexed_stores(pc,end):
        # Analyze only the already ROM-hash-proved routine's straight-line
        # LDA #00 / STA abs,X sequence; every instruction boundary is asserted.
        code=block(pc,end-pc)
        at=0;destinations=[];loads=0
        while at<len(code):
            op=code[at]
            if op==0xA9:
                assert code[at+1]==0;loads+=1;at+=2
            elif op==0x9D:
                destinations.append(code[at+1]|(code[at+2]<<8));at+=3
            elif op==0x20:
                assert pc+at==0xFF24 and code[at+1:at+3]==bytes.fromhex('15 FF')
                at+=3
            elif op==0x60:
                assert at==len(code)-1;at+=1
            else:raise ValueError('Undecoded opcode in original field store lift: '+hex(op))
        return destinations,loads
    d4,loads4=read_indexed_stores(0xFF15,0xFF24)
    d14,loads14=read_indexed_stores(0xFF24,0xFF56)
    assert tuple(d4)==FIELDS4 and tuple(d14)==FIELDS14
    assert loads4==1 and loads14==2
    return {'schema':'JP-0509-reconstructed-actor-helper-original-ROM-audit/v1',
      'source_rom_sha256':ROM_SHA,
      'source_prg31_ranges':[{'start_cpu':f'{p:04X}','bytes':n,'sha256':digest} for p,n,digest in RANGES],
      'scan_slots':'1..12 ascending, zero in RAM $054E,X is free, all full returns X=$0D A=$01',
      'four_fields':[f'{x:04X}' for x in FIELDS4],
      'extra_fourteen_fields':[f'{x:04X}' for x in FIELDS14],
      'all_indexed_fields_count':len(FIELDS4)+len(FIELDS14),
      'reference_scope':'previously strict-certified 0508 original bytes; pure C++ source lift / structural equivalence test, no new gameplay domain proof',
      'new_strict_PRG_bytes':0,'new_VPP_points':0,'rom_code_data_exported':False}
if __name__=='__main__':
    report=audit(Path(sys.argv[1]).read_bytes())
    if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('PASS original fixed FF06/FF14 actor helper ROM hashes and 18 stores')
