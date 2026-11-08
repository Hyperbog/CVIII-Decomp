# JP0838 — Original Stage 1 actor-boundary triage from real JP0837 logs

## Evidence and limits

Owner's actual JP0837 Windows run reported 3,901 matching native/interpreter full-machine hash records; 6,716 distinct bank-qualified interpreter ROM misses from 27 physical 4 KiB banks (10,917,746 total misses). No original Mesen CPU instruction trace or authenticated native engine commit was provided. An interpreter miss log is **not total executed-ROM coverage**.

The first source/native RAM comparison (frame 3090) differs at ten bytes. At that boundary the reported actor-watch set matches and source 3 / source 4 type-`$3D` actors are not yet present in either sampled machine. Mesen's `$0020` is `$16` at frame 3090, `$B3` at 3091, and `$EC` at 3092; native is `$EC` at 3090. This suggests a possible frame or observation-phase offset but is **not** proof of one. Stack bytes near `$01E1` are also shifted. Compare clock values and actor provenance before debugging AI.

## Read-only Windows diagnostic

From the `decompilation` checkout:

```powershell
python .\JP\recomp\tools\jp0838_actor_boundary_triage.py --smoke
python .\JP\recomp\tools\jp0838_actor_boundary_triage.py `
  --owner-capture "$env:USERPROFILE\Documents\MesenCE\LuaScriptData\jp0835_capture_20261108.zip" `
  --jp0837-dir "$env:USERPROFILE\Documents\jp0837-private" `
  > "$env:USERPROFILE\Documents\jp0838-triage.json"
```

It reads existing `native.cycframe`, `interp.cycframe`, `jp0837-report.json` and the strict JP0835 archive. It does not replay game frames, modify source/ROM, or rewrite private traces. The strict JP0837 report binds the files to the original capture. The output includes 811 post-frame snapshots (3090–3900), both actors' first paired sample, the first differing watched address and frame, actor-presence disagreement, original/native/interpreter clock positions and selected RAM snippets.

Use the resulting `source_vs_native.first_watched_ram_difference` and `source_vs_native.first_actor_pair_difference` to decide which subsystem requires investigation. A `null` value means *none among sampled frames 3090–3900*, not a whole-game proof. A nonzero clock offset alone does not prove an input phase error; $4016 bus reads and NMI entry must be traced before attributing cause. If parity first breaks before frame 3090, obtain earlier original-Mesen RAM snapshots; JP0835 provides 2695 onward.

## Next verification boundary

If the actor pair differs, select the first affected frame and examine original/compiled opcode and mapper-bank traces around its preceding NMI and writer sites. If sampled actor state matches, diagnose stack `$01E1` and zero page `$0020` with an earlier synchronized capture before adding actor-side patches. Preserve original Mapper24 VRC6 behavior and the pinned NESRecomp engine until differential evidence warrants an isolated change.