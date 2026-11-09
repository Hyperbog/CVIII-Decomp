# JP0839 — Original-JP Stage 1 frame boundary vs. player Y

## Evidence

Owner's original-JP JP0835 MesenCE ZIP and actual JP0837 Windows run reported 811 frame snapshots, frames 3090..3900. Native vs interpreter RAM and cycle counts matched all 811; both source 3/slot 1 and source 4/slot 2 actors first appeared in post-frame snapshot 3091 and persisted through 3900. This is **sampled**, not intra-frame or whole-game, parity.

All 811 original/native sample cycle offsets are bounded between +2 and +6 CPU cycles: +2 (266 frames), +3 (247), +4 (229), +5 (35), +6 (34). There is no observed accumulating drift in the sampled span.

### Verified instruction-boundary mismatch

- MesenCE [`Core/NES/NesPpu.cpp`](https://github.com/nesdev-org/MesenCE/blob/master/Core/NES/NesPpu.cpp): `SendFrame()` invokes `ProcessEvent(EventType::EndFrame)` as `ProcessScanlineStart()` enters scanline 240, so JP0835's Lua `endFrame` callback captures RAM at the PPU scanline boundary.
- NESRecomp **pinned** `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1` [`runner/cyc/hw_ppu.c`](https://github.com/mstan/nesrecomp/blob/2b4fcdb98c9e702be3fb365cfc645003c50b5fc1/runner/cyc/hw_ppu.c): `advance_dot()` sets `hw_observe_hit = hw_frame_done = true` at scanline 240.
- The same engine's [`runner/cyc/cyc_run.c`](https://github.com/mstan/nesrecomp/blob/2b4fcdb98c9e702be3fb365cfc645003c50b5fc1/runner/cyc/cyc_run.c): `run_until_stop()` only returns from dispatch **after an instruction**; `cyc_run_frame()` then calls `cyc_run_observer`. Thus `--frame-log-at mesen` targets the same PPU line, but samples the guest RAM at the next CPU instruction boundary. The observed +2..+6 CPU cycles are consistent with this mechanism. Exact instruction causality has **not** been traced.

### Original authenticated-ROM writer

Original Japanese Mapper24 ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Physical 16 KiB PRG bank 11, CPU `$8023–$8035` (when mapped at `$8000`): `CLC; LDA $04DB,X; ADC $0537,X; STA $04DB,X; LDA $041C,X; ADC $0520,X; STA $041C,X`. This is an authentic routine updating actor Y fraction `$04DB+X` and Y integer `$041C+X`, including player slot `X=0`. Native and Mesen differed in `$04DB` on 44 frames and `$041C` on 43 frames. These **player-slot** coordinates were excluded by JP0833's actor-watch set (slots 1..12); zero watched differences does not establish whole-player-state parity.

Other original snapshots: `$01E1,$01E2,$01E3` did not change across 811 frames, while `$0020` changed on 806 frame transitions and `$01FC` on 802. The constant stack bytes are not necessarily harmless: real stack-pointer and writer evidence is still absent.

## Read-only Windows classifier

The JP0839 tool consumes the same authenticated ZIP and JP0837 native logs. It verifies existing JP0838 provenance and 811-frame native/interpreter equality before reporting first player-slot Y mismatch, mismatch episode lengths, selected source/native neighboring values, and CPU clock offsets. Adjacent-frame equality is a **diagnostic only**, not proof of frame shift.

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
python .\JP\recomp\tools\jp0839_player_boundary_probe.py --smoke
python .\JP\recomp\tools\jp0839_player_boundary_probe.py `
  --owner-capture $zip `
  --jp0837-dir "$env:USERPROFILE\Documents\jp0837-private" `
  > "$env:USERPROFILE\Documents\jp0839-player-boundary.json"
$r = Get-Content "$env:USERPROFILE\Documents\jp0839-player-boundary.json" -Raw | ConvertFrom-Json
$r.first_player_y_mismatch
$r.player_y_mismatch_episodes | Select-Object -First 8
$r.addresses.'041C' | Format-List
$r.addresses.'04DB' | Format-List
```

## Decision criterion

If player Y differences occur as isolated updates with no lasting divergence, inspect exact instruction starts, mapped physical bank and in-flight opcode at the first discrepant sample before changing CPU/PPU scheduling. If they persist, isolate the first actual player-difference frame and compare ROM execution paths, input read phase, and mapped bank. Do not make actor, timing, mapper or source-ROM modifications based solely on end-frame RAM offsets. No real native JP0839 run has yet been executed here.