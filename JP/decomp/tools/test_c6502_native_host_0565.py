#!/usr/bin/env python3
"""0565 StarFox-style C-only linked host smoke without original ROM media."""
from __future__ import annotations
import argparse,shutil,subprocess,tempfile
from pathlib import Path
from static_recompile_c_0562 import generate as bank_generate
from static_recompile_boot_c_0564 import generate as fixed_generate

ROOT=Path(__file__).resolve().parents[3]
C=ROOT/'JP/recomp/native/c6502'

def smoke(cc):
 if not shutil.which(cc):raise ValueError('no C11 compiler found')
 with tempfile.TemporaryDirectory(prefix='jp-c6502-host-') as temp:
  w=Path(temp)
  bank=bank_generate([
   dict(pc=0x8000,category='audited',opcode=0xa9,arg=0x0012,next=0x8002),
   dict(pc=0x8002,category='candidate',opcode=0x60,arg=0,next=0x8003)
  ])
  fixed=fixed_generate([
   dict(physical=31*8192,pc=0xe000,opcode=0xa9,arg=3,
        next=0xe002,evidence='HISTORICALLY_VERIFIED'),
   dict(physical=31*8192+2,pc=0xe002,opcode=0x85,arg=0x10,
        next=0xe004,evidence='TRACE_EXECUTED')
  ])
  (w/'bank0a_compiled.c').write_text(bank)
  (w/'boot_compiled.c').write_text(fixed)
  exe=w/'jp_c6502'
  subprocess.run([cc,'-std=c11','-O1','-Wall','-Wextra','-Werror',
      '-pedantic','-I'+str(C),str(C/'cpu.c'),str(C/'opcode_table.c'),
      str(C/'main.c'),str(w/'boot_compiled.c'),str(w/'bank0a_compiled.c'),
      '-o',str(exe)],check=True)
  data=bytearray(393232)
  data[:4]=b'NES\x1a'
  # $FFFC reset vector -> fixed31:$E000, host fixture executes
  # LDA #3; STA $10 and then fails at missing $E004.
  vec=16+31*8192+0x1ffc
  data[vec:vec+2]=(0xe000).to_bytes(2,'little')
  rom=w/'fixture.nes';rom.write_bytes(data)
  def run(*opts):
   return subprocess.run([str(exe),str(rom),*opts],
                         capture_output=True,text=True)
  result=run('--test-media','--steps','2')
  if result.returncode!=0 or 'STATUS=BOUNDED step=2 pc=E004' not in result.stdout or (
      'compiled=2 interpreted=0 ram10=03' not in result.stdout):
   raise AssertionError('linked native C host bounded smoke: '+repr(result))
  result=run('--test-media','--steps','3')
  if result.returncode==0 or 'STATUS=HALTED' not in result.stdout:
   raise AssertionError('unresolved native C host instruction not fail-closed')
  result=run('--steps','2')
  if result.returncode==0 or 'CRC32 differs' not in result.stderr:
   raise AssertionError('regular host accepted synthetic unverified ROM')
  result=run('--test-media','--steps','0')
  if result.returncode==0:raise AssertionError('zero-step runtime not bounded')
  print('PASS C-only linked native host, physical fixed31 code, bounded execution, '
        'missing-PC gate, cartridge CRC gate')

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--smoke',action='store_true')
 p.add_argument('--cc',default='cc')
 a=p.parse_args()
 if not a.smoke:p.error('--smoke required')
 smoke(a.cc)
