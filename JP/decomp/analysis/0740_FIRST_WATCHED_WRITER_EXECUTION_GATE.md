# JP0740 — First watched original-JP CPU write: opt-in execution evidence gate

**Result:** instrumentation implemented; the first incorrect writer of $62,
$0565, $0520 or $041C is **not yet established**. This checkpoint must
not convert opcode-byte candidates into claims of live instruction execution.

## Existing source evidence

Original Japanese Mapper24 ROM SHA-256:
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.
The recovered original JP0718 ZIP preserves periodic RAM/PPU snapshots,
controller polls and limited selector writes. Its 11 historical
RAM_CHANGE events target only $35/$36, not the player or scrolling state
under investigation. The older JP0719 native ZIP preserves periodic
RAM/PPU/CHR/OAM snapshots but no CPU bus-write sequence. Exact controller
*input intent* from 17,562 original polls agrees with the native input
schedule; equal CPU $4016 latch/read timing is **not verified**.

The JP0739 ROM-verified direct-store candidates remain candidates.
Their exact execution order cannot be recovered by interpolation from
the samples around original frame 9,504.

## Original MesenCE read-only observer

File: JP/decomp/tools/mesen_jp0740_original_write_trace.lua

- Locked to the actual original-JP iNES SHA-1 used by the archived
  JP0718 Mesen2 recording. Requires enabled Mesen script file I/O.
- Consumes the **existing owner-private original JP0718 -input.tsv**,
  requires 17,562 ascending absolute-frame records and a complete footer.
  Uses emu.setInput at the inputPolled event to reproduce that *intent*.
  This changes controller inputs according to the historical schedule,
  not game RAM; it cannot independently guarantee CPU bus read parity.
- Collects original CPU writes (including unchanged-value stores) to
  $0062, $0053-$0055, $0063, $006B, player coordinates, fractional
  speeds and action/fall state, plus controller bus reads at $4016/$4017.
- An execution callback observes CPU PC *before* the watched writes,
  and Mesen convertAddress provides a physical PRG offset. Those are
  recorded as mapped opcode-PC evidence, not blindly equated with the
  post-instruction PC returned by a write callback.
- Bounds events to source frames 9,370–9,600; caps 150,000 events;
  refuses reset/state load, missing inputs, incomplete runs and failed
  original snapshots. The source RAM anchor state and exact CPU cycle
  count at frames 9,440, 9,504 and 9,576 **must** reproduce the
  recovered historical JP0718 reference.
- Does not store full original ROM, graphics or controller recordings
  in the public repo.

The original emulator must be run with a compatible Mesen Lua host
and the original cartridge: an original trace has **not** been captured
in this session. The runner is not available in the current container.
Do not ask the owner for a new manual playthrough.

## Opt-in native NESRecomp 2A03 recorder

Files:
- JP/recomp/tools/jp0740_native_write_overlay.py
- JP/recomp/native/rom_runtime_0732/cviii_jp0740_native_trace.c/.h

The normal game remains uninstrumented. Only a private
CMake `-DJP0740_TRACE_CPU_WRITES=ON` build:
1. Requires JP0733 SHA-verified retail ROM-at-launch entry;
2. Uses **exact text anchors** against the pinned original
   NESRecomp hw_machine.c / cyc_run.c; rejects changed upstream sources;
3. Makes source copies in the build directory, **never modifies
   the upstream pinned noncommercial checkout**;
4. At CPU instruction dispatch captures PC and 4KiB PRG bank identity,
   then observes actual hw_bus_write, including no-op/unchanged RAM
   writes; also observes CPU $4016/$4017 via hw_read;
5. Emits only a bounded private event trace on native frames 9,370–9,600
   with `JP0740_NATIVE_TRACE_TSV`; atexit marks
   incomplete runs as such. The zero-based native frame index must **not**
   be silently treated as original Mesen absolute frame.

No original ROM or compiled game bytes are committed.
No native behavior or actor collision algorithms were modified.

## Private reproduction prerequisites and commands

Start from the existing recordings, without another owner playthrough:

~~~sh
python3 JP/decomp/tools/jp0740_trace_verify.py \
  --rom "$ORIGINAL_JP_ROM" \
  --make-original-anchors "$OLD_JP0718_MESEN_ZIP" \
  --anchor-out /private/jp0740_anchors.tsv
~~~

A compatible original Mesen runner must execute the Lua source from the
**original power-on** with the following private environment paths:

~~~text
JP0740_INPUT_TSV=/private/JP0718-...-input.tsv
JP0740_ANCHORS_TSV=/private/jp0740_anchors.tsv
JP0740_TRACE_TSV=/private/jp0740_mesen_writes.tsv
~~~

For the authenticated current native engine, build only the internal
trace-target option, then run with the *existing* native controller input
schedule (owned original ROM provided only at launch):

~~~sh
cmake -S JP/recomp/native/rom_runtime_0732 -B /private/jp0740-build \
  -DNESRECOMP_EXTERNAL_ROOT=/private/pinned-nesrecomp \
  -DJP0740_TRACE_CPU_WRITES=ON -DJP0732_WINDOWED=OFF
cmake --build /private/jp0740-build --parallel
JP0740_NATIVE_TRACE_TSV=/private/jp0740_native_writes.tsv \
  /private/jp0740-build/jp_akumajou_runtime_0732 "$ORIGINAL_JP_ROM" \
    --headless --frames 9610 --edition original \
    --input /private/JP0719-original-controller-input.input
~~~

The exact argument compatibility must be verified against the pinned
runtime and launcher, and the native logger's COMPLETE footer checked.
The older JP0719 native executable is **not** the newer JP0732/JP0737
runtime. A valid JP0740 native capture is not interchangeable with the
historical JP0719 snapshot archive.

After obtaining two **successful** private traces:

~~~sh
python3 JP/decomp/tools/jp0740_trace_verify.py \
  --rom "$ORIGINAL_JP_ROM" \
  --original-trace /private/jp0740_mesen_writes.tsv \
  --native-trace /private/jp0740_native_writes.tsv
~~~

This parser enforces event ordering, ROM identity, mirror semantics,
mapped PRG offset low bits and original historical anchors. The output
intentionally **does not claim a first incorrect write** without a
cross-engine validated CPU-state/cycle/mapper alignment. Chronological
write sequences allow identification of candidate producer PCs after
that alignment. The static census can then be cross-referenced against
the actual mapped writer and player-state dependencies.

## Reproducible public tests

~~~sh
python3 JP/decomp/tools/jp0740_trace_verify.py --smoke
python3 JP/recomp/tools/jp0740_native_write_overlay.py --smoke
~~~

The native regression gate also syntax-checks the C11 trace observer.
These are entirely ROM-free tests; passing them is neither a user
JP0723+ playthrough nor original Japanese gameplay parity.

**Scores unchanged:** VPP 31/100, strictly certified physical PRG
49,504/262,144, checkpoint 0508. Last personally owner-tested
checkpoint remains **JP0722**. All JP0740 events and source evidence
have zero new certification credit.
