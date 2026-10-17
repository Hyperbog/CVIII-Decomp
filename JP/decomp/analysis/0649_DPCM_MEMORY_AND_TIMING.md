# JP0649 — Original Japanese DPCM sample geometry and bounded DAC

## Scope and original owner-ROM verification

JP0648 authenticated 15 original sound commands ($6F–$7D) and their
four-byte 2A03 DMC register programs from PRG0C:$A957–$A992.
JP0649 recovers original **CPU sample address/length, VRC6 switchable
PRG bank geometry, regional DMC periods, and raw 7-bit bitstream DAC**,
but does not replace the working sound or simulate full DMA timing.

The owner-local ROM audit passed against the exact Japanese Mapper24
cartridge, SHA-256
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
It delegates all bank0C metadata/driver and 15 special-record pointer
checks to the previously authenticated JP0648 source verifier.

The original **15 DMC entries occupy 8 unique CPU sample spans**.
All spans are fully within the switchable CPU **$C000–$DFFF** PRG
window; earliest begins $C000, latest ends $DFC0. **Two**
original variants loop; **none** request an enabled DMC IRQ in the
static descriptor. Some commands share identical sample addresses
with different rate indices.

The original APU register specification is:

- Sample address = $C000 + 64 * value written to $4012.
- Byte length = 1 + 16 * value written to $4013.
- Period index = ($4010 & $0F), using exact NTSC/PAL lookup tables.
- Initial 7-bit DAC value = $4011 & $7F.

## The critical still-unresolved mapper bank

Mapper24/VRC6 **switches** its physical 8 KiB bank at $C000–$DFFF
using the $C000 bank register, low five bits. Physical PRG offset is
8192 * bank8 + (CPU_addr - $C000), for an **explicitly observed
stable** register value bank8 in 0..31.

The original sound descriptors alone do **not** establish which bank
the game selects at actual DMA fetch time, or whether a bank switch
occurs while DMA is playing. The new helper requires an explicit bank
snapshot and rejects bank-window-crossing samples. Testing 32 possible
bank selections is mathematical mapping coverage, not evidence of the
authentic runtime selection. No bank choice is invented.

## Production C11 decoder and tests

The dormant module cviii_dpcm_decode_0649.h/.c accepts a successful
JP0648 event plan and bank8. It validates original six-write register
ordering, priority/command/counter consistency, bounded address span,
full 256KiB PRG size and output capacity. It outputs one pass of raw,
LSB-first seven-bit DAC levels, applying +2/-2 steps without exceeding
0..127. It never writes guest APU, mapper RAM, CPU state, PCM or save
files and has no live call site in the game's audio callback.

The strict C11 fixture cviii_dpcm_decode_test_0649.c exercises all
15 commands × 256 priority values, all 32 candidate bank8 mappings
and NTSC/PAL rates on accepted plans, malformed plan rejection,
$DFFF crossing refusal, bit order, both output clamps, insufficient
buffer refusal and unchanged caller output on failed inputs.
The tests force assertions active even in Windows Release builds.

Owner-local Python source audit jp_dpcm_memory_audit_0649.py
authenticates the exact original ROM, the prior original metadata
and DMC table fingerprints, and all eight source spans; optional
JSON outputs **metadata only**, never copyrighted DPCM sample bytes.
The ROM-free mode uses invented descriptor values and deliberate
out-of-range negative cases. Public Windows and Linux CI are ROM-free.

Run privately:

    python3 JP/decomp/tools/jp_dpcm_memory_audit_0649.py --smoke
    python3 JP/decomp/tools/jp_dpcm_memory_audit_0649.py --rom "PRIVATE_ORIGINAL_JP.nes"

## Hardware timing boundary

The result's bit_count * period_cpu_cycles is the *idealized raw bit
period sum*, not a claim of elapsed NES CPU cycles or audible timing.
NES hardware has asynchronous DMC memory fetches, buffering, shift
phase, OAMDMA contention, 3/4-cycle DMA stalls, looping and restart
behavior. The earlier JP0554 DMC DMA helper also remains explicitly
caller-driven and is not automatically connected to this decoder.

References: https://www.nesdev.org/wiki/APU_DMC and
https://www.nesdev.org/wiki/DMA.

Original game playback and JP0647 independent Music/SFX voices remain
unchanged/dormant. **Still open:** record live original Mesen/native
$C000 mapper bank writes and DMA fetch timing, verify actual sample
source bytes and their timing, build a correctly buffered real-time
effect producer, then compare game audio before enabling anything.

Modding is deferred until the Enhanced Edition is complete; owner-fixed
graphics issue #1 stays closed. Strict semantic PRG remains
49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed frontier
$FB96; R-002 and audio R-007 OPEN.
