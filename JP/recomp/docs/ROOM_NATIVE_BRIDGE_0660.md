# JP0660 — Original-6502/native room-loader observation bridge

## Status and safety boundary

**Experimental opt-in verification, not native replacement.** The actual Japanese
2A03 executes its original PRG0A:$B7F7–$B872 routine, including JSR/RTS, mapper
switches, CPU/PPU cycles, IRQs and DMA. The independent C11 model
`cviii_room_stream_0659` runs on an entry snapshot and never commits guest state.

The bridge uses **two actual upstream NESRecomp callbacks without editing
upstream**: `cyc_cpu_ram_read_policy` sees the original `LDA $07A0` at the
operand read of `$0A:$B7F7`, and `cyc_cpu_rts_observer` observes its final RTS.
The entry is conditioned on the **physical 4-KiB PRG identity `$2B`** at CPU
`$B7F7`, the actual `AD A0 07` opcode sequence, RAM `$23=$0A`, and a
five-value bounded original selector `$07A0` (0–4). This callback returns the
unmodified operand byte and never writes guest state.

The expected stack return address is extracted from the actual CPU stack at
entry. An RTS is checked only when both return PC and restored S match.
The comparison includes **all non-stack CPU RAM, A/X/Y, C/Z/N/V, preserved I/D,
and final physical bank**. Stack page `$0100–$01FF` is excluded because
original nested JSR/RTS instructions overwrite their scratch locations.

When the host's `--hash-out` enables the cycle trace, the verifier records real
CPU writes to VRC6 mapper port `$8000` and checks their **ordered values**
against the original 0E/0A switch sequence. Without cycle tracing, results
are labeled `mapper=NOT_OBSERVED`, **never** complete mapper postcondition
matches. The cycle span from the first operand read through final RTS is
reported, but there is no independently proven cycle budget. This is
postcondition observation, not cycle/interrupt parity certification.

A busy CPU RAM-read or RTS callback causes initialization to fail rather than
silently replacing another plugin's observer. An occupied trace hook degrades
to CPU/RAM-only verification. Malformed/missing pack rejects the opt-in switch.
Unsupported selector or bank identity leaves original execution unchanged.
Any mismatch only reports a diagnostic; there is no speculative state write,
rollback, branch hijack, or automatic native replacement.

## Owner-only input

The importer authenticates the whole 393,232-byte Japanese mapper24 ROM using
SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
It extracts the ten-byte original PRG0A pointer table and the exact 175-byte
PRG0E source stream into a **249-byte owner-local private pack**. The runtime
checks the fixed source ROM identity and pinned FNV64 of the original fragments,
then self-tests all five selector streams. FNV64 is an accidental corruption
check, not a cryptographic signature; these packs must come only from the
trusted importer, not untrusted mods or network sources.

```sh
python3 JP/recomp/tools/build_room_native_bridge_0660.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --out "/private/CVIII-Room-Native-Verify.dat"
```

Then pass `--native-room-verify /private/CVIII-Room-Native-Verify.dat` to the
private NESRecomp build. Add `--hash-out /private/native-room-hashes.txt` in a
**headless** run to enable real ordered mapper-write verification. The existing
`--frames`, `--input`, save/load and debugger mechanisms remain unchanged;
no TAS is required. If the routine is never reached naturally, no comparison
is claimed and `observed_entries` stays zero.

## Reproduction without commercial data

GitHub Actions builds/runs the ROM-free synthetic tests from
`JP/recomp/tests/room_native_bridge_0660/`. They cover 1,280 selector/seed
cases, 640 independent mapper-write sequences, mismatched RAM/writes, unsupported
selectors, stack-return matching, wrong mapped bank and opcode, and untouched
guest operand value. The external native-host integration CI also builds the
actual game-owned observer with real NESRecomp headers.

**Not established:** naturally observed `$0A:$B7F7` gameplay entries, full
frame or cycle/interrupt parity, original graphics parity, or authorization to
bypass the 6502 routine. No TAS or emulator trace data is part of the
permanent ROM-only reference CSV.