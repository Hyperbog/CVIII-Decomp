#!/usr/bin/env python3
"""Owner-private JP Stage 1 ROM/source attestation and paired actor-RAM differential.

The optional paired traces MUST use the same controller-poll replay and the
same post-frame boundary. Frame samples cannot prove intermediate writes.
"""
import argparse
import hashlib
import json
from pathlib import Path

JP = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANKS = {
    10: '1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8',
    11: '17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a',
    15: '96990dfb1b859cfbcebed583ac100cc49aefe235ab61220fafa365dabba88964',
}
WINDOWS = {
    (11,0x8001,0x804b,0x8000): '4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9',
    (11,0xb486,0xb53f,0x8000): 'dd9bd653a17930cce3e37105bea6e6fdf3f9c846c35aa388295ee192c7e457fd',
    (15,0xe249,0xe264,0xc000): '5a5d7b8a0f857c8062faee305b4d752522f281bda0271e402cd4c66759b37324',
    (15,0xe2d0,0xe2d6,0xc000): '8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380',
}
SCHEMA = 'CVIII-JP0833-actor-postframe/v1'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def attest(path):
    rom = path.read_bytes()
    require(len(rom) == 393232 and rom[:4] == b'NES\x1a' and sha(rom) == JP,
            'unrecognized original Japanese VRC6 cartridge')
    prg = rom[16:16+262144]
    for bank, expected in BANKS.items():
        require(sha(prg[bank*16384:(bank+1)*16384]) == expected,
                'physical PRG bank identity mismatch')
    for (bank, start, end, base), expected in WINDOWS.items():
        b = prg[bank*16384+start-base:bank*16384+end-base]
        require(sha(b) == expected, f'original opcode window {start:04X} differs')
    bank = prg[10*16384:11*16384]
    def byte(pc):
        require(0x8000 <= pc <= 0xbfff, 'raw0A pointer out of range')
        return bank[pc-0x8000]
    def word(pc):
        return byte(pc) | (byte(pc+1) << 8)
    require((byte(0x91c6),byte(0x921e)) == (0x13,0x3d),
            'source-script/type crosswalk changed')
    rows = []
    for phase in range(6):
        event = byte(0x93e8+2*phase)
        doubled = (event*2) & 255
        fallback = bool(event & 0x80 and doubled >= 0xa0)
        table = 0x9f6e if not(event & 0x80) or fallback else 0xa06e
        pointer = word(table + (0 if fallback else doubled))
        rows.append((pointer,byte(pointer)))
    require([x[1] for x in rows] == [0,0,0,0x32,0x32,0],
            'six source-slot event rows differ')
    for phase,pc,x,y in ((3,0xa444,160,80),(4,0xa43f,192,176)):
        rec = [byte(pc+i) for i in range(5)]
        require(rows[phase] == (pc,0x32) and (phase-1)*64+rec[1] == x and
                rec[2] == y and rec[3:] == [0,0], 'actor source identity differs')
    require(sha(bank[0xab1f-0x8000:0xab5f-0x8000]) ==
            'dd742e7f329382fed658e0b2d6847cc3b55965b55380a2c8fd057b75cc15917e',
            'chapel original source span differs')
    return {'original_rom_sha256':JP, 'stage1_source':'00/01/00',
            'source_phases':[3,4], 'record_cpu':['A444','A43F'],
            'source_world_xy':[[160,80],[192,176]], 'original_opcode_windows':4,
            'scope':'ROM source identity; does not prove per-frame gameplay'}


def load_trace(path, source):
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    require(3 <= len(records) <= 200001, 'at least two frame snapshots required')
    head = records.pop(0)
    digest = head.get('input_sha256')
    require(head.get('schema') == SCHEMA and head.get('source') == source and
            head.get('rom_sha256') == JP and head.get('boundary') == 'post-frame' and
            type(digest) is str and len(digest) == 64 and
            set(digest) <= set('0123456789abcdef'),
            f'{source} provenance or controller poll fingerprint missing')
    out = {}
    previous = -1
    for row in records:
        frame, raw = row.get('frame'),row.get('ram_hex')
        require(type(frame) is int and frame > previous and
                type(raw) is str and len(raw) == 4096,
                'bad, duplicate or out-of-order frame')
        try:
            memory = bytes.fromhex(raw)
        except ValueError as e:
            raise ValueError('nonhex RAM') from e
        require(len(memory) == 2048, 'not 2KiB internal RAM')
        out[frame] = memory
        previous = frame
    return head,out


def addresses():
    addrs = [0x18,0x34,0x35,0x36,0x53,0x54,0x62,0x65,0x7f6]
    for off in (0x7c2,0x7c8,0x7e0):
        addrs.extend(off+s for s in range(6))
    for off in (0x400,0x41c,0x438,0x470,0x48c,0x4a8,
                0x4c4,0x4db,0x4f2,0x509,0x520,0x537,
                0x54e,0x645,0x669,0x67b):
        addrs.extend(off+slot for slot in range(1,13))
    return sorted(set(addrs))


def compare(left,right):
    a_head,a = left
    b_head,b = right
    require(a_head['input_sha256'] == b_head['input_sha256'],
            'unaligned controller poll input schedule')
    require(set(a) == set(b), 'post-frame snapshot frame sets differ')
    mismatch = []
    sources = {3:0,4:0}
    for frame in sorted(a):
        original,native = a[frame],b[frame]
        require(tuple(original[k] for k in (0x34,0x35,0x36)) == (0,1,0),
                'Mesen reference outside Stage 1-02')
        for slot in range(1,13):
            parent = original[0x645+slot]
            if (parent in sources and original[0x54e+slot] == 0x3d and
                    original[0x470+slot]&4):
                sources[parent] += 1
        for k in addresses():
            if original[k] != native[k] and len(mismatch) < 64:
                mismatch.append({'frame':frame,'ram':f'{k:04X}',
                                 'mesen':f'{original[k]:02X}',
                                 'native':f'{native[k]:02X}'})
    return {'schema':'CVIII-JP0833-actor-lifetime-diff/v1',
            'matched_actor_ram_samples':not mismatch,
            'sampled_frames':len(a),'first_mismatches':mismatch,
            'mesen_source3_4_sampled_slots':sources,
            'intermediate_actor_writers_observed':False,
            'full_gameplay_parity_certified':False}


def smoke():
    ram = bytearray(2048)
    ram[0x35] = 1
    for slot,parent in ((1,3),(2,4)):
        ram[0x54e+slot] = 0x3d
        ram[0x470+slot] = 4
        ram[0x645+slot] = parent
    head = {'schema':SCHEMA,'rom_sha256':JP,'boundary':'post-frame',
            'input_sha256':'a'*64}
    data = {3092:bytes(ram),3093:bytes(ram)}
    good = compare((dict(head,source='mesen'),data),
                   (dict(head,source='native'),data))
    require(good['matched_actor_ram_samples'] and
            good['mesen_source3_4_sampled_slots'] == {3:2,4:2},
            'identical source-backed actors rejected')
    modified = dict(data)
    damaged = bytearray(ram)
    damaged[0x550] = 0
    modified[3093] = bytes(damaged)
    bad = compare((dict(head,source='mesen'),data),
                  (dict(head,source='native'),modified))
    require(not bad['matched_actor_ram_samples'] and
            bad['first_mismatches'][0]['ram'] == '0550',
            'actor deallocation divergence not detected')
    try:
        compare((dict(head,source='mesen'),data),
                (dict(head,source='native',input_sha256='b'*64),data))
    except ValueError:
        pass
    else:
        raise ValueError('different input epochs admitted')
    print('PASS JP0833 synthetic actor differential, deallocation detection, poll-epoch rejection')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--mesen-frames',type=Path)
    p.add_argument('--native-frames',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--smoke',action='store_true')
    args = p.parse_args()
    require(bool(args.mesen_frames) == bool(args.native_frames),
            'paired Mesen and native frame traces required')
    require(args.rom or args.smoke, 'provide --rom or --smoke')
    if args.smoke:
        smoke()
    if args.rom:
        result = attest(args.rom)
        if args.mesen_frames:
            result['actor_differential'] = compare(
                load_trace(args.mesen_frames,'mesen'),
                load_trace(args.native_frames,'native'))
        if args.report:
            args.report.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        return int(args.mesen_frames is not None and
                   not result['actor_differential']['matched_actor_ram_samples'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
