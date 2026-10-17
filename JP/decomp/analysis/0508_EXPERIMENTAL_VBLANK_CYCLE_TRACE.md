# Checkpoint 0508 — Experimental CPU-cycle/vblank scheduling and multiscenario ROM trace

**Status: PROVISIONAL, not hardware/reference-emulator parity, complete NES gameplay, or a strict PRG/VPP promotion.** Immutable JP ROM: SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, mapper 24/VRC6a. This is an experimental execution infrastructure deliverable, not a completed checkpoint.

## Why this is an improvement

The prior 0508 scans manually injected NMI at artificial instants. `JP/decomp/tools/trace_cycle_vblank_0508.py` instead executes the actual ROM instructions using the tested 2A03/VRC6 mapped bus; accounts for nominal official 6502 opcode cycles with branch and indexed-read page-cross penalties; models NTSC 341×262 PPU dot frames at three dots per CPU cycle, PPUSTATUS vblank clear-on-read, PPUCTRL NMI enable and vblank NMI rising edges, and an approximate OAMDMA stall. Actual NMI instructions are executed from the original vector on modeled vblank events. Input bit patterns depend on modeled PPU frame indices, not artificially injected NMIs.

`JP/decomp/tools/test_cycle_vblank_0508.py` passed **all 151 official 6502 opcode cycle classes**, **27 representative opcode cycle values**, PPU vblank timing, PPUSTATUS clear, enabling NMI during active vblank, approximate DMA queue and real-ROM NMI stack-vector entry. This is a **model self-consistency audit**, not independent hardware cycle certification.

## Reproduced ROM workload

| Synthetic controller policy | Modeled PPU frames | Actual original JP instruction steps | Modeled NMI entries | Distinct `$18` values observed |
|---|---:|---:|---:|---|
| Start pressed every 30 PPU frames | 480 | 4,438,080 | 475 | `$00,$02,$03,$04,$09,$0A` |
| No buttons | 240 | 2,209,638 | 237 | `$00` |
| A/B/Start cadence | 240 | 2,217,034 | 236 | `$00,$02,$0A` |
| **Total** | **960** | **8,864,752** | **948** | *Union, not extra credit* |

The 480-frame path retains the earlier synthetic first-level selector sequence `$00→$02→$0A→$09→$03→$04`, but reaches the transitions around modeled PPU frames 219, 220, 391, 420 and 421, rather than at exactly the earlier manually injected NMI counts. First-level `$0C/$0D` is still unobserved. The room indices `$07A0/$07A6` are zero in these tested trajectories; no global bound follows.

`0508_cycle_vblank_batch_summary.json` stores per-policy counts and SHA-256 for each **uncompressed** JSON trace. Each complete trace is committed as a deterministic gzip object (`mtime=0`): `0508_cycle_vblank_480_report.json.gz`, `0508_cycle_vblank_none_240.json.gz`, `0508_cycle_vblank_abstart_240.json.gz`. Use `gzip -dc` to inspect. These are compact derived traces, not lossless ROM copies.

## Deliberate limitations

- CPU cycles are advanced at instruction completion, **not** each bus cycle; IRQ/NMI poll latency and race conditions are approximate.
- No real VRC6 IRQ dispatch timing, PPU CHR/nametable/sprite rendering, scroll/OAM video signals, sprite status flags or odd-frame skipped PPU dot.
- `$4014` causes an estimated 513/514-cycle stall but does not emulate the complete OAM DMA read/write bus sequence. Audio/DMC are not scheduled.
- The controller, PPU and NMI conditions remain synthetic, with **no comparison against a trusted reference emulator trace**. This cannot certify real route progression, bank-$0A room-loader liveness, `$18=$0C/$19=$13` from gameplay or native full-frame parity.

**No score or ledger change:** strict verified PRG **49,404/262,144 (18.8461%)**, **VPP 24/100**, completed recovery checkpoint **0507**, fixed PRG31 frontier **`$FB96`**. R-001, R-002 and R-006 remain open. Next is independent reference-emulator differential tracing and fuller PPU/IRQ/mapper integration before promoting newly observed bytes.

## Reproduction

```sh
python3 JP/decomp/tools/test_cycle_vblank_0508.py '<JP ROM>.nes' /tmp/cycle_unit.json
python3 JP/decomp/tools/trace_cycle_vblank_0508.py '<JP ROM>.nes' /tmp/start480.json --frames 480 --policy start30 --max-steps 7000000
python3 JP/decomp/tools/trace_cycle_vblank_0508.py '<JP ROM>.nes' /tmp/none240.json --frames 240 --policy none
python3 JP/decomp/tools/trace_cycle_vblank_0508.py '<JP ROM>.nes' /tmp/abstart240.json --frames 240 --policy abstart
```
