#!/usr/bin/env python3
"""JP0837: private mapper24 interpreted-ROM seed audit and first divergence.

With --native-exe, runs the JP0835 schedule in native and interpreter-only
NESRecomp modes. Observed 4k PRG misses are NOT total execution coverage.
No original Mesen CPU instruction trace is present in the JP0835 archive.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jp0836_stage1_fresh_replay as replay
import jp0834_sync_stage1_capture as bridge
import jp0833_stage1_lifetime_diff as actors

ENGINE_PIN = '2b4fcdb98c9e702be3fb365cfc645003c50b5fc1'
MISS = re.compile(r'^4k:([0-9a-fA-F]{1,2}):([0-9a-fA-F]{4})\s+([0-9]+)$')
HASH = re.compile(r'^(\d+) trace=([0-9A-F]{16}) mem=([0-9A-F]{16}) '
                  r'PC=([0-9A-F]{4}) A=([0-9A-F]{2}) X=([0-9A-F]{2}) '
                  r'Y=([0-9A-F]{2}) S=([0-9A-F]{2}) P=([0-9A-F]{2}) '
                  r'int=([01]{2}) cycles=(\d+) hw=([0-9A-F]{16})$')
FIELDS = ('trace','mem','PC','A','X','Y','S','P','int','cycles','hw')


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def rom_prg(path):
    image = path.read_bytes()
    require(len(image) == 393232 and hashlib.sha256(image).hexdigest() == replay.ROM_SHA256,
            'wrong original Japanese ROM SHA-256')
    require(image[:4] == b'NES\x1a' and image[6] >> 4 == 8 and
            image[7] & 0xf0 == 0x10 and image[4] == 16,
            'not expected mapper24/256KiB iNES image')
    return image[16:16+262144]


def bank_misses(path, prg):
    """Read the *pinned engine*'s 4KB miss-log, without interpreting RAM comments."""
    lines = path.read_text(encoding='ascii').splitlines()
    require(lines and lines[0].startswith('# ROM instruction starts executed by the interpreter:'),
            'missing pinned NESRecomp miss-log header')
    bank_count = len(prg)//4096
    counts = {}
    for line in lines:
        if not line or line.startswith('#'):
            continue
        m = MISS.fullmatch(line.strip())
        require(m is not None, f'unsupported/unqualified miss-log row: {line[:64]}')
        bank, pc, count = int(m[1],16),int(m[2],16),int(m[3])
        require(0 <= bank < bank_count and 0x8000 <= pc <= 0xffff and
                0 < count <= 0xffffffff, 'miss-log invalid bank, PC or count')
        # Mapper 24 fixes its last 8KB at E000-FFFF. The physical 4KB bank
        # includes the CPU-slot subpage in its identity.
        if pc >= 0xe000:
            require(bank == bank_count - 2 + ((pc >> 12) & 1),
                    'mapper24 fixed E000-FFFF bank identity inconsistent')
        key=(bank,pc)
        require(key not in counts,'duplicate miss-log bank/address record')
        counts[key]=count
    # An empty validated miss-log means no interpreted ROM starts were observed.
    # It is not evidence that every bank or gameplay route has been covered.
    rows=[]
    for (bank,pc),count in sorted(counts.items()):
        off=bank*4096+(pc&0x0fff)
        rows.append({'bank4k':bank,'pc':pc,'prg_file_offset':off,
                     'opcode':prg[off],'interpreter_entry_count':count})
    return rows


def seeds(rows):
    return ('# JP0837 observed *interpreted* ROM instruction starts; JP mapper24\n'
            '# Physical 4KB PRG bank, CPU address, execution count (pinned NESRecomp format)\n'+
            ''.join(f'4k:{r["bank4k"]:02X}:{r["pc"]:04X} {r["interpreter_entry_count"]}\n'
                    for r in rows))


def hashes(path):
    result={}
    for line in path.read_text(encoding='ascii').splitlines():
        m=HASH.fullmatch(line)
        require(m is not None, 'bad NESRecomp hash-out record')
        frame=int(m[1]);require(frame == len(result), 'hash frame skipped/duplicated')
        result[frame]=dict(zip(FIELDS,m.groups()[1:]))
    require(len(result)==replay.END_FRAME+1, 'incomplete native/interpreter hash epoch')
    return result


def first_hash_difference(a,b):
    require(a.keys()==b.keys(), 'hash frame ranges differ')
    for frame in a:
        diff={key:{'native':a[frame][key],'interpreter':b[frame][key]}
              for key in FIELDS if a[frame][key]!=b[frame][key]}
        if diff:
            return {'frame':frame,'fields':diff}
    return None


def first_ram_difference(reference, native):
    require(reference.keys()==native.keys(), 'post-frame ranges differ')
    watched=set(actors.addresses())
    for frame in reference:
        a,b=reference[frame],native[frame]
        require(len(a)==len(b)==2048,'wrong CPU RAM snapshot length')
        if a==b: continue
        different=[i for i in range(2048) if a[i]!=b[i]]
        watched_diff=[i for i in different if i in watched]
        return {'frame':frame,'different_cpu_ram_bytes':len(different),
                'first_8': [{'address':f'{p:04X}','mesen':f'{a[p]:02X}',
                             'native':f'{b[p]:02X}'} for p in different[:8]],
                'first_watched':None if not watched_diff else {
                    'address':f'{watched_diff[0]:04X}',
                    'mesen':f'{a[watched_diff[0]]:02X}',
                    'native':f'{b[watched_diff[0]]:02X}'},
                'original_source3_slot1':replay.actor_parent(a,1)==3,
                'original_source4_slot2':replay.actor_parent(a,2)==4,
                'native_source3_slot1':replay.actor_parent(b,1)==3,
                'native_source4_slot2':replay.actor_parent(b,2)==4}
    return None


def file_write(path,content):
    replay.write_private(path,content.encode('ascii'))


def run(exe,rom,folder,mode):
    base=['--headless','--edition','original','--frames',str(replay.END_FRAME+1),
          '--input',str((folder/'native-local.input').resolve()),
          '--hash-out',str((folder/f'{mode}.hashes').resolve()),
          '--frame-log',str((folder/f'{mode}.cycframe').resolve()),
          '--frame-log-frames',f'{replay.FIRST_COMPARISON}:{replay.END_FRAME}',
          '--frame-log-at','mesen']
    if mode=='native':
        base+=['--miss-log',str((folder/'native.misses').resolve())]
    else:
        base+=['--interp-only']
    outputs=[folder/f'{mode}.hashes',folder/f'{mode}.cycframe']
    if mode=='native':outputs.append(folder/'native.misses')
    require(not any(p.exists() for p in outputs),
            f'{mode} run outputs exist; use fresh private out-dir')
    result=subprocess.run([str(exe.resolve()),str(rom.resolve()),*base],
                          capture_output=True,text=True,timeout=3600)
    file_write(folder/f'{mode}.stdout',result.stdout)
    file_write(folder/f'{mode}.stderr',result.stderr)
    require(result.returncode==0,f'{mode} NESRecomp run failed (exit {result.returncode})')


def analyse(rom,archive,out,exe=None,existing=False):
    prg=rom_prg(rom)
    masks,frames,source=replay.parse_archive(archive)
    out.mkdir(parents=True,exist_ok=True,mode=0o700)
    file_write(out/'native-local.input',replay.schedule(masks))
    if exe:
        require(exe.is_file(), 'no native executable at --native-exe')
        run(exe,rom,out,'native')
        run(exe,rom,out,'interp')
    elif existing:
        require(all((out/n).is_file() for n in
                    ('native.hashes','interp.hashes','native.cycframe',
                     'interp.cycframe','native.misses')),
                'existing diagnostic files incomplete')
    else:
        return {'status':'capture_authenticated_no_native_trace',
                'source':source,'verified_bank_coverage':False,
                'first_divergence_measured':False}
    rows=bank_misses(out/'native.misses',prg)
    file_write(out/'jp0837-bank-qualified-seeds.txt',seeds(rows))
    native_hash=hashes(out/'native.hashes')
    interp_hash=hashes(out/'interp.hashes')
    selected={f for f in frames if f>=replay.FIRST_COMPARISON}
    original={f:frames[f] for f in sorted(selected)}
    native=bridge.native_frames(out/'native.cycframe',selected)
    interp=bridge.native_frames(out/'interp.cycframe',selected)
    return {'status':'executed_here' if exe else 'unattested_existing_artifacts',
            'engine_revision_expected':ENGINE_PIN,
            'engine_binary_revision_verified':False,
            'source_archive_sha256':source['archive_sha256'],
            'input_sha256':source['original_input_sha256'],
            'miss_log_is_interpreter_gaps_only':True,
            'bank_qualified_interpreter_entries':len(rows),
            'bank_qualified_4k_banks':sorted({r['bank4k'] for r in rows}),
            'total_logged_interpreter_entries':sum(r['interpreter_entry_count'] for r in rows),
            'first_native_vs_interpreter_hash_difference':first_hash_difference(native_hash,interp_hash),
            'first_mesen_vs_native_cpu_ram_difference':first_ram_difference(original,native),
            'first_mesen_vs_interpreter_cpu_ram_difference':first_ram_difference(original,interp),
            'full_original_gameplay_parity_proven':False,
            'input_bus_phase_proven':False}


def smoke():
    prg=bytes(range(256))*1024
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        f=Path(d)/'misses'; f.write_text('# ROM instruction starts executed by the interpreter: PRG bank, address, count.\n4k:01:8123 4\n4k:3E:E010 7\n')
        rows=bank_misses(f,prg)
        require(len(rows)==2 and rows[0]['prg_file_offset']==0x1123 and
                rows[1]['opcode']==prg[0x3e010], 'wrong physical bank decoding')
        f.write_text('# ROM instruction starts executed by the interpreter: PRG bank, address, count.\n')
        require(bank_misses(f,prg)==[], 'empty valid miss-log rejected')
        f.write_text('# ROM instruction starts executed by the interpreter: PRG bank, address, count.\n4k:01:8123 4\n4k:3D:E010 7\n')
        try:bank_misses(f,prg)
        except ValueError:pass
        else:raise AssertionError('fixed mapper window accepted wrong bank')
        base=bytearray(2048);base[0x35]=1
        a=bytes(base);base[0x550]=0x3d
        observed=first_ram_difference({3090:a,3091:a},{3090:a,3091:bytes(base)})
        require(observed['frame']==3091 and observed['first_watched']['address']=='0550',
                'wrong first watched RAM divergence')
        x={0:dict(zip(FIELDS,['0']*len(FIELDS)))}
        y={0:dict(x[0])};y[0]['trace']='1'
        require(first_hash_difference(x,y)['frame']==0,'hash mismatch ignored')
    print('PASS JP0837 ROM bank qualification, fixed-window rejection, first-RAM/hash divergence')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--owner-capture',type=Path)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--native-exe',type=Path)
    p.add_argument('--existing',action='store_true')
    p.add_argument('--smoke',action='store_true')
    a=p.parse_args()
    try:
        if a.smoke:smoke();return 0
        require(a.rom and a.owner_capture and a.out_dir,
                'require --rom --owner-capture --out-dir')
        result=analyse(a.rom,a.owner_capture,a.out_dir,a.native_exe,a.existing)
        file_write(a.out_dir/'jp0837-report.json',json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        if result['status']=='capture_authenticated_no_native_trace':return 0
        if result['status']!='executed_here':return 1
        return int(any(result[k] for k in (
            'first_native_vs_interpreter_hash_difference',
            'first_mesen_vs_native_cpu_ram_difference',
            'first_mesen_vs_interpreter_cpu_ram_difference')))
    except (ValueError, OSError, subprocess.TimeoutExpired) as e:
        print(f'JP0837 ERROR: {e}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())