#!/usr/bin/env python3
"""JP0663 complete root-level workstream migration.

Runs on a *temporary staging checkout*, never deletes historical source,
never includes the original ROM. Physically moves every JP root folder under
JP/decomp or JP/recomp; rewrites repo-root references and Markdown links.
Only push after CI gates pass; original branch remains a stable rollback.
"""
from __future__ import annotations
import os
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
JP = ROOT / 'JP'
PRODUCT_TOOLS = (
    'patch_cyc_', 'build_retail_cycle_', 'package_alpha_builder_',
    'test_alpha_', 'test_control_profiles_', 'jp_asset_pack_',
    'jp_asset_runtime_', 'validate_cycle_media_', 'jp_menu_',
    'jp_audio_session_verify_', 'jp_audio_bus_report_', 'jp_object_oam_report_',
    'jp_chr_fetch_report_', 'jp_frame_evidence_report_', 'jp_nt_trace_report_',
    'jp_sound_session_', 'jp_sprite_frame_', 'jp_sdl_',
)
PRODUCT_DOCS = {
    'ENHANCED_CURRENT_STATUS.md', 'RELEASE_MILESTONES.md',
    'ORIGINAL_ENHANCED_EDITIONS.md', 'ALPHA_OWNER_HANDOFF.md',
    'ORIGINAL_ENHANCED_PARITY.md', 'ENHANCED_MODDING_ARCHITECTURE.md',
}
DECOMP_DIRS = {'PreservationArchive', 'SharedNES', 'analysis',
               'docs', 'src', 'tests', 'tools', 'workstreams'}
RECOMP_DIRS = {'native', 'release', 'scenarios'}
TEXT_EXT = {'.py', '.sh', '.bash', '.ps1', '.bat', '.cmd', '.md',
            '.txt', '.json', '.csv', '.yml', '.yaml', '.cmake',
            '.c', '.h', '.cpp', '.hpp', '.asm', '.lua', '.ini',
            '.toml', '.xml', '.cfg', '.gitattributes', '.gitignore'}
LINK = re.compile(r'(\]\()([^\s\)]+)(\))')
JPREF = re.compile(r'(?<![A-Za-z0-9_])JP/(?!decomp/|recomp/)([-A-Za-z0-9_./]+)')
PARENTS = re.compile(r'\.parents\[(\d+)\]')


def dest(path: str) -> str:
    if not path.startswith('JP/'):
        return path
    part=PurePosixPath(path).parts
    if len(part)<2 or part[1] in ('decomp', 'recomp') or path=='JP/README.md':
        return path
    group=part[1]
    if group in RECOMP_DIRS:
        return 'JP/recomp/'+'/'.join(part[1:])
    if group=='tools':
        name=part[2] if len(part)>2 else ''
        wing='recomp' if name.startswith(PRODUCT_TOOLS) else 'decomp'
        return 'JP/'+wing+'/'+ '/'.join(part[1:])
    if group=='docs':
        name=part[2] if len(part)>2 else ''
        wing='recomp' if name in PRODUCT_DOCS else 'decomp'
        return 'JP/'+wing+'/'+ '/'.join(part[1:])
    if group=='workstreams':
        wing='recomp' if len(part)>2 and part[2]=='native-recompilation' else 'decomp'
        return 'JP/'+wing+'/'+ '/'.join(part[1:])
    if group in DECOMP_DIRS:
        return 'JP/decomp/' + '/'.join(part[1:])
    raise ValueError(f'Unclassified Japanese tree path: {path}')


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,check=True,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).stdout


def relative_markdown(old_path: str,new_path: str,text: str) -> str:
    def fix(m):
        old=m.group(2)
        if old.startswith(('#','https://','http://','mailto:','data:','sandbox:')):
            return m.group(0)
        raw,sep,fragment=old.partition('#')
        if not raw or raw.startswith('/'):
            return m.group(0)
        try:
            orig=os.path.normpath(os.path.join(os.path.dirname(old_path),raw)).replace('\\','/')
            mapped=dest(orig) if orig.startswith('JP/') else orig
            newrel=os.path.relpath(mapped,os.path.dirname(new_path)).replace('\\','/')
        except (ValueError,OSError):
            return m.group(0)
        if raw.endswith('/') and not newrel.endswith('/'):
            newrel+='/'
        return m.group(1)+newrel+(sep+fragment if sep else '')+m.group(3)
    return LINK.sub(fix,text)


def substitute_references(text: str) -> str:
    def repl(m):
        original='JP/'+m.group(1)
        # Some calls use JP/tools/ as a bare directory.
        if original.endswith('/'):
            return 'JP/decomp/tools/'
        try:
            return dest(original)
        except ValueError:
            # Prose may contain JP/<game title>, not a repository path.
            return m.group(0)
    return JPREF.sub(repl,text)


def fix_cmake(new_path: str,text: str) -> str:
    if new_path.endswith('/native0509/CMakeLists.txt') or new_path.endswith('/standalone0509/CMakeLists.txt'):
        for part in ('src','tests','tools'):
            text=text.replace('../../../'+part,'../../'+part)
    if new_path=='JP/recomp/native/nesrecomp_cycle/CMakeLists.txt':
        # Its former ../../tools resolves to JP/recomp/tools after the move.
        pass
    return text


def fix_python(old_path: str,new_path: str,text: str) -> str:
    # Paths gain one directory level. In original tools and tests, parent
    # index 2 used to mean repository root; change to 3. A parent-index 1
    # originally meant JP; after the move it means the workstream root and
    # remains correct for source-local data/tools.
    if old_path.startswith(('JP/tools/','JP/tests/','JP/src/','JP/analysis/',
                            'JP/SharedNES/','JP/PreservationArchive/','JP/docs/',
                            'JP/release/','JP/workstreams/','JP/scenarios/')):
        text=PARENTS.sub(lambda m: '.parents['+str(int(m.group(1))+1)+']'
                         if int(m.group(1))>=2 else m.group(0),text)
    if new_path=='JP/decomp/tools/run_native_regressions.sh':
        text=text.replace('")/../.." && pwd)', '")/../../.." && pwd)')
    if old_path=='JP/tools/audit_workstreams.py':
        text=text.replace('f"JP/workstreams/{name.replace(\'_\',\'-\')}/"',
                          'f"JP/{\'recomp\' if name == \'native_recompilation\' else \'decomp\'}/workstreams/{name.replace(\'_\',\'-\')}/"')
    if old_path=='JP/tools/audit_folder_consolidation_0662.py':
        text=text.replace("sorted(p.name for p in (root/'JP/recomp').iterdir()) == ['README.md']",
                          "set(p.name for p in (root/'JP/recomp').iterdir()) >= {'README.md','native','release','tools'}")
    return text


def migrate():
    tracked=git('ls-files','-z').split('\0')
    originals=[p for p in tracked if p]
    jp_sources=[p for p in originals if p.startswith('JP/')]
    target={p:dest(p) for p in originals}
    assert len({target[p] for p in originals})==len(originals), 'Destination path collision'
    moves=[(p,target[p]) for p in jp_sources if p!=target[p]]
    for old,new in moves:
        output=ROOT/new
        output.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','mv','--',old,new],cwd=ROOT,check=True,
                       stdout=subprocess.DEVNULL)
    # Transform all tracked text sources, including workflow path filters
    # and historical notes. Binary/compressed files must stay identical.
    rewritten=0
    for old in originals:
        new=target[old]
        file=ROOT/new
        if not file.is_file() or file.is_symlink():
            continue
        if (file.suffix.lower() not in TEXT_EXT and
            file.name not in ('CMakeLists.txt','Makefile','Dockerfile')):
            continue
        raw=file.read_bytes()
        if len(raw)>2_000_000 or b'\0' in raw:
            continue
        try:
            s=raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        n=relative_markdown(old,new,s) if file.suffix.lower()=='.md' else s
        n=substitute_references(n)
        if file.suffix.lower() in ('.py','.sh'):
            n=fix_python(old,new,n)
        if file.suffix.lower()=='.ps1':
            # Build-Alpha computes project checkout root from a user argument,
            # so its rewritten JP/recomp paths remain repo-relative.
            pass
        n=fix_cmake(new,n)
        if n!=s:
            file.write_bytes(n.encode('utf-8'))
            rewritten+=1

    # Ensure the two workstream landing pages make the migration clear.
    root_readme=JP/'README.md'
    current=root_readme.read_text(encoding='utf-8')
    current=current.replace('**The physical migration is not yet complete:**',
                            '**JP0663 root-level physical migration is complete.**')
    root_readme.write_text(current,encoding='utf-8')
    # git mv removes files, not every now-empty nested directory on the
    # runner filesystem. Refuse to delete any surviving file, then prune.
    for name in sorted(DECOMP_DIRS | RECOMP_DIRS):
        legacy=JP/name
        if legacy.exists():
            leftover=[str(p) for p in legacy.rglob('*') if p.is_file() or p.is_symlink()]
            assert not leftover, ('Unmigrated original files',name,leftover[:8])
            shutil.rmtree(legacy)
    dirs={p.name for p in JP.iterdir() if p.is_dir()}
    assert dirs=={'decomp','recomp'}, ('Unexpected JP root directories',sorted(dirs))
    assert (JP/'recomp/native/nesrecomp_cycle/CMakeLists.txt').is_file()
    assert (JP/'recomp/release/alpha/Build-Alpha.ps1').is_file()
    assert (JP/'decomp/analysis/RESUME_STATE.json').is_file()
    assert (JP/'decomp/analysis/PROGRESS_SCORE.csv').is_file()
    assert (JP/'decomp/src/cpu_2a03.cpp').is_file()
    print(f'JP0663 moved {len(moves)} tracked JP files, revised {rewritten} text files')
    print('JP root clean:',sorted(dirs))
    git('add','-A')
    print(git('status','--short').splitlines()[:20])


if __name__=='__main__':
    migrate()
