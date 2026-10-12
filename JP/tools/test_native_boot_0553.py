#!/usr/bin/env python3
"""Check every 6502 state (not merely end state) in compiled JP reset -> first NMI."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
from replay_reset_0548 import Bus,CPU,SHA
from static_recompile_boot_0553 import executed
from static_recompile_fixed_0553 import make
ROOT=Path(__file__).resolve().parents[2]
NATIVE=ROOT/'JP/native/boot'

def run(rom:Path,compiler='g++',out:Path|None=None):
    payload=rom.read_bytes()
    if len(payload)!=393232 or hashlib.sha256(payload).hexdigest()!=SHA:raise ValueError('Unauthenticated Japanese ROM')
    sites,meta,_,ref_bus,ref_cpu=executed(payload)
    if meta['trace_executed_physical_instruction_sites']!=403 or meta['original_cpu_instructions']!=11740:raise ValueError('source trace drift')
    from build_whole_cart_recomp_0529 import generate_sources
    with tempfile.TemporaryDirectory(prefix='jp0553-full-source-') as scratch:
        location=Path(scratch)
        generate_sources(payload,location)
        fixed_source=(location/'prg_fixed31.asm').read_text()
        regenerated,verified_manifest=make(payload,fixed_source)
        if regenerated!=(NATIVE/'generated/boot_compiled.cpp').read_text():raise ValueError('native source does not match the original 8K fixed bank')
        saved=json.loads((NATIVE/'generated/boot_native_manifest.json').read_text())
        if saved!=verified_manifest:raise ValueError('stored fixed bank manifest does not match source')
        if saved['compiled_physical_instruction_sites']!=1904:raise ValueError('fixed bank site count drift')
    with tempfile.TemporaryDirectory(prefix='jp0553-cpu-native-') as d:
        exe=Path(d)/'jp_native_boot'
        subprocess.run([compiler,'-std=c++20','-O2','-Wall','-Wextra','-Werror','-pedantic',
                        '-I'+str(NATIVE),str(NATIVE/'generated/boot_compiled.cpp'),
                        str(NATIVE/'../bank0a/generated/bank0a_compiled.cpp'),str(NATIVE/'boot_native_driver.cpp'),'-o',str(exe)],check=True)
        assert subprocess.run([str(exe),'--self-test'],capture_output=True,check=True).returncode==0
        runner=subprocess.run([str(exe),str(rom)],capture_output=True,text=True,check=True)
        room_output=subprocess.run([str(exe),'--room',str(rom)],capture_output=True,text=True,check=True).stdout.splitlines()
    rows=runner.stdout.splitlines()
    if len(rows)!=11743:raise ValueError(f'Expected 11740 instructions+final+IO+RAM, got {len(rows)}')
    def ramhash(ram):
        h=0xcbf29ce484222325
        for b in ram:
            h=((h^b)*0x100000001b3)&((1<<64)-1)
        return h
    original_bus=Bus(payload); c=CPU(original_bus);injected=False
    for i in range(11740):
        if c.pc==0xe04b and not injected:
            c.interrupt();injected=True
        expected=[i,c.pc,original_bus.bank,c.a,c.x,c.y,c.sp,c.p,len(original_bus.mappers),original_bus.status_polls,int(injected),ramhash(original_bus.mem[:2048])]
        actual=[int(s) for s in rows[i].split(',')]
        if actual!=expected:
            diff=[(k,a,b) for k,(a,b) in enumerate(zip(actual,expected)) if a!=b]
            raise ValueError(f'original/native first instruction difference step={i}, PC={c.pc:04X}, fields={diff}')
        c.step()
    if c.pc!=0xe04b or c.last_opcode!=0x40:raise ValueError('Original NMI failed to return')
    final=[11740,c.pc,original_bus.bank,c.a,c.x,c.y,c.sp,c.p,len(original_bus.mappers),original_bus.status_polls]
    actual=[int(v) for v in rows[-3].split(',')[1:]]
    if final!=actual:raise ValueError(f'final CPU difference: expected {final}, got {actual}')
    if not rows[-2].startswith('IO,'):raise ValueError('missing ordered IO events')
    io=[]
    for event in rows[-2][3:].split(';'):
        if event:
            addr,value=event.split(':');io.append([int(addr),int(value)])
    expected_io=[item[1:] for item in original_bus.events if item[0]=='io_write']
    if io!=expected_io:raise ValueError('ordered PPU/APU/MMIO writes differ')
    if rows[-1][:4]!='RAM,':raise ValueError('missing full RAM')
    ram=bytes.fromhex(rows[-1][4:])
    if ram!=bytes(original_bus.mem[:2048]):
        p=next(i for i,(a,b) in enumerate(zip(ram,original_bus.mem[:2048])) if a!=b)
        raise ValueError(f'full RAM mismatch at {p:04X}')
    from replay_room_loader_0540 import CPU as Room6502
    prg=payload[16:16+262144]
    if len(room_output)!=1280:raise ValueError('native room omitted a case')
    for idx in range(5):
        for seed in range(256):
            record=room_output[idx*256+seed].split(',')
            if len(record)!=13 or record[0]!='ROOM':raise ValueError('malformed native room output')
            initial=[int(x) for x in record[1:10]]
            original=Room6502(prg,idx,seed).run()
            expected=[idx,seed,original.a,original.x,original.y,0,original.sp,original.bank,len(original.mapper_writes)]
            if initial[:5]!=expected[:5] or initial[6:]!=expected[6:]:
                raise ValueError(f'original/native room CPU/mapper mismatch {idx}:{seed} {initial} vs {expected}')
            p=initial[5]
            if bool(p&1)!=original.c or bool(p&2)!=original.z or bool(p&128)!=original.n:
                raise ValueError(f'room flags mismatch {idx}:{seed}')
            original_reads=[(addr,value) for _,addr,_,value in original.read_0e]
            if int(record[10])!=len(original_reads):raise ValueError('mapped read count')
            mapped=[]
            for pair in record[11].split(';'):
                if pair:
                    addr,value=pair.split(':');mapped.append((int(addr),int(value)))
            if mapped!=original_reads:raise ValueError(f'mapped reads mismatch {idx}:{seed}')
            ram=bytes.fromhex(record[12])
            if ram!=bytes(original.ram):
                n=next(k for k,(v,w) in enumerate(zip(ram,original.ram)) if v!=w)
                raise ValueError(f'room 2KiB RAM mismatch {idx}:{seed} at {n:04X}')
    report={'schema':'JP0553-statically-compiled-reset-first-NMI-parity/v1',
        'original_sha256':SHA,'compiler':compiler,'native_instructions_checked':11740,
        'instruction_state_comparisons':11740,'all_cpu_registers_flags_and_mapper_state_matched':True,
        'full_2k_ram_matched':True,'every_instruction_2k_ram_digest_matched':True,
        'ordered_hardware_writes_matched':True,'unique_native_instruction_sites':verified_manifest['compiled_physical_instruction_sites'],
        'compiled_combined_instruction_sites':verified_manifest['compiled_physical_instruction_sites']+2357,
        'bounded_room_original_vs_combined_native_cases':1280,
        'bounded_room_full_ram_matched':True,
        'ram_sha256':hashlib.sha256(ram).hexdigest(),
        'original_gameplay_parity':False,'ppu_status_scripted':True,'first_nmi_injected':True,
        'strict_prg_new_bytes':0}
    if out:out.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS combined native fixed bank31+bank0A: 11740/11740 CPU-step states + 1280 room cases + 2KiB RAM',compiler)
    return report

def smoke(compiler='g++'):
    fixed=json.loads((NATIVE/'generated/boot_native_manifest.json').read_text())
    raw=json.loads((NATIVE/'../bank0a/generated/bank0a_native_manifest.json').read_text())
    if fixed['compiled_physical_instruction_sites']!=1904 or fixed['historically_verified_fixed31_sites']!=1564:
        raise ValueError('fixed native manifest drift')
    if raw['instruction_sites']!=2357 or raw['candidate_code_certified'] is not False:
        raise ValueError('bank0A evidence drift')
    with tempfile.TemporaryDirectory() as directory:
        exe=Path(directory)/'native'
        subprocess.run([compiler,'-std=c++20','-O2','-Wall','-Wextra','-Werror','-pedantic',
                        '-I'+str(NATIVE),str(NATIVE/'generated/boot_compiled.cpp'),
                        str(NATIVE/'../bank0a/generated/bank0a_compiled.cpp'),
                        str(NATIVE/'boot_native_driver.cpp'),'-o',str(exe)],check=True)
        subprocess.run([str(exe),'--self-test'],check=True)
        if subprocess.run([str(exe),str(Path(directory)/'missing_rom.nes')],capture_output=True).returncode==0:
            raise ValueError('missing ROM accepted')
        bogus=Path(directory)/'bogus.nes';bogus.write_bytes(b'NES\x1a')
        if subprocess.run([str(exe),str(bogus)],capture_output=True).returncode==0:
            raise ValueError('short ROM accepted')
    print('PASS native boot+room ROM-free compile; fail-closed unknown PC and missing/corrupt media',compiler)

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--smoke',action='store_true');p.add_argument('--compiler',default='g++');p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:smoke(a.compiler)
    if a.rom:run(a.rom,a.compiler,a.out)
    if not a.rom and not a.smoke:p.error('must specify --smoke or --rom')
if __name__=='__main__':main()
