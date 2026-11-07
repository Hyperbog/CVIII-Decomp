# JP0651 — Independent MesenCE DMC DMA source and cycle comparison

## Original goal and evidence boundary

JP0650 records actual native NESRecomp DMC DMA-get bytes with the
physical mapper24 PRG offset at the read. JP0651 adds a corresponding
read-only **independent MesenCE core instrumentation source** and a strict
comparison of the two recorded fetch streams. It does not change the
owner's running game. The original Japanese ROM remains private.

**Checkpoint completion means the observer-source generator, source
provenance pin, cross-trace validator, negative tests and Windows/Linux
CI are ready. It does NOT mean independent original Japanese game
execution or Mesen-vs-native DMA equality was observed.**

## Why generic Mesen Lua reads are insufficient

A Mesen `read` callback on CPU `$C000–$FFFF` can see normal instruction
and operand reads, dummy reads, OAM DMA or a real DMC fetch. Such a
callback alone cannot certify a DMC sample-byte transfer.

Instead, JP0651 independently inspects [MesenCE](https://github.com/nesdev-org/MesenCE)
`Core/NES/NesCpu.cpp`, in its genuine DMC-only
`NesCpu::ProcessPendingDma()` branch, where
`_dmcDmaRunning && !_needHalt && !_needDummyRead` holds, the existing
`ProcessDmaRead(GetDmcReadAddress(),...)` returns a byte, and
`SetDmcReadBuffer(readValue)` is called. That branch is separately
marked by `_isDmcDmaRead` and excludes OAM/dummy reads.

The private patch:

- Is **strictly pinned** to upstream MesenCE commit
  `4b8a196e299b3de297b204fd1208d2981562c89b` and exact
  Git blob SHA-1 `d411c11981f16011bd8a19f7cc0b2a69cae1a019`
  for `Core/NES/NesCpu.cpp`. A different checkout fails closed.
  Because MesenCE uses `* text=auto` in `.gitattributes`, Windows Git
  may check out the pristine file with CRLF even though the canonical
  Git blob uses LF. The patcher permits **only** full-file CRLF-to-LF
  normalization before checking the unchanged pinned blob SHA.
  Mixed line endings, stray CR bytes and modified content remain
  rejected; the canonical SHA is not replaced or bypassed.
- Produces a separate patch output file for a **private separately
  compiled MesenCE checkout**, not a repository edit or distributed
  emulator binary.
- Captures the original DMC read's returned byte, original CPU
  read address, `GetMapper()->GetAbsoluteAddress(address)` physical
  PRG offset (or -1 for unmapped RAM), and the Mesen CPU cycle.
  It **never issues an extra bus read or modifies the returned value**.
- Activates only with a nonempty `CVIII_MESEN_DMC_TRACE`
  environment path. The private CSV includes actual ROM sample bytes.
  A 200,000-fetch cap emits `trace_limit`, rejected by the validator.
- Is statically and synthetically tested by CI, **not** independently
  built/run as a complete MesenCE emulator there. Compiler/runtime
  acceptance still requires the owner to build and execute the
  pinned, privately patched MesenCE version.

## Owner-only evidence collection

Build a private MesenCE from the exact pinned commit. On that checkout,
run the patcher against **the pristine** `Core/NES/NesCpu.cpp` into
a separate folder, then substitute the generated file in a **private
build copy** of MesenCE and compile per MesenCE's build instructions.

Example (POSIX-style, adapt paths on Windows):

```sh
python3 JP/decomp/tools/patch_mesen_dmc_reference_0651.py \
  --source "/private/MesenCE/Core/NES/NesCpu.cpp" \
  --out "/private/mesen-patched/NesCpu.cpp"
```

Set `CVIII_MESEN_DMC_TRACE` to a private output CSV path in the
environment when running this privately compiled emulator with the
same authenticated original Japanese ROM. For native execution,
append the existing JP0650 option `--dmc-dma-trace` to the established
private native launch arguments. **Both runs need identical power-on
conditions, controller inputs, stage route, region and no load-state
transitions.** Save states are deliberately not comparable yet.

Then run:

```sh
python3 JP/decomp/tools/jp_mesen_dmc_dma_compare_0651.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native "/private/CVIII-DMC-DMA.csv" \
  --mesen "/private/Mesen-DMC-DMA.csv" \
  --json "/private/JP0651-DMA-pair-summary.json"
```

If the native JP0650 verifier reports any ROM-byte divergences,
capture the exception-only owner-local CSV in that SAME native run with
`CVIII_DMC_CONFLICT_TRACE` (the merged JP0650 read-only extension),
and append:

    --conflicts "/private/CVIII-DMC-Conflicts.csv"

The sidecar is **required only when native sample bytes differ from
authenticated PRG bytes**. It contains no sample byte values. Its row
count and in-order cycle, CPU/physical source, power epoch, held CPU
read address, and 2A03 `$4015-$4017` register alias are rechecked
against every actual native mismatch; `cpu_reading=1` and
`alias_conditions_met=1` are required. Missing, extra, duplicated,
forged, or unclassified sidecar records fail closed. A sidecar alone
is not proof of reference parity or capture provenance.

The original SHA-256-pinned ROM must match
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Neither the cartridge, generated sample bytes, full private logs,
patched emulator binary nor sound assets are to be committed.

## Comparison contract

The independently recorded Mesen CSV has:
`event,cycle,cpu_addr,physical,byte` with only `dma_fetch` rows
and possible **rejected** `trace_limit`.

The JP0650 native CSV is also revalidated using the existing
source-authenticated ROM, mapper bank/page, epoch and event checks.
Normal fetches must match cartridge PRG bytes exactly. The ONLY
exception is a recorded, validated, same-session JP0650 held-CPU
register-conflict row for that specific native fetch ordinal.
The native mismatch's **actual bus-returned byte is never changed,
replaced, inferred or ignored**. The MesenCE reference may differ from
ROM only at those classified ordinals and must produce the same
returned byte as native, not a substituted pristine ROM byte.
All other byte differences remain a hard failure.
JP0651 demands **one native power-on epoch**, with no save/load,
at least two DMA gets in each trace, one-to-one fetch count and order,
and identical CPU address, mapped PRG offset and sample byte at every
ordinal. Consecutive fetch **CPU cycle gaps** must match *exactly*.
An overall constant cycle offset is reported explicitly, not
interpreted as perfect cycle-number identity or hidden by averaging.
The combined JSON report includes counts, observed bank IDs, verified
native conflict-fetch count, number of ordinary ROM-byte fetches,
and an offset, **never the source PCM byte payload**. When classified
hardware conflicts are present, `original_rom_byte_sequence_match`
is correctly `false`, while `actual_returned_dma_byte_sequence_match`
must be `true`. This does not relax source address, physical mapping,
event count/order or consecutive CPU-cycle gap checks.

Malformed/omitted/duplicated/reordered/altered reads, physical bank
changes, fixed-PRG31 misuse, **unclassified** ROM-byte mismatches,
mismatched native/Mesen returned bytes even for classified conflicts,
clock drift,
invalid epochs, bank-write/fetch contradictions, and truncated files
are all **hard failures**. A valid syntax-only CSV or fabricated
positive smoke fixture cannot establish an independently executed
retail game. The comparator cannot remotely attest which exact Mesen
binary, ROM or controller input was used by the owner.

## Tests and remaining game work

New ROM-free Python smoke suites:
`patch_mesen_dmc_reference_0651.py --smoke` validates strict source
anchors, the single real DMC read, and fail-closed duplicate
instrumentation. `jp_mesen_dmc_dma_compare_0651.py --smoke` compares
4 synthetic fetches spanning hypothetical mapper banks 17 and 3 plus
fixed PRG31, with 20+ deliberately damaged ordering/cycle/source cases.
Additional synthetic JP0650 sidecar tests cover an authorized
`$4015` DMC conflict and rejected missing/extra/forged records,
incorrect held CPU state, changes to Mesen's actual conflict byte,
unclassified Mesen corruption and cycle drift.
Both are wired into the existing Windows SDL2 Alpha and Linux NESRecomp
workflows. No real retail-JP game capture or MesenCE compile occurs in
these automated tests.

**Next evidence gate:** owner-local paired original Japanese game run,
with matched controller input and deterministic full-power-on epochs.
Only then can the reference/native real DMC DMA events be compared for
actual sound timing. Future work must also decode original music phrase
and SFX note voices before enabling JP0647's independent mixer.
JP0649 raw DPCM remains a bounded, offline decoder.

No new semantic decompilation credit (strict PRG 49,504/262,144 =
18.8843%, VPP27/100; checkpoint0508, frontier $FB96; R-002/R-007
OPEN). The working owner game audio stays untouched, modding remains
deferred until Enhanced Edition completion, and graphics issue #1
remains owner-resolved closed.
