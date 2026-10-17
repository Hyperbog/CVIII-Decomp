#!/usr/bin/env python3
"""Static NES preservation-archive publication/link audit (not semantics certification)."""
from __future__ import annotations
import argparse
import pathlib
import re
import sys

EXPECTED = [
"00_SCOPE_EVIDENCE_AND_SOURCE_BASELINE.md",
"01_CARTRIDGE_PRG_CHR_MAPPER.md",
"02_CPU_RESET_NMI_IRQ_DISPATCH.md",
"03_PPU_OAM_SPRITE_PIPELINE.md",
"04_OBJECT_SCHEDULER_COLLISION_SCRATCH.md",
"05_AI_SCRIPT_AND_ACTION_VM.md",
"06_ROOMS_STAGE_WORLD_STATE.md",
"07_AUDIO_STREAMS_VRC6_APU.md",
"08_NATIVE_RECOMP_AND_PARITY_CONTRACTS.md",
"09_DISCOVERY_ATLASES_AND_JP_US_MATCHING.md",
"10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md",
"11_PROGRAMMER_MODDER_REFERENCE.md",
"12_OPEN_RESEARCH_AND_CERTIFICATION_SCOPE.md",
]
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
def check(root: pathlib.Path) -> None:
    here=root / "JP" / "PreservationArchive"
    assert here.is_dir(), f"Missing {here}"
    actual=sorted(x.name for x in here.glob("[0-9][0-9]_*.md"))
    assert actual==EXPECTED, (actual,EXPECTED)
    files=[here/"README.md"] + [here/n for n in EXPECTED] + [here/"DISCOVERY_LOG.md"]
    link_count=0
    errors=[]
    for file in files:
        text=file.read_text(encoding="utf-8")
        assert text.startswith("# "),file
        assert len(text)>500,file
        if file.name!="README.md":
            assert "**Status:**" in text,file
        for target in re.findall(r"\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)",text):
            if target.startswith(("http:","https:","mailto:","#")):continue
            resolved=(file.parent / target.split("#",1)[0]).resolve()
            if not resolved.exists(): errors.append(f"{file.relative_to(root)}: broken {target}")
            link_count+=1
    assert not errors,"\n".join(errors)
    index=(here/"README.md").read_text(encoding="utf-8")
    for n in EXPECTED:
        assert f"({n})" in index, f"Not indexed: {n}"
    assert ROM_SHA in (here/"00_SCOPE_EVIDENCE_AND_SOURCE_BASELINE.md").read_text()
    assert "NO STATIC OR RUNTIME COMPLETION CERTIFICATE" in (here/"12_OPEN_RESEARCH_AND_CERTIFICATION_SCOPE.md").read_text()
    assert "C-001" in (here/"10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md").read_text()
    assert "(DISCOVERY_LOG.md)" in index, "Permanent discovery log missing from index"
    backlog=(here/"12_OPEN_RESEARCH_AND_CERTIFICATION_SCOPE.md").read_text(encoding="utf-8")
    for task in range(1,11):
        assert f"R-{task:03d}" in backlog, f"Missing stable research task R-{task:03d}"
    log=(here/"DISCOVERY_LOG.md").read_text(encoding="utf-8")
    assert "0507" in log and "49,404" in log, "Historical baseline missing"

    print(f"Archive structure PASS: {len(EXPECTED)} numbered chapters + README")
    print(f"Resolved {link_count} local Markdown references")
    print("This is a structure/link/identity policy audit, NOT a JP-ROM semantic, native runtime or hardware parity certificate.")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo-root",type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3])
    args=parser.parse_args()
    try:check(args.repo_root.resolve())
    except (AssertionError,OSError) as e:
        print("ARCHIVE AUDIT FAILURE:",e,file=sys.stderr);raise SystemExit(1)
