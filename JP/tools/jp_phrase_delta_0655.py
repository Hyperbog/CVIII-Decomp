#!/usr/bin/env python3
"""JP0655 original PRG0C phrase arithmetic: source-vs-native bounded replay.

A full original-JP ROM is needed for 6502 opcode replay; --smoke uses only
synthetic integers, never embeds retail source or music payloads.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
from pathlib import Path

ORIGINAL_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA = 'f52c62b3c01fb10e9d727b9e983a2d0c1fc78ef502c5f972f9b28a349b2a9a42'
EXEC_SHA = 'feaba31c42beb226b70c9bc3f4551c4f3a2d1f75ac6c7874c4537f11249a8151'
POOL_SHA = 'a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5'
SUBROUTINE_SHA = {
    (0x8D15,0x8D4C):'30d0ef2f537e579ce47ef71afc54b7ac83fc966a9248c82f22e0890527cbfc74',
    (0x8D4C,0x8D60):'9898cc613eff3a85d480d3a908efd9c7b13a2f265cccfd5a05eecb3f8182d47e',
    (0x8D60,0x8D76):'c5c81eeb8623764bde0889a6e6d1070166ff9f3e9e78c115205d4bf74cf7773c',
    (0x8D76,0x8D90):'b10cf22a11e99bfce83df2b964f72faf986fc4d199eb0def04c01ceaee4eb8ba',
}
BASE = 0x8000
SIZE = 16384


def require(cond: bool, why: str) -> None:
    if not cond: raise ValueError(why)


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bank_from_rom(rom: bytes) -> bytes:
    require(len(rom) == 393232 and digest(rom) == ORIGINAL_SHA and rom[:4] == b'NES\x1a'
            and (rom[6]>>4 | rom[7]&0xF0) == 24,
            'only exact original JP 393232-byte mapper24 cartridge is accepted')
    return rom[16 + 12*SIZE:16+13*SIZE]


def check_bank(bank: bytes) -> None:
    require(len(bank)==SIZE and digest(bank)==BANK_SHA,
            'changed physical original PRG raw0C')
    require(digest(bank[0x8D15-BASE:0x8D90-BASE])==EXEC_SHA,
            'original 8D15-8D8F opcode/operand bytes modified')
    require(digest(bank[0xA42C-BASE:0xA957-BASE])==POOL_SHA,
            'original 1323-byte phrase pool changed')
    for (lo,hi),sha in SUBROUTINE_SHA.items():
        require(digest(bank[lo-BASE:hi-BASE]) == sha,
                f'original 6502 helper source changed at {lo:04X}-{hi-1:04X}')


class Delta(ctypes.Structure):
    _fields_ = [(f,ctypes.c_uint8) for f in (
        'source_byte','entry_x','exit_x','exit_y','exit_a','exit_c','exit_z','exit_n','exit_v',
        'cursor_after','high_nibble_after','scratch_e2_after','low_ec_after',
        'high_ed_after','did_update_high_nibble')]
    _fields_ += [('source_cpu_address',ctypes.c_uint16)]


def original_6502(bank: bytes, initial_ram: bytes, start_x: int):
    """Instruction-fetched original NMOS 6502, $8D15 through nested $8D8F RTS.
    No arithmetic from the host native implementation is reused here.
    Caller begins with control-token classification external to this bounded path.
    """
    mem=bytearray(initial_ram)
    require(len(bank)==SIZE and len(mem)==2048 and 0<=start_x<=255,
            'invalid original replay input')
    pc=0x8D15; x=start_x; a=y=0; c=z=n=v=0
    stack=[]; steps=0
    def flags(value):
        nonlocal z,n
        z=int((value&255)==0);n=int(bool(value&128))
    def get8():
        nonlocal pc
        require(0x8D15<=pc<0x8D90,'unexpected control-flow target')
        v=bank[pc-BASE];pc+=1;return v
    def get16():
        lo=get8();return lo | (get8()<<8)
    while True:
        here=pc;op=get8();steps+=1
        require(steps<2400, 'unbounded source instruction budget')
        if op==0xBD: # LDA absolute,X
            at=(get16()+x)&65535; require(at<len(mem),'out-of-RAM indexed source')
            a=mem[at];flags(a)
        elif op==0xB1: # LDA (zp),Y: physical original ROM mapping for this scope
            zp=get8(); ptr=mem[zp]|mem[(zp+1)&255]<<8
            at=(ptr+y)&65535
            require(0x8000<=at<0xC000,'outside original source bank')
            a=bank[at-BASE];flags(a)
        elif op==0xA8:
            y=a; flags(y)
        elif op==0xC9: # CMP #imm
            v=get8();temp=(a-v)&255
            c=int(a>=v);flags(temp)
        elif op in (0x90,0xB0,0xF0):
            rel=get8();taken=(op==0x90 and not c) or (op==0xB0 and c) or (op==0xF0 and z)
            if taken:pc=(pc+rel-(256 if rel&128 else 0))&65535
        elif op==0x4A:
            c=a&1; a>>=1; flags(a)
        elif op==0x9D: # STA abs,X
            at=(get16()+x)&65535;require(at<len(mem),'out-of-RAM store')
            mem[at]=a
        elif op==0xFE: # INC abs,X
            at=(get16()+x)&65535;require(at<len(mem),'out-of-RAM increment')
            mem[at]=(mem[at]+1)&255;flags(mem[at])
        elif op==0x29:
            a&=get8();flags(a)
        elif op==0x85:
            at=get8();mem[at]=a
        elif op==0x20: # real JSR address and stack memory effects
            target=get16();ret=(pc-1)&65535
            require(len(stack)<6,'recursive source call not supported')
            # 6502 JSR pushes return high, then low, and RTS adds 1.
            sp=0xFF-2*len(stack)
            mem[0x100+sp]=(ret>>8)&255
            mem[0x100+sp-1]=ret&255
            stack.append(pc)
            pc=target
        elif op==0x60:
            if not stack:break
            pc=stack.pop()
        elif op==0xA5: # LDA zero page
            a=mem[get8()];flags(a)
        elif op==0xA9:
            a=get8();flags(a)
        elif op==0x38:c=1
        elif op==0x18:c=0
        elif op==0xE5: # SBC zp, 2A03 binary arithmetic
            operand=mem[get8()];d=a-operand-(1-c);res=d&255
            v=int(bool((a^operand)&(a^res)&0x80));c=int(d>=0);a=res;flags(a)
        elif op==0x65: # ADC zp
            operand=mem[get8()];d=a+operand+c;res=d&255
            v=int(bool((~(a^operand))&(a^res)&0x80));c=int(d>255);a=res;flags(a)
        elif op==0x7D: # ADC abs,X
            at=(get16()+x)&65535;require(at<len(mem),'out-of-RAM ADC')
            operand=mem[at];d=a+operand+c;res=d&255
            v=int(bool((~(a^operand))&(a^res)&0x80));c=int(d>255);a=res;flags(a)
        elif op==0xAA:x=a;flags(x)
        elif op==0xCA:x=(x-1)&255;flags(x)
        elif op==0x4C:pc=get16()
        elif op==0xA6:x=mem[get8()];flags(x)
        elif op==0xE6: # INC zp
            at=get8();mem[at]=(mem[at]+1)&255;flags(mem[at])
        elif op==0xC6: # DEC zp
            at=get8();mem[at]=(mem[at]-1)&255;flags(mem[at])
        else:raise ValueError(f'unhandled original 6502 opcode ${op:02X} at ${here:04X}')
    require(here in (0x8D3D,0x8D4B),'did not exit original ordinary phrase byte path')
    return {'ram':bytes(mem),'a':a,'x':x,'y':y,'c':c,'z':z,'n':n,'v':v,'steps':steps}


def fixture(bank: bytes, source_addr: int, cursor: int, entry_x: int,
            restore_x: int, factor: int, low: int, high: int, tag: int) -> bytes:
    mem=bytearray(2048)
    ptr=(source_addr-cursor)&0xFFFF
    mem[0xE2:0xE4]=ptr.to_bytes(2,'little')
    mem[0x06AA+entry_x]=cursor
    mem[0x03F7+entry_x]=factor
    mem[0x03F2+entry_x]=tag
    mem[0xEE]=restore_x
    mem[0x01AD+restore_x]=low
    mem[0x01B2+restore_x]=high
    return bytes(mem)


def parity(bank: bytes, native_lib: Path, cases: list[tuple[int,int,int,int,int,int,int,int]]) -> dict:
    dll=ctypes.CDLL(str(native_lib.resolve()))
    fn=dll.cviii_phrase_delta_0655
    fn.argtypes=(ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
                 ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
                 ctypes.c_uint8,ctypes.POINTER(Delta))
    fn.restype=ctypes.c_int
    image=(ctypes.c_uint8*SIZE).from_buffer_copy(bank)
    tested=0; zero_multiplier=0; add=0; sub=0; longest=0
    for (source_addr,cursor,x,restore_x,factor,low,high,tag) in cases:
        cmd=bank[source_addr-BASE]
        if cmd>=0xFB:continue
        ram=fixture(bank,source_addr,cursor,x,restore_x,factor,low,high,tag)
        reference=original_6502(bank,ram,x)
        out=Delta()
        ram_in=(ctypes.c_uint8*2048).from_buffer_copy(ram)
        status=fn(image,SIZE,ram_in,2048,x,ctypes.byref(out))
        require(status==1, f'native rejected authentic ordinary byte ${cmd:02X}')
        changed=reference['ram']
        expected=(cmd,x,reference['x'],reference['y'],reference['a'],
                  reference['c'],reference['z'],reference['n'],reference['v'],
                  changed[0x06AA+x],changed[0x03F2+x],changed[0xE2],
                  changed[0xEC],changed[0xED],int(cmd>=16),source_addr)
        actual=tuple(getattr(out,f) for f,_ in Delta._fields_)
        require(actual==expected, f'original 6502/native divergence at {source_addr:04X} '
                f'cmd={cmd:02X}, entry_x={x}, restore_x={restore_x}, factor={factor}, '
                f'base={high:02X}{low:02X}: {actual} != {expected}')
        # Restrict non-stack writes to exact documented result/fields.
        allowed={0x06AA+x, 0x03F2+x, 0xE2, 0xEC, 0xED}
        diff={i for i in range(2048) if changed[i]!=ram[i] and i not in (0x01FF,0x01FE)}
        require(diff.issubset(allowed),'unexpected original CPU RAM write footprint')
        longest=max(longest,reference['steps'])
        tested+=1;zero_multiplier+=factor==0;add+=cmd%16<8;sub+=cmd%16>=8
    require((tested,zero_multiplier,add,sub,longest) == (5610,1122,4775,835,1316),
            'ROM source-domain and bounded execution census changed')
    return {'parity_cases':tested, 'original_ordinary_source_bytes':1122,
            'source_pool_bytes':1323, 'control_source_bytes_not_replayed':201,
            'zero_multipliers':zero_multiplier,
            'nonnegative_nibbles':add,'negative_nibbles':sub,
            'max_reference_instructions':longest,
            'original_gameplay_liveness_verified':False,
            'music_sfx_ownership_verified':False}


def original_cases(bank: bytes):
    # Cover every single byte from the original structurally identified phrase
    # pool, including interior addresses, not just structurally valid roots.
    # This is an *isolated conditional source-data test*, not a live playthrough.
    return [(addr, cursor, x, restore, factor, lo, hi, tag)
            for addr in range(0xA42C,0xA957)
            if bank[addr-BASE] < 0xFB
            for cursor,x,restore,factor,lo,hi,tag in (
                (0,0,0,1,0x00,0x00,0x55),
                (0,1,1,2,0xFF,0x7F,0x23),
                (1,3,2,0,0x80,0xFF,0xCC),
                (128,7,6,255,0x03,0x01,0x5A),
                (255,5,3,17,0xF0,0x00,0x19),
            )]


def smoke() -> None:
    # Artificial repeated-add 6502 counter oracle. The counter wraps from
    # zero to FF; zero factor means 256 iterations, not zero iterations.
    checked=0
    for nibble in range(16):
        amount=nibble if nibble<8 else 16-nibble
        for factor in range(256):
            total=amount; x=factor
            while True:
                x=(x-1)&255
                if not x: break
                total=(total+amount)&255
            require(total==(amount*factor)&255,
                    '6502 repeated-add oracle mismatch')
            checked+=1
    require(checked==4096, 'synthetic numeric coverage drift')
    print('PASS JP0655 ROM-free 4096 repeated-add boundary cases')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--rom',type=Path)
    parser.add_argument('--native-lib',type=Path)
    parser.add_argument('--json',type=Path,help='aggregate metadata only; no ROM bytes')
    args=parser.parse_args()
    if args.smoke:smoke()
    if args.rom:
        bank=bank_from_rom(args.rom.read_bytes());check_bank(bank)
        if not args.native_lib:parser.error('--native-lib built from C11 code required for parity')
        result=parity(bank,args.native_lib,original_cases(bank))
        if args.json:args.json.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print('PASS JP0655 authentic original opcode vs native C11:',result)
    elif not args.smoke:
        parser.error('specify --smoke or --rom ORIGINAL_JP --native-lib LIB')

if __name__=='__main__':main()
