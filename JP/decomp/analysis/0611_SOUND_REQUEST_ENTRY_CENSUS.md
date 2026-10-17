# JP0611 — Fixed $E249 sound requests: authenticated dispatcher and caller-pattern census

**Scope:** Original Japanese Akumajou Densetsu, Mapper 24, full ROM SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
This is a **physical-byte discovery pass**, not a live call-graph proof or an audio modification.

## Original sound entry and dispatch (ROM evidence)

Fixed PRG31 `$E249–$E263` (`5a5d7b8a...37324` SHA-256, full digest pinned in audit)
accepts the command in A, sets `$26=$FF`, saves tracked VRC6 bank `$23`
into `$25`, maps raw bank `$0C` with `$E2D0`, invokes `$8850`, clears
`$26`, and restores the prior bank through `$E2D0`. Its wrapper is
**not** an independent music/SFX bus.  The following distinct paths are
encoded in the authentic raw-`$0C` `$8850` bytecode:

| Incoming A | Original control branch | Evidence limit |
|---|---|---|
| `$00–$4F` | `$8842` state check | Not a music-only classification |
| `$50–$6E` | `$87AE` reset, then `$8F5E+2*A` sound-record pointer installation | Metadata does not prove independent SFX ownership |
| `$6F–$FF` | `$8908`: subtract `$6F`, gate against `$019E`, select `$A957`-family data and write `$4010–$4013/$4015` | DMC programming is visible; earlier discarded events are not |

The previously audited **conditional** bank-`$0A` `$B58C` immediate `$6B` call
is a specific example in the middle path. JP0508 Phase 11 established its
six bank-`$05` stream installations and natural return; this does not establish
all callers' NMI/frame liveness.

## ROM-wide call-pattern census (structural only)

ROM byte patterns `20 49 E2` (`JSR $E249`) and `4C 49 E2`
(`JMP $E249`) occur **123** and **8** times, respectively, over the
entire 256 KiB physical PRG. **115 JSR** and **5 JMP** candidates are
immediately preceded by `A9 nn` (`LDA #nn`) within the same 8 KiB
physical bank: **120 constant-pattern candidates**, grouped by the
hypothetical incoming command into 91 low, 17 metadata-install and 12
DMC-command candidates. The remaining **11** have no such immediate
prefix and need actual producer and A-register traces.

A physical byte pattern is **not** a proven instruction. Preceding
`A9 nn` does **not** establish a valid instruction boundary, incoming
accumulator value, mapper state, or reachability. This census must not
be relabeled as 131 live sound requests, 120 distinct effects, or any
fixed music/SFX ownership map. In particular it must not be used to
change the original driver's event priority or mute behavior.

Reproduce, with no commercial sound/ROM bytes written to Git:

```sh
python3 JP/decomp/tools/jp_sound_request_census_0611.py "$ORIGINAL_JP_ROM" --self-test
python3 JP/decomp/tools/jp_sound_request_census_0611.py "$ORIGINAL_JP_ROM" --json /tmp/jp0611_sites.json
```

The script authenticates the whole ROM and four address-specific source
witnesses, validates both branch thresholds and DMC register writes,
checks candidate totals, and rejects four independent source-byte
mutations. Its optional site list stays owner-local and contains only
physical offsets and candidate opcodes/IDs, no lossless ROM stream.

## Next original-execution evidence boundary

Instrument the **entry into fixed `$E249`** in the private native runner,
recording CPU cycle, CPU PC, mapped PRG bank, A/X/Y, caller stack return,
`$019E/$0109..$0111` sound state and eventual APU/VRC6 writes. Compare
with independent original Japanese MesenCE event/caller traces. Distinguish
accepted commands from suppressed commands **before** attempting
polyphonic virtual voices or music/SFX gain sliders. Track tail-jump
callers separately: their stack provenance differs from JSR callers.

**Accounting:** No new verified semantic PRG bytes. Strict floor remains
`49,504/262,144 (18.8843%)`, VPP `27/100`, certified semantic checkpoint
`0508`, fixed investigation frontier `$FB96`. This research is JP0611,
not checkpoint `0509` completion or native audio output parity.
