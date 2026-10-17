# JP0650 — Actual DMC DMA source-bank observation in the native Enhanced host

## Scope and evidence classification

This checkpoint adds read-only **actual pinned native** 2A03 DMC sample
DMA-get and VRC6 mapper24 PRG-bank-write observation. It directly addresses
JP0649's unproved question: which physical PRG bank does the game actually
map when hardware fetches a DPCM source byte?

Original Japanese gameplay audio, APU DMA, CPU timing, VRC6 bank registers,
state files, music and SFX sliders, save slots, rendering, and game assets
are **unchanged**. The new trace is **off by default** and writes only
owner-private diagnostic CSV when explicitly requested.

There is **no assertion of live original-JP gameplay capture** in this
checkpoint. Public CI executes synthetic ROMs, production C11 modules
and the pinned native hardware overlay. A live owner game, independent
Mesen trace and real waveform parity still require a private playthrough.

## What is captured, and where

The private source-patch layer
`JP/recomp/tools/patch_cyc_dmc_dma_trace_0650.py` is applied **after**
the already-pinned JP0610 CHR+APU/VRC6 sound register observers.

1. **Real DMA get in upstream `hw_apu.c:dmc_dma_get()`.**
   Exactly one existing `hw_bus_read(apu.dmc_addr)` executes.
   The observer samples the PRG 4 KiB slot mapping from
   `hw_cart.prg_off[(addr>>12)&7] | (addr & $FFF)` immediately
   **before** that read, then records the **returned actual bus byte**
   after the existing read. It also records the CPU cycle,
   DMC source CPU address and `apu.dmc_bytes` *before* its decrement.
   It is not called on CPU halted/dummy cycles or merely scheduled DMC
   requests. This hook is inside the upstream hardware runtime, not a
   theoretical JP0649 bank guess.
2. **Mapper24 CPU write intent in `hw_cart_cpu_write()`.**
   Any original CPU write in the mapper's `$C000–$CFFF` register
   page is logged with `requested_bank8 = value & 31`.
   The original mapper write is still executed unchanged **after**
   the observer. This is **write intent**, not proof that a request
   already took effect. The next actual DMA fetch's physical
   offset is authoritative for that fetch.
3. **Original CPU/host boundary.** Power-on and guest state-load
   produce separate trace epochs, allowing clocks to restart after
   loading. No trace state is included in NES savestates. The trace
   cap is 200,000 rows; on the first excess record it emits
   `trace_limit`, which the verifier **always rejects** rather than
   silently certifying truncated gameplay evidence.

The output schema is:

`event,epoch,cycle,cpu_addr,physical,byte,bank8,bytes_before,requested_bank8`

Events are `power_on`, `state_loaded`, `bank_request`,
`dma_fetch`; invalid source/timing flags are explicit `invalid_*`
events. Unused cells use -1, not invented values. A true bank8 is
derived only from actual C000–DFFF physical mapping; E000–FFFF is
original fixed PRG31, and wrapped 8000–BFFF fetches remain marked
as other switchable PRG, not misattributed to the DMC descriptor bank.

## Owner-private capture and verification

Use the existing authenticated Japanese-ROM private Windows executable.
Append these arguments to the **existing known-good** launch arguments
(do not replace them):

    --dmc-dma-trace "C:\Private\CVIII-DMC-DMA.csv"

Play a known scene with sound effects, then exit normally. The CSV
contains **individual original Japanese ROM-derived sample bytes**:
do **not** commit it, upload it to GitHub, attach it publicly or
include it in a distributable builder. Do not upload the original ROM.

Run the exact source integrity audit privately, supplying the same
owner Japanese ROM:

    python JP/decomp/tools/jp_dmc_dma_trace_verify_0650.py       --rom "C:\Private\Akumajou Densetsu (Japan).nes"       --trace "C:\Private\CVIII-DMC-DMA.csv"       --json "C:\Private\JP0650-DMA-summary.json"

Optional `--strict-byte-match` fails if any returned DMA bus byte
differs from the authenticated cartridge's PRG byte at the recorded
physical offset. Some real 2A03 DMA bus-conflict circumstances may
return other values: mismatches are therefore **recorded explicitly**
even without the optional strict flag, and must be investigated.
The summary JSON stores counts and observed *bank IDs only*, never
sample byte payloads. Owners can retain the full CSV locally for
cross-referencing original Mesen DMA events.

The parser validates exact schema, epoch sequencing, per-epoch
monotone cycles, legal mapper24 CPU/physical mapping, fixed PRG31,
bank-write intent format, original PRG byte consistency and explicit
truncation/corruption rejection. An empty capture or a zero-fetch
valid trace **does not establish game sound execution**. Nor does
a successful private native trace establish independent original
Mesen parity.

## Regression evidence

- `patch_cyc_dmc_dma_trace_0650.py --smoke`: synthesizes the
  actual earlier JP0610 APU/mapper overlays, adds exactly one tap
  to each, rejects duplicate/corrupted source and verifies the
  original audio register observer plus **one** DMC bus read remains.
- `cviii_dmc_dma_trace_test_0650.c`: strict production C11
  event ordering, exact C000/D000/E000 physical sample offsets,
  load/reset epochs, malformed mapping, clock reversal, second-open
  rejection and capped-recording truncation marker. C assertions
  remain active in Windows Release / Linux `-DNDEBUG`.
- `jp_dmc_dma_trace_verify_0650.py --smoke`: synthetic
  original-independent mapped bytes, 8 negative cases, malformed
  epoch, invalid fetch, physical/byte mismatch, mapper-request
  discrepancy and unconditional truncation rejection.
- Linux Mapper24 NESRecomp and Windows SDL2 Alpha builder both
  compile the full original private hardware adapter with the new
  observers. Public builds use **only synthetic media**; a real
  original-JP hardware fetch sequence has not been played here.

## Remaining hard gates for independent Music/SFX

1. Owner-capture one actual Japanese game scene using the new trace,
   the JP0646 source-driver decision trace and JP0610 audio register
   trace on identical runs; verify observed DMC bank8 and any
   mid-sample mapper switches.
2. Acquire *independent original Mesen* mapper register and 2A03 DMC
   DMA-fetch events using the exact same ROM and matched controller
   input/epochs. Pair by cycle and sample bytes; a native-only trace
   is **not** an original reference.
3. Resolve DMC sample-reader buffering/timing, loop and reset semantics
   from these matched logs. JP0649's one-pass bit decoder and
   JP0647's 8+24 virtual mixer remain dormant until timing is proved.
4. Add actual original-music/effects source producers and user-facing
   reversible Enhanced output only **after** an authenticated
   original song + competing-effect comparison.

**Status:** real native instrumentation available; no live game
capture certified; independent Music/SFX playback still unimplemented.
Owner-fixed graphics issue #1 remains closed; all modding features
deferred until Enhanced Edition completion. Strict semantic PRG
49,504/262,144 (18.8843%), VPP27/100, checkpoint0508,
fixed PRG31 $FB96 and R-002/R-007 OPEN unchanged.
