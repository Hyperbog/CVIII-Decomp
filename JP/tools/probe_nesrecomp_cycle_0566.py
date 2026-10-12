#!/usr/bin/env python3
"""Probe upstream NESRecomp cycle-code generation on authenticated JP mapper24.

This is a COMPATIBILITY PROBE, not an assertion of an existing working port.
No upstream PolyForm Noncommercial source, ROM, generated code or game assets
are copied into the CVIII Git history.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SIZE=393232

def mapper_header(data:bytes)->int:
    if len(data)!=16 or data[:4]!=b'NES\x1a':
        raise ValueError('not a 16-byte original iNES header')
    return (data[6]>>4)|(data[7]&0xf0)

def authenticate(path:Path)->dict:
    raw=path.read_bytes()
    if len(raw)!=SIZE or hashlib.sha256(raw).hexdigest()!=JP_SHA:
        raise ValueError('original Japanese Akumajou Densetsu SHA-256 mismatch')
    number=mapper_header(raw[:16])
    if number!=24:raise ValueError(f'expected Konami VRC6a mapper24, got {number}')
    return {'sha256':JP_SHA,'mapper':number,'size':SIZE}

def probe(rom:Path,tool:Path,out:Path)->dict:
    evidence=authenticate(rom)
    root=ROOT.resolve()
    destination=out.resolve()
    if destination==root or root in destination.parents:
        raise ValueError('generated original-ROM C must remain outside the repository')
    if not tool.is_file():raise FileNotFoundError('NESRecomp CLI unavailable: '+str(tool))
    destination.mkdir(parents=True,exist_ok=True)
    cmd=[str(tool.resolve()),'build','--rom',str(rom.resolve()),
         '--backend','cycle','--output',str(destination)]
    run=subprocess.run(cmd,capture_output=True,text=True)
    if run.returncode:
        raise RuntimeError('NESRecomp mapper24 cycle backend probe rejected build (exit '
                           +str(run.returncode)+'): '+run.stderr[-1500:])
    generated=list(destination.rglob('*_cyc*.c'))
    if not generated:
        raise ValueError('generator returned success but emitted no cycle C units')
    result={'schema':'JP-0566-nesrecomp-vrc6-cycle-compat-probe/v1',
            'original_rom_sha256':evidence['sha256'],
            'mapper':24,'backend':'cycle','generator_completed':True,
            'generated_cycle_c_units':len(generated),
            'compiled_program_tested':False,'gameplay_parity':False,
            'strict_prg_new_bytes':0}
    (destination/'jp_cycle_probe.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--tool',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:
        header=bytearray(16);header[:4]=b'NES\x1a';header[6]=0x80;header[7]=0x10
        assert mapper_header(bytes(header))==24
        header[6]=0
        assert mapper_header(bytes(header))==16
        print('PASS ROM-free upstream NESRecomp mapper24 header/compatibility probe policy')
        return
    if not (a.rom and a.tool and a.out):p.error('--rom, --tool, --out required')
    print(json.dumps(probe(a.rom,a.tool,a.out),sort_keys=True))
if __name__=='__main__':main()
