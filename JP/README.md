# Japanese Castlevania III — two source workstreams

The Japanese *Akumajou Densetsu* project uses **two top-level directories**. All original game assets remain owner-supplied; no commercial ROM is checked in.

| Workstream | Purpose | Main entry |
| --- | --- | --- |
| **[decomp/](decomp/)** | Original 6502 routine recovery, evidence, research, preservation and historical native prototypes | [Semantic research](decomp/workstreams/semantic-decompilation/README.md) |
| **[recomp/](recomp/)** | Already-functioning NESRecomp C11/SDL2 native game, Enhanced Edition, build and release tooling, input, saves and QA | [Native product](recomp/workstreams/native-recompilation/README.md) |

The JP0663 migration **physically separated the entire old JP root**, retained historical files and updated build/CI references. There are no additional top-level JP source directories. Research helpers in `recomp/native/enhanced/` may remain compiled but dormant; their original-source parity is tracked separately from the live game's feature status.

## Native playable game

Use [recomp/release/alpha/](recomp/release/alpha/) for the ROM-free Windows build kit, [recomp/native/nesrecomp_cycle/](recomp/native/nesrecomp_cycle/) for the pinned external NESRecomp integration, and [current product status](recomp/docs/ENHANCED_CURRENT_STATUS.md) for owner-tested features. The original Japanese cartridge must be privately supplied with the expected fingerprint.

## Semantic decompilation

Use [decomp/docs/PROGRESS_METRIC.md](decomp/docs/PROGRESS_METRIC.md) for the independent **31/100 VPP** source-recovery score and [decomp/analysis/RESUME_STATE.json](decomp/analysis/RESUME_STATE.json) for the certified **49,504/262,144 PRG-byte** evidence floor. **Neither number measures native-game playability.** Historical 6502 assembly is in [decomp/asm/](decomp/asm/) and old 0509/0510 CPU and actor experiments are under [decomp/legacy/](decomp/legacy/).

The [ownership manifest](decomp/workstreams/WORKSTREAMS.json), [ROM-free boundary audit](decomp/tools/audit_workstreams.py), [preservation chapters](decomp/PreservationArchive/), and [root contributor policy](../AGENTS.md) apply to the respective workstreams. Original gameplay remains the default reference; experimental presentation and modding are opt-in and separate from semantic certification.
