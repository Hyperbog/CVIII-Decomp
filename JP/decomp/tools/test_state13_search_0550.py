#!/usr/bin/env python3
"""ROM-free regression of authenticated Stage-1 Mesen fork search contracts.

Fixtures are synthetic on purpose. A positive synthetic event MUST NEVER
be reported as authentic original-JP gameplay evidence.
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path

from audit_mesen_state13_0549 import AuditError, scan
from search_mesen_state13_0550 import (
    FRAME_COUNTS, FORKS, FORK_FRAMES, BASE_NAMES,
    plan, validate_fork, assemble_report,
)
from test_mesen_state13_0549 import fixture


def must_reject(callback, description):
    try:
        callback()
    except (AuditError, ValueError):
        return
    raise AssertionError(f'accepted bad {description}')


def test():
    m=plan()
    assert m['provenance']=='PLAN_ONLY_NO_NEW_GAMEPLAY_EVIDENCE'
    assert m['total_emulated_frames_if_executed']==1100+len(FORKS)*1200
    assert m['cold_boot_frames']==1100
    assert len(FORKS)==5 and len(set(FORKS))==5
    with tempfile.TemporaryDirectory(prefix='jp0550-') as temp:
        root=Path(temp)
        segments=[]
        frame_start=1
        for name, frames in zip(BASE_NAMES,FRAME_COUNTS):
            path=root/(name+'.jsonl')
            path.write_text(fixture(frames=frames,start=frame_start),encoding='utf-8')
            result=scan(path)
            segments.append({'name':name,**result})
            frame_start+=frames
        assert frame_start==1101
        bootstrap={'total_frames':1100,'segments':segments}
        parent=root/'stage360.mss'
        parent.write_bytes(b'SYNTHETIC STATE FOR CONTRACT TEST ONLY')
        from hashlib import sha256
        parent_sha=sha256(parent.read_bytes()).hexdigest()
        paths=[]
        for name in FORKS:
            path=root/(name+'.jsonl')
            path.write_text(fixture(state13=name=='right_jump_1200',
                                    frames=1200,start=1101), encoding='utf-8')
            result=validate_fork(name,path,parent_final_frame=1101,
                                 parent_savestate_sha256=parent_sha,input_args=FORKS[name])
            assert result['frames']==1200 and result['start_frame']==1101
            paths.append((name,path))
        merged=assemble_report(bootstrap,parent,paths,original_hashes_verified=False)
        assert merged['number_of_forks']==5
        assert merged['total_emulator_frames_executed']==7100
        assert merged['longest_contiguous_input_route_frames']==2300
        assert merged['observation']=='UNAUTHENTICATED_FIXTURE_NO_GAMEPLAY_CLAIM'
        assert not merged['original_rom_sha256_authenticated']
        assert not merged['state13_e526_observed']
        assert merged['unauthenticated_test_hits_not_gameplay_evidence']==1
        assert merged['new_strict_prg_bytes']==0
        path=paths[0][1]
        must_reject(lambda:validate_fork('idle_1200',path,parent_final_frame=1200,
                                        parent_savestate_sha256=parent_sha,input_args=()),'parent frame')
        must_reject(lambda:validate_fork('idle_1200',path,parent_final_frame=1101,
                                        parent_savestate_sha256=parent_sha,input_args=('0:right@1-1200',)),
                    'input tamper')
        must_reject(lambda:validate_fork('forged_name',path,parent_final_frame=1101,
                                        parent_savestate_sha256=parent_sha,input_args=()),'route name')
        must_reject(lambda:validate_fork('idle_1200',path,parent_final_frame=1101,
                                        parent_savestate_sha256='notsha',input_args=()),'state identity')
        must_reject(lambda:assemble_report(bootstrap,parent,[paths[0],paths[0]],original_hashes_verified=False),
                    'duplicate fork')
        must_reject(lambda:assemble_report({'total_frames':1099,'segments':segments},parent,paths,
                                           original_hashes_verified=False),'bootstrap count')
        must_reject(lambda:assemble_report(bootstrap,root/'absent.mss',paths,
                                           original_hashes_verified=False),'absent savestate')
        altered=path.read_text().replace('"start_frame": 1101','"start_frame": 1102')
        path.write_text(altered)
        must_reject(lambda:validate_fork('idle_1200',path,parent_final_frame=1101,
                                        parent_savestate_sha256=parent_sha,input_args=()),'wrong fork start')
        path.write_text(fixture(frames=1199,start=1101))
        must_reject(lambda:validate_fork('idle_1200',path,parent_final_frame=1101,
                                        parent_savestate_sha256=parent_sha,input_args=()),'short fork')
        # A malformed CV0549 log line is not an ignorable unrelated log.
        path.write_text(fixture(frames=1200,start=1101).replace('CV0549 kind=frame','CV0549 broken=frame',1))
        must_reject(lambda:scan(path),'malformed observer event')
        path.write_text(fixture(frames=1200,start=1101).replace('frame=4 state=02','frame=0 state=02',1))
        must_reject(lambda:scan(path),'nonmonotonic event frames')
    print('PASS 0550 Mesen fork route plan: 5 distinct 1200-frame branches from one 1100-frame parent')
    print('PASS 0550 authenticated-only observation gate and 11 adversarial provenance checks')

if __name__=='__main__':test()
