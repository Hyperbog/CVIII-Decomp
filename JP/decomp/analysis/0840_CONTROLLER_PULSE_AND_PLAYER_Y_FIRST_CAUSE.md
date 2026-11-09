# JP0840 — Stage 1: controller intent vs game-accepted A, player Y first cause

## Verified original source (private JP0835 archive)

The original Japanese mapper-24 ROM was previously authenticated as SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. The captured JP0835 ZIP SHA-256 is `bd41c9c241d100e112c166ee8d0cf0928d39840399c3e28e854d58609ea4e46d`. The owner independently ran a JP0837 native/interpreter comparison and a JP0839 player RAM triage; the **native logs remain private to the owner's Windows system**.

JP0839 found a consecutive player-slot-0 Y difference, frames **3511..3596** (86 frames). The integer Y byte `$041C` differs on frames **3511..3553** (43), and fractional Y byte `$04DB` on **3553..3596** (44). Its zero watched actor-slot-1..12 mismatches do *not* imply player parity.

**New verified evidence from the original Mesen capture:** Of 28 short scheduled A pulses after frame 2695, 27 are registered in guest `$002A` on the intended frame. Only the pulse scheduled for frame **3509** is reflected in guest `$002A` at frame **3511**, a **two-frame delay**. Guest `$0028` also first flags A at frame 3511; original player integer Y stays `$B0` through frame 3512 and first moves to `$AB` at frame **3513**. The owner-reported native Y already equals `$AB` at frame **3511** and `$A6` at frame 3512. This is strong evidence for a different acceptance/processing moment for one controller pulse, not proof of the mechanism.

A per-frame `inputPolled` controller-intent record does not establish exact $4016/$4017 CPU read timing. `$0028/$002A` are game-owned RAM indicators, **not bus captures**. The two-frame delay might reflect game-loop scheduling, skipped input-processing, input capture callbacks, or CPU/PPU timing. Do not permanently compensate by shifting input frames or modifying actor AI without tracing the first cause.

## Owner-only next check (existing native logs, no recompilation)

```powershell
cd C:\Users\hyper\CVIII-Decomp
git pull --ff-only origin decompilation
python .\JP\recomp\tools\jp0840_input_pulse_firstcause.py --smoke
python .\JP\recomp\tools\jp0840_input_pulse_firstcause.py `
  --owner-capture $zip `
  --jp0837-dir "$env:USERPROFILE\Documents\jp0837-private" `
  > "$env:USERPROFILE\Documents\jp0840-input-onset.json"
$r = Get-Content "$env:USERPROFILE\Documents\jp0840-input-onset.json" -Raw | ConvertFrom-Json
$r.focus_source_guest_a_held_first
$r.focus_native_guest_a_held_first
$r.focus_source_player_integer_y_first_moves
$r.focus_native_player_integer_y_first_moves
$r.focus_rows | Format-Table -AutoSize
```

If the native guest accepts A at frame 3509 but the original Mesen guest only at 3511, **first investigate the source of that discrepancy**. The next investigation would compare first $4016/$4017 reads and the original ROM's input-acceptance path during frames 3508–3512; avoid a gameplay patch justified solely by a replay-intent schedule.

## Checks performed

- Re-parsed the real original owner-private JP0835 ZIP; 28 source A rising events, one exceptional two-frame guest delay at 3509; first Mesen player-Y movement frame 3513.
- Python syntax and ROM-free unit smoke passed.
- Native comparison branch is implemented to validate JP0837 provenance and all 811 native/interpreter frames before reporting differences. **The tool was not executed against the owner's private native traces here**; first native input onset remains unverified.
- No engine, mapper, ROM, scheduler, recompilation, or guest-state changes.