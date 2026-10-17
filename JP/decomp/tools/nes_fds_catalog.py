#!/usr/bin/env python3
"""Read-only, ROM-free FDS and QD block/file inventory for preservation.

References: https://www.nesdev.org/wiki/FDS_disk_format
            https://www.nesdev.org/wiki/FDS_file_format
            https://www.nesdev.org/wiki/QD
FDS images omit hardware gaps and CRC; QD includes 2-byte CRC words.
Data and BIOS bytes are never emitted. CRC is present but not independently checked.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

FDS_SIDE=65500
QD_SIDE=65536
DISK_SIGNATURE=b'*NINTENDO-HVC*'

class FdsFormatError(ValueError):
    pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def name8(raw: bytes) -> str:
    # Metadata may not be ASCII. Escape rather than dropping bytes.
    return ''.join(chr(x) if 0x20<=x<=0x7e else f'\\x{x:02X}' for x in raw)

def side_catalog(side: bytes, side_index: int, crc_words: bool = False) -> dict:
    if len(side)!=(QD_SIDE if crc_words else FDS_SIDE):
        raise FdsFormatError('wrong disk-side geometry')
    off=0
    def read_block(marker: int, length: int) -> tuple[int,bytes]:
        nonlocal off
        start=off
        if off+length+(2 if crc_words else 0)>len(side):
            raise FdsFormatError(f'side {side_index}: truncated block {marker} at {off}')
        if side[off]!=marker:
            raise FdsFormatError(f'side {side_index}: expected block {marker} at {off}, found {side[off]}')
        payload=side[off:off+length]
        off+=length+(2 if crc_words else 0)
        return start,payload
    disk_off,block1=read_block(1,56)
    if block1[1:15]!=DISK_SIGNATURE:
        raise FdsFormatError(f'side {side_index}: invalid FDS disk signature')
    count_off,block2=read_block(2,2)
    count=block2[1]
    files=[]
    def read_one(hidden: bool):
        file_off,h=read_block(3,16)
        file_len=int.from_bytes(h[13:15],'little')
        data_off,d=read_block(4,1+file_len)
        # ROM payload excluded: hashes and length only.
        record={
            'file_number':h[1], 'file_id':h[2], 'name':name8(h[3:11]),
            'load_address':int.from_bytes(h[11:13],'little'),
            'size_bytes':file_len, 'type':h[15],
            'header_block_offset':file_off,'data_block_offset':data_off,
            'data_sha256':sha(d[1:]),'hidden_after_declared_count':hidden
        }
        files.append(record)
    for _ in range(count):read_one(False)
    # BIOS normally honors the declared file count. Some FDS titles use
    # independent routines to read additional blocks. Locate only complete
    # correctly sequenced adjacent hidden pairs (no assumption of liveness).
    while off<len(side) and side[off]==3:
        old=off
        try:read_one(True)
        except FdsFormatError:
            off=old  # malformed trailing marker belongs to tail, not file list
            break
    tail=side[off:]
    return {
        'side_index':side_index, 'side_sha256':sha(side),
        'header_block_offset':disk_off, 'file_count_block_offset':count_off,
        'licensee_code':block1[0x0F],
        'game_code':name8(block1[0x10:0x13]),
        'game_type':block1[0x13], 'game_version':block1[0x14],
        'disk_number':block1[0x16], 'disk_side':block1[0x15],
        'disk_type':block1[0x17], 'boot_file_id_limit':block1[0x19],
        'declared_file_count':count,
        'visible_file_count':sum(not f['hidden_after_declared_count'] for f in files),
        'possible_hidden_file_count':sum(f['hidden_after_declared_count'] for f in files),
        'files':files,
        'trailing_bytes':len(tail),
        'trailing_nonzero_bytes':sum(x!=0 for x in tail),
        'trailing_sha256':sha(tail),
        'crc_word_bytes_present':crc_words,
        'crc_verified':False
    }

def catalog(data: bytes) -> dict:
    if data[:4]==b'FDS\x1a':
        if len(data)<16:raise FdsFormatError('truncated FDS image header')
        sides=data[16:]; geometry=FDS_SIDE;kind='FDS-headered';crc=False
        if not sides or len(sides)%geometry:raise FdsFormatError('bad headered FDS side geometry')
        reported=data[4]
        if reported not in (0,len(sides)//geometry):
            raise FdsFormatError('FDS header and side count disagree')
    elif len(data)>0 and len(data)%FDS_SIDE==0:
        sides=data;geometry=FDS_SIDE;kind='FDS-unheadered';crc=False
    elif len(data)>0 and len(data)%QD_SIDE==0:
        sides=data;geometry=QD_SIDE;kind='QD-candidate';crc=True
    else:raise FdsFormatError('unrecognized FDS/QD geometry')
    records=[side_catalog(sides[p:p+geometry],p//geometry,crc)
             for p in range(0,len(sides),geometry)]
    return {'schema':'shared-nes-fds-index/v1','format':kind,
            'image_sha256':sha(data),'image_bytes':len(data),
            'side_count':len(records),'side_geometry_bytes':geometry,
            'bios_included':False,'sides':records,
            'strict_verified_game_code_bytes':0,
            'no_payload_or_bios_exported':True,
            'evidence':'disk blocks structurally decoded; no BIOS execution, runtime file loading, hidden-file liveness, CRC validation or game-code semantic proof'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image');p.add_argument('--out')
    a=p.parse_args()
    result=catalog(Path(a.image).read_bytes())
    rendered=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:Path(a.out).write_text(rendered)
    else:print(rendered,end='')
if __name__=='__main__':main()
