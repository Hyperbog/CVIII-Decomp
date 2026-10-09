#!/usr/bin/env python3
"""Summarize captured original-ROM IRQ/NMI experiments; deterministic raw JSON hashes."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
labels=[('start30',480),('none',240),('abstart',240)]
sc=[]
for policy,frames in labels:
    fname=f'0508_irq_frames_{policy}_{frames}.json'
    payload=(D/fname).read_bytes()
    d=json.loads(payload)
    assert d['frames_completed']==frames
    assert d['irq_entries']==d['irq_returns']
    assert d['irq_ack_writes']==d['irq_returns']
    assert all(v['vector']==0xE0F5 for v in d['irq_entry_log'])
    assert d['nmi_entries']-d['nmi_returns']==1
    a=json.loads((D/('0508_cycle_vblank_480_report.json' if policy=='start30' else '0508_cycle_vblank_batch_summary.json')).read_text())
    if policy=='start30':baseline={'instructions':a['CPU_steps'],'NMIs':a['natural_NMI_entries'],'18_values':sorted({v['18'] for v in a['RAM_state_changes']})}
    else:baseline=next(s for s in a['scenarios'] if s['policy']==policy)
    state_values=sorted({v['18'] for v in d['observed_state_transitions']})
    assert state_values==baseline['18_values'],(policy,state_values,baseline)
    assert d['nmi_entries']==baseline['NMIs']
    sc.append({'policy':policy,'frames':frames,'cpu_instructions':d['cpu_steps'],
        'nmi':d['nmi_entries'],'irq_entries':d['irq_entries'],'irq_returns':d['irq_returns'],
        'irq_source_assertions':d['mapper_irq_assertions'],
        'irq_latch_writes':d['irq_latch_writes'],'irq_control_writes':d['irq_control_writes'],'irq_ack_writes':d['irq_ack_writes'],
        'selector_18_observed':state_values,
        'prior_no_irq_instructions':baseline['instructions'],
        'instruction_delta_vs_no_irq':d['cpu_steps']-baseline['instructions'],
        'prior_no_irq_nmi':baseline['NMIs'],
        'raw_report':fname,'raw_report_sha256':hashlib.sha256(payload).hexdigest(),
        'final':d['end']})
comp=json.loads((D/'0508_vrc6_irq_component_report.json').read_text())
assert comp['tests_passed']==267
out={'status':'BOUNDED_EXPERIMENTAL_IRQ_CPU_PPU_NOT_REFERENCE_PARITY',
    'source_rom_sha256':comp['rom_sha256'],
    'component_regression_checks':267,
    'scenarios':sc,
    'totals':{'frames':sum(x['frames'] for x in sc),'cpu_instructions':sum(x['cpu_instructions'] for x in sc),
              'nmi':sum(x['nmi'] for x in sc),'irq_entries':sum(x['irq_entries'] for x in sc),
              'irq_returns':sum(x['irq_returns'] for x in sc)},
    'new_strict_prg_bytes':0,'strict_prg_total':49404,'vpp':24,
    'limitations':['No reference console/emulator parity', 'CPU interrupt sampled only at instruction boundaries',
       'PPU vblank and DMA approximated', 'No cycle-positioned mapper register writes or APU/DMC timing',
       'Observed selector states do not prove full-game reachability or global absent paths']}
assert out['totals']=={'frames':960,'cpu_instructions':8861056,'nmi':948,'irq_entries':350,'irq_returns':350},out['totals']
path=D/'0508_vrc6_irq_batch_summary.json'
path.write_text(json.dumps(out,indent=2)+'\n')
print('PASS',out['totals'])
