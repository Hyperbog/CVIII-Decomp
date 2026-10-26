#!/usr/bin/env python3
"""Private, reversible original-JP stage resource extraction: raw0E:BE8B-BF39.

No original resource data is embedded in this tool. --export writes a local
editor-friendly JSON from the user's OWN original JP ROM; --pack returns only
these 175 resource bytes (NOT a ROM). Unmodified exports round-trip exactly.
Original game runtime/liveness and mod application are NOT implemented.
"""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RAW0A_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
RAW0E_SHA='9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5'
SPAN_SHA='977745b341cfa56056be96e454d2e49e5d91084b798e82b1a1e819dcfcdab479'
SCHEMA='JP-VRC6-original-room-resource-fivebyte/v1'
ROOTS=(0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C)
COUNTS=(10,7,4,4,5)
SOURCE_START=0xBE8B; SOURCE_END=0xBF3A

def sha(v):return hashlib.sha256(v).hexdigest()
def insist(ok,why):
    if not ok:raise ValueError(why)
def original(rom):
    insist(len(rom)==393232 and sha(rom)==ROM_SHA and rom[:4]==b'NES\x1a',
           'refuse anything other than the exact original JP cartridge')
    prg=rom[16:16+262144]
    bank0a=prg[10*16384:11*16384]
    bank0e=prg[14*16384:15*16384]
    insist(sha(bank0a)==RAW0A_SHA and sha(bank0e)==RAW0E_SHA,
           'physical mapper bank drift')
    found=tuple(bank0a[0x38C2+2*i] | bank0a[0x38C3+2*i]<<8 for i in range(5))
    insist(found==ROOTS,'actual original five-pointer table drift')
    insist(sha(bank0e[SOURCE_START-0x8000:SOURCE_END-0x8000])==SPAN_SHA,
           'actual 175-byte physical source window drift')
    return bank0e

def layout():
    entries=[(i,ROOTS[i],COUNTS[i]) for i in range(5)]
    # Physical memory order differs from selector order.
    sorted_entries=sorted(entries,key=lambda e:e[1]);cursor=SOURCE_START
    for _,root,n in sorted_entries:
        insist(root==cursor,'unaccounted gap in original source streams')
        cursor+=5+5*n  # 4 header bytes + 5×record count + FF
    insist(cursor==SOURCE_END,'expected 175 physical source bytes')
    return sorted_entries

def header_ram_effects(header):
    """Original raw0A:$B808-$B83F header writes, not inferred actor identities."""
    insist(len(header)==4,'four original header bytes required')
    return {
        'ram_0034':int(header[0])>>4,
        'ram_0035':int(header[0])&15,
        'ram_0036':int(header[1])>>4,
        'ram_0054':int(header[1])&15,
        'ram_0072':int(header[1])&1,
        'ram_07A1':int(header[2]),
        'ram_054E':int(header[3])
    }

def extract(bank):
    insist(len(bank)==16384,'exact raw16 bank0E required')
    items=[]
    for index,root,count in layout():
        offset=root-0x8000
        stream=bank[offset:offset+5+5*count]
        insist(len(stream)==5+5*count and stream[-1]==255,
               'original record stream missing exact FF terminal')
        insist(all(stream[4+5*j]!=255 for j in range(count)),
               'early original FF terminator in record first byte')
        rows=[]
        for j in range(count):
            rows.append({
               'id':f'jp-room0e-{index:02d}-record-{j:02d}',
               'source_cpu':f'{root+4+5*j:04X}',
               'fields':[int(v) for v in stream[4+5*j:9+5*j]],
               'ram_offsets':[f'{p+j+1:04X}' for p in (0x48C,0x400,0x438,0x41C,0x4A8)],
               'enabled_ram':f'{0x54E+j+1:04X}'
            })
        items.append({'id':f'jp-room0e-{index:02d}',
            'selector':index,'physical_raw_prg':'0E',
            'source_cpu':f'{root:04X}',
            'header_bytes':[int(x) for x in stream[:4]],
            'header_ram_effects':header_ram_effects(stream[:4]),
            'records':rows,'terminator':255})
    return {'schema':SCHEMA,'source_rom_sha256':ROM_SHA,
        'source_bank':'raw0E','source_bank_cpu_span':'BE8B-BF39',
        'source_length_bytes':175,
        'source_windows_accounted':5,
        'repacked_byte_sha256':SPAN_SHA,
        'ram_0034_zero_stream_count':sum(
            item['header_ram_effects']['ram_0034']==0 for item in items),
        'streams':sorted(items,key=lambda item:item['selector']),
        'warning':'Private original source. The five streams are not evidenced as Stage 1 actor spawns; their header RAM selectors must be checked before any stage-specific use.'}

def pack(doc):
    insist(type(doc) is dict and doc.get('schema')==SCHEMA,'wrong stage resource schema')
    insist(doc.get('source_rom_sha256')==ROM_SHA,'wrong cartridge source identity')
    insist(doc.get('source_bank')=='raw0E' and doc.get('source_bank_cpu_span')=='BE8B-BF39'
           and doc.get('source_length_bytes')==175 and doc.get('source_windows_accounted')==5,
           'physical/source boundary mismatch')
    data=doc.get('streams')
    insist(type(data) is list and len(data)==5,'expected exactly 5 source stream objects')
    payload=bytearray()
    for selector,root,count in layout():
        item=next((x for x in data if type(x) is dict and x.get('selector')==selector),None)
        insist(item is not None and item.get('id')==f'jp-room0e-{selector:02d}' and
               item.get('source_cpu')==f'{root:04X}' and
               item.get('physical_raw_prg')=='0E',
               'unstable stream selector or source physical address')
        header=item.get('header_bytes')
        insist(type(header) is list and len(header)==4 and all(type(v) is int and 0<=v<=255 for v in header),
               'header requires 4 exact 8-bit source bytes')
        effects=item.get('header_ram_effects')
        if effects is not None:
            insist(effects==header_ram_effects(header),
                   'header RAM effects disagree with original header bytes')
        payload.extend(header)
        rows=item.get('records')
        insist(type(rows) is list and len(rows)==count,'changed stream record count')
        for j,row in enumerate(rows):
            insist(type(row) is dict and row.get('id')==f'jp-room0e-{selector:02d}-record-{j:02d}'
                   and row.get('source_cpu')==f'{root+4+5*j:04X}',
                   'record ID/source address shifted')
            fields=row.get('fields')
            insist(type(fields) is list and len(fields)==5 and
                   all(type(v) is int and 0<=v<=255 for v in fields) and fields[0]!=255,
                   'record requires 5 legal bytes, first field cannot be FF')
            insist(row.get('ram_offsets')==[f'{p+j+1:04X}' for p in (0x48C,0x400,0x438,0x41C,0x4A8)] and
                   row.get('enabled_ram')==f'{0x54E+j+1:04X}',
                   'source-proven RAM output mapping drift')
            payload.extend(fields)
        insist(item.get('terminator')==255,'missing exact FF stream terminator')
        payload.append(255)
    stage0_count=sum(
        header_ram_effects(next(x for x in data if x['selector']==i)['header_bytes'])['ram_0034']==0
        for i in range(5))
    if 'ram_0034_zero_stream_count' in doc:
        insist(doc['ram_0034_zero_stream_count']==stage0_count,
               'stage-zero source classification disagrees with stream headers')
    insist(len(payload)==175,'not exact original five-stream source extent')
    return bytes(payload)

def smoke():
    # Fully invented stage content, no game-byte data. A complete synthetic
    # root-boundary roundtrip and targeted schema/command corruption checks.
    bank=bytearray(16384)
    for selector,root,count in layout():
        p=root-0x8000
        for j in range(4):bank[p+j]=(selector*41+j*17+7)&255
        for j in range(count):
            for k in range(5): bank[p+4+j*5+k]=(selector*19+j*3+k*11+1)&255
        bank[p+4+count*5]=255
    doc=extract(bytes(bank))
    encoded=pack(doc)
    insist(encoded==bytes(bank[SOURCE_START-0x8000:SOURCE_END-0x8000]),
           'synthetic stage resource extraction roundtrip differs')
    for mutate in ('selector','count','field','terminator','ram','source','header','decoded','stage0_count'):
        broken=copy.deepcopy(doc)
        s=broken['streams'][0]
        if mutate=='selector':s['selector']=7
        if mutate=='count':s['records'].pop()
        if mutate=='field':s['records'][0]['fields'][0]=255
        if mutate=='terminator':s['terminator']=0
        if mutate=='ram':s['records'][0]['ram_offsets'][1]='DEAD'
        if mutate=='source':s['source_cpu']='9000'
        if mutate=='header':s['header_bytes'][0]=256
        if mutate=='decoded':s['header_ram_effects']['ram_0034']^=1
        if mutate=='stage0_count':broken['ram_0034_zero_stream_count']=100
        try:pack(broken)
        except ValueError:pass
        else:raise AssertionError('unsafe source-data mutation admitted: '+mutate)
    print('PASS JP0659 ROM-free original room schema, exact 175-byte invented source roundtrip and 7 rejection gates')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--export',type=Path,help='private local JSON; contains copyrighted source byte data')
    p.add_argument('--input',type=Path,help='editable JSON for validated re-encoding')
    p.add_argument('--pack',type=Path,help='private local 175-byte resource block, not a ROM')
    p.add_argument('--roundtrip',action='store_true')
    args=p.parse_args()
    if args.smoke:smoke()
    if args.rom:
        b=original(args.rom.read_bytes())
        source=extract(b)
        encoded=pack(source)
        insist(sha(encoded)==SPAN_SHA and
               encoded==b[SOURCE_START-0x8000:SOURCE_END-0x8000],
               'original game resource roundtrip failed')
        if args.export:args.export.write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
        if args.roundtrip:
            print('PASS JP0659 authentic original 175 source bytes / 5 streams / 30 typed record instances')
            stages=[item['header_ram_effects']['ram_0034'] for item in source['streams']]
            print('Original header $34 values:', ','.join(f'{v:02X}' for v in stages),
                  '; $34=00 matches:',source['ram_0034_zero_stream_count'])
    if args.input:
        source=json.loads(args.input.read_text(encoding='utf-8'))
        packed=pack(source)
        if args.pack:args.pack.write_bytes(packed)
        if args.rom and not args.pack:
            insist(sha(packed)==SPAN_SHA,'modified local resource does not equal unmodified cartridge')
        print('PASS JP0659 local stage resource schema:',len(packed),'bytes')
    elif args.pack:p.error('--pack requires --input')
    if not args.smoke and not args.rom and not args.input:p.error('--smoke, --rom, or --input required')
if __name__=='__main__':main()
