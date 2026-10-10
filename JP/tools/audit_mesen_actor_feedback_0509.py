#!/usr/bin/env python3
"""Original-JP Mesen feedback matrix for live actor event producers.

Boots the immutable Japanese ROM normally and forks controller-only policies
from one authentic frame-aligned stage checkpoint. Does NOT change CPU/RAM/PC.
Collects physical-PRG-qualified execution and RAM-write witnesses through the
external Mesen2 debugger. All savestates/CDL/logs are private temporary data.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from audit_mesen_actor_live_0509 import ROM_SHA, file_sha, run

EXPECTED_AGENT='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
EXPECTED_CORE='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
BRANCH_FRAMES=640
# No mutation API is called. Separate instruction callbacks are filtered by
# emulator *physical* mapping, not only the game's tracked bank RAM[$23].
OBSERVER=r'''
local frame=0
local ramType=emu.memType.nesInternalRam
local count={}
local seen={}
local physicalBase=0x0A*0x4000
local function ram(a) return emu.read(a,ramType) end
local function origin() local s=emu.getState();return s['cpu.pc'],s['cpu.x'] end
local function phys(pc) return emu.convertAddress(pc,emu.memType.nesMemory).address end
local function inRaw(pc)
  return pc>=0x8000 and pc<0xC000 and phys(pc)==physicalBase+(pc-0x8000)
end
local writes={0x07C2,0x07CD,0x054F,0x055A,0x07E0,0x07E5}
local function writer(group,a,v)
  local pc,x=origin()
  if not inRaw(pc) then return end
  local k=string.format('%s/%04X/%04X/%02X',group,a,pc,v)
  count[k]=(count[k] or 0)+1
  if not seen[k] then
    seen[k]=true
    emu.log(string.format('WRITE f=%d group=%s addr=%04X value=%02X pc=%04X phys=%06X x=%d',frame,group,a,v,pc,phys(pc),x))
  end
end
emu.addMemoryCallback(function(a,v) writer('row',a,v) end,emu.callbackType.write,0x07C2,0x07CD)
emu.addMemoryCallback(function(a,v) writer('actor',a,v) end,emu.callbackType.write,0x054F,0x055A)
emu.addMemoryCallback(function(a,v) writer('high',a,v) end,emu.callbackType.write,0x07E0,0x07E5)
local pcs={0x8143,0x8157,0x8182,0x84F3,0x8501,0x8520,0x8B2C,0x8B71,0x85DD,0x8D90,0xFF06,0xFF24,0x90C5,0x90DF,0x9133}
for _,pc in ipairs(pcs) do
 emu.addMemoryCallback(function()
  if pc<0xE000 and not inRaw(pc) then return end
  local k=string.format('%04X',pc)
  count[k]=(count[k] or 0)+1
  if count[k]<=3 or (pc==0x8501 and count[k]<=6) then
    local _,x=origin()
    emu.log(string.format('EXEC f=%d pc=%04X phys=%06X x=%d row=%02X sub=%02X',frame,pc,phys(pc),x,ram(0x07C2+x),ram(0x07C8+x)))
  end
 end,emu.callbackType.exec,pc)
end
emu.addEventCallback(function()
  frame=frame+1
  if frame==640 then
    local slots={}
    for i=1,12 do slots[#slots+1]=string.format('%02X',ram(0x054E+i)) end
    emu.log('FINAL frame=640 slots='..table.concat(slots,','))
  end
end,emu.eventType.endFrame)
'''

EXEC_RE=re.compile(r'^EXEC f=(\d+) pc=([0-9A-F]{4}) phys=([0-9A-F]{6}) x=(\d+) row=([0-9A-F]{2}) sub=([0-9A-F]{2})$')
WRITE_RE=re.compile(r'^WRITE f=(\d+) group=(\w+) addr=([0-9A-F]{4}) value=([0-9A-F]{2}) pc=([0-9A-F]{4}) phys=([0-9A-F]{6}) x=(\d+)$')


def policy(name):
    o=[]
    def key(button,a,b):
        assert 0<=a<=b<BRANCH_FRAMES,(name,button,a,b)
        o.extend(['--input',f'0:{button}@{a}-{b}'])
    if name=='idle': pass
    elif name=='right':key('right',0,639)
    elif name=='left':key('left',0,639)
    elif name=='right_whips':
        key('right',0,639)
        for f in range(0,640,37):
            if f+5<640:key('b',f+5,min(f+8,639))
    elif name=='right_jumps':
        key('right',0,639)
        for f in range(0,640,43):
            if f+4<640:key('a',f+4,min(f+9,639))
        for f in range(0,640,107):
            if f+34<640:key('up',f+34,min(f+65,639))
    elif name=='right_ab':
        key('right',0,639)
        for f in range(0,640,47):
            if f+2<640:key('a,b',f+2,min(f+7,639))
    elif name=='up_right':
        key('right,up',0,639)
        for f in range(0,640,41):
            if f+2<640:key('a',f+2,min(f+7,639))
    else: raise ValueError(name)
    return o


def parse_capture(log):
    source=[];writes=[];final=None
    for line in log.splitlines():
        m=EXEC_RE.fullmatch(line)
        if m:
            f,pc,phys,x,row,sub=m.groups()
            source.append({'relative_frame':int(f),'cpu_pc':pc,'prg_offset':phys,
                           'object_x':int(x),'row':row,'event':sub})
        m=WRITE_RE.fullmatch(line)
        if m:
            f,group,addr,value,pc,phys,x=m.groups()
            writes.append({'relative_frame':int(f),'group':group,'ram':addr,
                           'value':value,'cpu_pc':pc,'prg_offset':phys,'x':int(x)})
        if line.startswith('FINAL frame=640 slots='):final=line.rsplit('=',1)[-1].split(',')
    if final is None:raise ValueError('Observer did not complete 640 original emulator frames')
    return source,writes,final


def audit(mesen,rom,private_anchor=None,only=None):
    if file_sha(rom)!=ROM_SHA:raise ValueError('Expected original Japanese ROM SHA mismatch')
    if file_sha(mesen)!=EXPECTED_AGENT or file_sha(mesen.parent/'MesenCore.so')!=EXPECTED_CORE:
        raise ValueError('External Mesen2 agent/core SHA changed; requalify first')
    with tempfile.TemporaryDirectory(prefix='jp_mesen_feedback_0509_') as tmp:
        root=Path(tmp)
        observer=root/'actor_observer.lua';observer.write_text(OBSERVER)
        if private_anchor:
            shutil.copyfile(private_anchor,root/'stage.mss')
            _,anchor=run(mesen,rom,root,'check-anchor',[
                '--load-state',str(root/'stage.mss'),'--frames','0','--timeout','15'])
            if anchor['final_frame'] != 2603:
                raise AssertionError('Supplied private state is not at verified frame 2603')
        else:
            phase0=['--frames','1502','--timeout','70']
            for f in (50,170,270,370):phase0+=['--input',f'0:start@{f}-{f+4}']
            phase0+=['--input','0:right@780-1501','--input','0:a@820-1501',
                     '--save-state',str(root/'boot.mss')]
            _,boot=run(mesen,rom,root,'boot',phase0)
            if (boot['reason'],boot['final_frame'])!=('frame_limit',1503):raise AssertionError('Boot frame anchor mismatch')
            phase1=['--load-state',str(root/'boot.mss'),'--frames','1100','--timeout','70',
                    '--input','0:right@0-1099','--input','0:a@0-1099',
                    '--save-state',str(root/'stage.mss')]
            _,stage=run(mesen,rom,root,'stage',phase1)
            if (stage['reason'],stage['final_frame'])!=('frame_limit',2603):raise AssertionError('Stage frame anchor mismatch')
        result=[]
        expected={'idle':None,'right':None,'left':None,'right_whips':None,
                  'right_jumps':489,'right_ab':491,'up_right':485}
        for name,first_frame in expected.items():
            if only is not None and name not in only: continue
            opts=['--load-state',str(root/'stage.mss'),'--frames','640',
                  '--timeout','55','--lua',str(observer)]+policy(name)
            events,summary=run(mesen,rom,root,name,opts)
            if (summary['reason'],summary['frames_executed'])!=('frame_limit',640):
                raise AssertionError(f'Unexpected Mesen fork stop {name}: {summary}')
            lua=[x['text'] for x in events if x.get('event')=='lua_log']
            if len(lua)!=1:raise AssertionError(f'Missing observer output {name}')
            source,writes,slots=parse_capture(lua[0])
            live=[x for x in source if x['cpu_pc']=='8B2C']
            found=min((x['relative_frame'] for x in live),default=None)
            if found!=first_frame:
                raise AssertionError(f'Observed first live actor event {name}: {found} not {first_frame}')
            if first_frame is not None:
                assert len(live)==2,(name,live)
                assert [x['object_x'] for x in live]==[3,4]
                assert [x['row'] for x in live]==['32','32']
                assert [x['value'] for x in writes if x['cpu_pc']=='8D90' and x['group']=='actor']==['3D','3D']
                assert any(x['cpu_pc']=='8143' and x['ram']=='07C5' and x['value']=='32' for x in writes)
                assert any(x['cpu_pc']=='8157' and x['ram']=='07E3' and x['value']=='00' for x in writes)
                assert any(x['cpu_pc']=='85DD' and x['ram']=='07CB' and x['value']=='11' for x in writes)
                assert slots[0:2]==['3D','3D']
            else:
                assert not any(x['cpu_pc'] in ('84F3','8B2C') for x in source)
            if any(x['cpu_pc'] in ('90C5','90DF','9133') for x in source):
                raise AssertionError('Unexpected earlier synthetic-only handler became live; review separately')
            result.append({'policy':name,'frames':640,'first_live_handler_frame':found,
                           'source_instructions_sampled':source,'distinct_ram_writer_witnesses':writes,
                           'actor_slot_types_1_12':slots,
                           'observer_sha256':hashlib.sha256(lua[0].encode()).hexdigest()})
        return {'schema':'JP-0509-independent-Mesen-agentic-feedback/v1',
                'rom_sha256':ROM_SHA,'mesen_agent_sha256':EXPECTED_AGENT,'mesen_core_sha256':EXPECTED_CORE,
                'start_from_clean_rom':private_anchor is None,'natural_frame_checkpoint':2603,
                'policy_count':len(result),'frames_per_policy':640,
                'total_fork_frames':len(result)*640,'policy_results':result,
                'private_anchor_state_sha256':file_sha(private_anchor) if private_anchor else None,
                'limitations':'bounded natural-controller routes only; no original game input/row global proof; zero PRG/VPP credit; savestates private',
                'new_strict_prg_bytes':0,'new_vpp_points':0}



def merge_reports(files):
    expected=('idle','right','left','right_whips','right_jumps','right_ab','up_right')
    observed={}; anchor=None
    for path in files:
        report=json.loads(path.read_text())
        if report['schema']!='JP-0509-independent-Mesen-agentic-feedback/v1' or report['rom_sha256']!=ROM_SHA:
            raise ValueError(f'Unexpected original source identity in {path}')
        if report['policy_count']!=len(report['policy_results']) or report['frames_per_policy']!=640:
            raise ValueError(f'Unfinished feedback policy in {path}')
        sha=report['private_anchor_state_sha256']
        if not sha or (anchor is not None and sha!=anchor):
            raise ValueError('Independent policies do not share the same validated source-state anchor')
        anchor=sha
        for row in report['policy_results']:
            name=row['policy']
            if name not in expected or name in observed:raise ValueError(f'Duplicate/invalid actor route {name}')
            observed[name]=row
    if set(observed)!=set(expected):
        raise ValueError(f'Missing feedback policies: {sorted(set(expected)-set(observed))}')
    result=[]
    for name in expected:
        row=observed[name]
        writes=row['distinct_ram_writer_witnesses']
        first=row['first_live_handler_frame']
        # Retain compact source-qualifying facts without exporting a lossless
        # instruction trace, Mesen savestate, raw memory or original-ROM bytes.
        wanted=('8143','8157','8182','8B71','85DD','8D90')
        source=[{'pc':pc,'physical_prg_offset':f'{0x0A*16384+int(pc,16)-0x8000:06X}'}
                for pc in wanted if any(w['cpu_pc']==pc for w in writes)]
        actor_writes=[{'ram':w['ram'],'value':w['value'],'pc':w['cpu_pc'],
                       'prg_offset':w['prg_offset']}
                      for w in writes if w['group']=='actor' and w['value']=='3D']
        result.append({'policy':name,'original_frames_executed':640,
                       'first_live_handler_frame_absolute':2603+first if first is not None else None,
                       'first_live_handler_frame_relative':first,
                       'handler_8B2C_exec_occurrences':sum(s['cpu_pc']=='8B2C' for s in row['source_instructions_sampled']),
                       'actor_type3D_stores':actor_writes,
                       'live_event_writer_pcs':source,
                       'branch_observer_sha256':row['observer_sha256']})
    digest=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'JP-0509-Mesen-multi-policy-live-actor-feedback-merged/v1',
            'rom_sha256':ROM_SHA,'mesen_agent_sha256':EXPECTED_AGENT,'mesen_core_sha256':EXPECTED_CORE,
            'source':'seven independently completed Mesen2 runs from independently clean-boot-verified frame 2603 savestate',
            'private_anchor_sha256':anchor,'no_ram_or_pc_injection':True,
            'policy_count':len(result),'branch_frames_each':640,'total_branch_frames':640*len(result),
            'policy_results':result,'result_digest_sha256':digest,
            'remaining':'real other event rows 08/09/0A spawn handlers, full game-frame parity, strict PRG manifest overlap',
            'new_strict_prg_bytes':0,'new_vpp_points':0}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_jp_rom',type=Path,nargs='?')
    p.add_argument('--mesen-agent',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--private-anchor',type=Path,help='Trusted previously clean-booted frame-2603 state (private; labels scope)')
    p.add_argument('--policies',nargs='+',help='Subset of seven predefined policies')
    p.add_argument('--merge-reports',nargs='+',type=Path,help='Validate and merge independently completed, private-state scenario reports')
    a=p.parse_args()
    if a.merge_reports:
        result=merge_reports(a.merge_reports)
        print('PASS Mesen feedback merge:',result['policy_count'],'physically authenticated controller forks')
    else:
        if not a.mesen_agent or not a.original_jp_rom:
            p.error('original_jp_rom and --mesen-agent required to run emulator')
        result=audit(a.mesen_agent.resolve(),a.original_jp_rom.resolve(),a.private_anchor,a.policies)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
    if not a.merge_reports:
        print('PASS Mesen2 original-JP actor feedback:',result['policy_count'],
              'input branches',result['total_fork_frames'],'forked live emulator frames')

if __name__=='__main__':main()
