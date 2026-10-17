# Decomp — original-source research and preservation

This directory contains the **partial semantic source reconstruction** of Japanese *Akumajou Densetsu*, not the running NESRecomp product.

| Directory | Contents |
| --- | --- |
| [src/](src/) and [asm/](asm/) | Original CPU, mapper and routine reconstruction |
| [analysis/](analysis/) | Evidence ledger, VPP/PRG state, technical analyses and checkpoint history |
| [tests/](tests/) and [tools/](tools/) | ROM-free regressions, original-ROM parity tools and audit scripts |
| [docs/](docs/) and [PreservationArchive/](PreservationArchive/) | Methodology, original technical findings and durable archival chapters |
| [SharedNES/](SharedNES/) | Shared Japanese/US NES source research |
| [legacy/](legacy/) | Preserved, non-product JP0509/0510 CPU, actor and SDL prototype experiments |
| [workstreams/](workstreams/) | Independent semantic research status, ownership rules and evidence |

The earlier `JP/recomp/*.asm` fragments now live in [asm/](asm/). The superseded `native0509`, `standalone0509` and `native_demo0510` directories are preserved in [legacy/](legacy/) rather than deleted.

**Research score:** [31/100 semantic VPP](docs/PROGRESS_METRIC.md) and [49,504/262,144 strict certified PRG bytes](analysis/RESUME_STATE.json). Neither score measures the progress of the independently [playable native game](../recomp/).

Run `python3 JP/decomp/tools/audit_native_evidence_ledger.py`, `python3 JP/decomp/tools/audit_workstreams.py` and `bash JP/decomp/tools/run_native_regressions.sh` from the repository root for the applicable ROM-free research gates.
