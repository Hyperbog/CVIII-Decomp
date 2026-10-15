# JP0629 — Real-Mesen provenance gate for raw01/0A room selectors

**Status:** Original-ROM-derived nine-entry source boundary recovered; read-only
Mesen2 capture script and fail-closed temporal trace validator committed.
A **real Mesen capture has NOT been collected or validated** in this phase.
R-002 remains OPEN, strict decompilation PRG coverage unchanged.

## Authenticated physical table and narrowed risk classification

The owner-local Japanese retail ROM SHA-256 is
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
In physical VRC6 **raw bank01** (16KiB selected at CPU $8000-$BFFF)
the known `$BB57-$BB61` source reads
`LDA $30; LSR A; TAY; LDA $BB62,Y; STA $07A0; RTS`.

A separate **nine-byte physical array** sits at raw01 **$BB62-$BB6A**,
SHA-256 `5dc2cd33cc3315a52720f845da6d9ad4af1b4f18fef32d6bf8629390e1cd6944`.
At raw01:$BB6B the bytes are `A9 00 85 00 A2 05`, an instruction-like
`LDA #0; STA $00; LDX #5` entry. Raw01:$B877 contains `JMP $BB6B`.
That explicit control-flow candidate strongly distinguishes the following
bytes from an intended 128-entry lookup table, but a live original-game
call still needs execution evidence.

The nine-entry table is accessed without going past its identified end
for hypothetical `RAM[$30]=$00..$11` (18 inputs, 2 per byte).
If **each** such output is subsequently fed to the **separate** raw0A
room-loader consumer at `$B7F7` under correct bank0A mapping:

| Consumer pointer type | Conditional RAM $30 inputs |
|---|---:|
| One of five previously validated stream roots | 6 |
| Other address in $8000-$BFFF (not record-validated) | 4 |
| Outside expected switchable bank0E window | 8 |
| **Total** | **18** |

The specific `$30=$06 → $07A0=$35 → $FF63` example remains a
**conditional calculation**, not observed cross-bank gameplay.
The previous [JP0628 all-256 sweep](0628_ROOM_SELECTOR_PRODUCER_BOUNDARY.md)
was useful to demonstrate failure cases, but most inputs make `$BB57`
read **past the nine identified table cells** into different original
bytes. Neither analysis proves the live domain of `$30`, the live
bank01 → bank0A flow, or a game crash. `$FF63` is a legal fixed
PRG31 CPU address, merely outside the hypothesized bank0E stream range.

The [original-ROM table audit](../tools/audit_room_selector_table_0629.py)
authenticates the complete ROM, original producer opcodes, all nine
table bytes by SHA-256, `$BB6B` code-like prefix and `$B877`
branch bytes. It produces non-lossless source classifications and
refuses changed source signatures. The private original-ROM audit
**PASSed locally** for all 18 bounded inputs.

## Real reference-emulator acquisition contract

[Original-Mesen script](../tools/mesen_jp_room_selector_provenance_0629.lua)
registers read-only callbacks at the *CPU* locations:

- raw01:$BB57 producer **entry** (event P) only if
  `emu.convertAddress` maps that CPU address to **physical PRG offset
  $07B57**;
- **all four 2 KiB CPU-mirrored aliases** of RAM $07A0, recording the
  proposed new byte and pre-write RAM value (event W);
- raw0A:$B7F7 consumer **entry** (event C) only if the source maps to
  physical PRG **offset $2B7F7**. The pointer read is from mapped
  actual raw0A CPU addresses, using Mesen's side-effect-free NES
  debug memory read, then recorded with the actual RAM[$07A0].

The script also records tracked mapper shadow `RAM[$23]`, optional
CPU PC/physical hint for writes, CPU cycles, and monotonically numbered
events. Source-only PC aliases never establish a raw bank. It
**fails closed** on unexpected table mappings, log limits and state
loads; produces a terminal marker at script end. It does not mutate
RAM, mapper registers, input, savestates, PPU or APU.

In Mesen2/MesenCE with your own original JP cartridge, load the Lua
script, perform **real gameplay without injecting state**, stop it,
then save the Lua log privately (do not commit the log until source
and privacy review).

Validate the log using the repository's
[JP0629 trace validator](../tools/audit_mesen_room_selector_trace_0629.py):

```sh
python3 JP/tools/audit_mesen_room_selector_trace_0629.py --smoke
python3 JP/tools/audit_room_selector_table_0629.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --out /tmp/jp0629_table.json
python3 JP/tools/audit_mesen_room_selector_trace_0629.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --trace "/private/Mesen2-JP0629.log" \
  --out /tmp/jp0629_mesen_report.json
```

The validator requires the original ROM SHA, exact source PC, physical
PRG offset *and* tracked bank for the P/C entry events, CPU-cycle
ordering, complete event/footer accounting, source-consistent
pointer words and no state load or truncated capture. It reports
candidate last-write → consumer temporal links, without promoting
source-code bytes, proving every intermediate writer path or
claiming an actual gameplay run when only synthetic examples exist.

**Testing:** ROM-free equivalent producer/consumer trace fixtures
pass locally, including negative cases for wrong bank, false source
PC, wrong pointer, sequence errors, truncation and state-load.
The repo's parser has its own `--smoke` routine; Windows and Linux
workflow checks have been committed, but a fresh Actions execution is
not yet certified. **No Mesen executable or session was available in
the current container**; no independent reference-emulator observation
is claimed.

## Open proof and ledger boundary

The original [0508 synthetic NMI manifest](0508_BULK_DYNAMIC_PRODUCER_TRACE.md)
did not encounter room selector state $18=$0C/$0D and did not establish
a live raw01:$BB57 → raw0A:$B7F7 chain. These are distinct state
families until a mapper-qualified original-game trace proves otherwise.

**R-002 remains OPEN:** establish the actual producer bank, live
caller and RAM[$30] domain; compare it with all intervening writes to
RAM[$07A0] before each raw0A room-loader entry; then prove five-stream
indexes in real gameplay or document and analyze alternatives.

**Certification unchanged:** strict PRG **49,504 / 262,144
(18.8843%)**, VPP **27/100**, checkpoint **0508**, fixed frontier
**$FB96**. `JP/analysis/RESUME_STATE.json` not modified.
