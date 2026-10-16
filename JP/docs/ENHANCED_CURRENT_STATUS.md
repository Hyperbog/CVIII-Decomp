# Enhanced Edition — Current status (JP0643)

Reconciled with the owner's October 2026 gameplay feedback.
This is the **current product status**, not a replacement for the
chronological decompilation notes.

## The working player-facing baseline

- **One public Enhanced Edition**, with faithful original Japanese
  Akumajou Densetsu gameplay as the default. The internal `Original`
  runtime mode is retained for engineering A/B checks, not a separate
  public product.
- The owner reports that the native Windows game runs correctly.
  The earlier rendering artifact (Stage 2/3?/4-0A/A-01 discussion)
  is **resolved by owner confirmation**. [Issue #1](https://github.com/Hyperbog/CVIII-Decomp/issues/1)
  has been closed as completed. This is not a technical pixel-parity
  certificate or an identification of a particular fix commit.
- The current published public kit is documented as
  **0.2.0-alpha.1**: an owner-ROM-authenticated local Windows build kit,
  **not** a downloadable copyrighted game executable.
  Historical owner validation extends through Stage 4-0A, including
  character switching with Sypha. Later host/menu features may not
  yet have undergone an owner gameplay pass.

## Implemented source, with remaining acceptance limits

| Component | State and limitations |
|---|---|
| Native Japanese game and public Windows launcher | Playable owner-tested baseline; user supplies authenticated original JP ROM |
| Save states | F8/F9 and Ctrl+0..9 native slots; JP0644 now rolls back the chosen quick slot on failed I/O and keeps the picker open for retry; real owner-file round-trip still pending |
| Enhanced F4 Start/Pause | Source-implemented Save, Load, Audio and two-step Quit, game-authentic pixel font, modal pause and input release; source/C11 tests pass; F4 opens by keyboard, gamepad operates menu after opening |
| Enhanced F4 Save/Load chooser | Original font, 0–9 slot picker, uses existing whole-machine serializer; new GUI/real save-load acceptance pending |
| Enhanced F6 Audio | Health-bar and original-font menu with 1% Master/Music/SFX sliders; nested Audio returns to parent Pause; latest owner UI acceptance pending |
| Master volume | **Working**, applied to final mixed PCM in Enhanced mode |
| Music/SFX sliders | Stored settings only; **not** independent sound gains or voices |
| JP0647 independent virtual mixer | **Implemented**: bounded 8 music + 24 SFX synthetic PCM voices, separate virtual gain controls, no voice stealing, reset-safe handles. **Dormant** in real gameplay: original sound programs and PCM producers not yet recovered; real Music/SFX sliders remain preferences only. |
| JP0648 original DMC command source | Original-JP-authenticated 15 four-byte DMC programs ($6F..$7D) and pure six-register-event planner, with original priority and $06DD side-effect model. Unsupported high commands fail closed; **not** a playable DPCM generator. |
| JP0649 original DPCM sample ranges/bit decode | **Implemented, dormant:** SHA-authenticated 15 descriptors covering 8 distinct CPU sample spans in switchable VRC6 $C000–$DFFF, plus NTSC/PAL per-bit period geometry and raw 7-bit DAC decoding for caller-supplied PRG bank8. Live mapper bank/DMA phase and real game audio remain unverified. |
| JP0650 native DMC DMA physical-bank observer | Opt-in owner-only --dmc-dma-trace from actual DMC bus gets and VRC6 $C000 bank-write intents: mapped physical source offsets, returned bytes, cycle/epoch and validated ROM-byte reporting; truncation explicitly rejected. Real original-game capture and independent Mesen parity pending. |
| JP0651 independent MesenCE DMA reference pair | **Implemented, ROM-free tested:** SHA-pinned optional MesenCE DMC-only source hook and strict one-to-one native/reference address, mapped PRG offset, byte and inter-fetch cycle comparison. Real original-JP paired emulator execution and MesenCE build acceptance still pending. |
| Experimental sprite enhancement | Opt-in extra-OAM compositor and stable sprite history/priority; JP0645 now uses original PRG26 OAM-rotation emission identity to prevent duplicated animation ghosts, with 64-sprite synthetic CI; default off, owner gameplay acceptance pending; issue #1 stays closed |
| Original ROM asset package | Authentic private CHR/package/index and read-only tracing are implemented, **not** an installable texture override |
| F10 stage/companion tools | Debug-only checkpoint/password bootstrap, not public game progression |
| JP0641/JP0642 scenario/replay tools | Versioned preflight and private reference/native frame-budget orchestration; synthetic CI passed, genuine per-frame parity not demonstrated |

The pinned seven-stage native SDL chain successfully passed Windows
Alpha builder and Linux NESRecomp integration GitHub Actions at JP0639
(runs 38829146730 and 38829147219). The independent scenario
contract passed Windows and Linux at JP0642 (run 38833423691).
Those results validate build/instrumentation, not all new UI features
on the owner's actual Windows desktop.

## Not yet delivered as Enhanced player features

- Independent music and sound-effects voice pools, mixing, and true
  Music/SFX volume gains (issues #3 and #6).
- Player-installable, versioned symbolic-ID texture/resource override
  packs with deterministic fallback (issue #8).
- True extended-world widescreen camera/view (issue #5).
- Player-facing control-rebinding UI and persistent profiles (issue #7).
- Optional multidirectional whip/new mechanics (issue #9), not part of
  faithful baseline behavior.
- Full mod/plugin SDK, mod loader, editor and alternate soundtrack packs.
- Owner QA of newly added F4/F6 menus, actual Save/Load slot files,
  input suppression, UI pause/resume, and keyboard/controller focus.

## Recommended next product milestones

1. **Current native Enhanced release candidate QA:** rebuild privately
   and verify F4/F6/Save-Load/Audio-to-Pause input, save persistence,
   real state round-trip and controller interactions. Accept the
   graphics issue closure; do not invent a new renderer defect.
2. **Complete optional Enhanced sprite presentation:** compare
   actual rendered scenes in owner builds, keep original mechanics
   unchanged, and fix only observed sprite regressions. This is
   independent of the already-closed graphics issue #1.
3. **Authentic original Music/SFX virtual producers:** JP0647 now
   provides the independent 8+24 PCM mixer; recover one actual
   original Japanese song and competing effects, prove command/voice
   ownership and timing, then connect the decoded producers and real
   Music/SFX gains behind a reversible Enhanced-only setting. Keep
   original hardware emulation for CPU/gameplay state.
4. **Custom controls:** complete player-facing keyboard/controller
   rebinding and persistent profiles with a recoverable default.
5. **True widescreen:** render additional verified scene geometry;
   never stretch the 256x240 original bitmap as a substitute.
6. **Full Enhanced Beta acceptance:** exercise stage routes,
   companions, bosses, audio, saves and menus in actual gameplay,
   then release a stable Enhanced Edition.
7. **After release only:** modding infrastructure, user-installed
   texture/resource packs, soundtrack swaps, editors and optional
   gameplay modules. Do not put these on the active pre-release queue.

## Latest integration — JP0644

The seventh-layer generated SDL shell now passes compiled offline and
netplay tests with the real menu/slot/audio-controller C models, covering
transactional failed Save/Load, retry/cancel, nested Audio parent return,
modal input ownership and double-confirm Quit. The Windows SDL2 native
candidate builder and Linux external NESRecomp integration CI both passed
at commit `279da91c` (runs 38836167641 and 38836167331). These are
**synthetic-media integration results**, not real controller/save-file owner
acceptance. See [JP0644 evidence](../analysis/0644_ENHANCED_MODAL_TRANSACTION_AND_SDL_HARNESS.md)
and [owner menu QA](../release/alpha/QA_ENHANCED_MENUS_0644.md).

**Product scope reminder:** all modding features are explicitly deferred
until the Enhanced Edition is complete and stable.

## Latest gameplay-facing Enhanced work — JP0645

The optional StableSprites compositor now pairs animated sprite pieces
by logical PRG26 emission identity despite rotating physical OAM slots,
with one-to-one matching and conservative fallback. The original Japanese
PRG26 `$22 += $44` and OAM `X += $C4` opcode windows were checked on the
actual owner cartridge, not inferred from an invented ROM. A ROM-free
4,096-case phase/slot inverse audit is included. Both the Windows SDL2
candidate and Linux NESRecomp native integration passed, including the
new 64-piece animation and one-frame ghost tests (runs 38838450762 and
38838450730). **StableSprites remains opt-in/off by default** until owner
stage-specific visual QA; original gameplay and issue #1 resolution are
unchanged. Modding remains outside pre-release scope. See [JP0645](../analysis/0645_STABLE_SPRITE_EMISSION_ANIMATION.md).

## Latest audio-engine research integration — JP0646

A private owner-only `--sound-decision-trace` can now record
**native original driver control-flow decisions**, not merely sound
request entry points. The ROM-backed original PRG0C branch classes are
low-command gated return, low install, metadata install, DMC priority
return and DMC programming. It records original RAM snapshots and
flags invalid event order rather than attributing an effect to a song.
The read-only reporter is disabled by default and leaves the working
native sound, 2A03/VRC6 registers, CPU/PPU timing and gameplay intact.

New synthetic C11 decision-stream and pinned-source patch tests plus
full Windows SDL2 Alpha and Linux Mapper24 backend builds **passed**
(runs [Windows 38841999987](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38841999987),
[Linux 38842000015](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38842000015)).
No independent Music/SFX playback or effective separate output gains
were delivered; these **still require** matched original-game sound
events and virtual voices. Actual owner private retail-game trace
capture/independent Mesen comparison remains outstanding (R-007).
See [JP0646 evidence](../analysis/0646_ORIGINAL_SOUND_TERMINAL_OBSERVER.md).

## Latest Enhanced audio core — JP0647

The **production virtual PCM mix infrastructure is now implemented**:
8 independent music voices, 24 independent SFX voices, independent
Music/SFX/Master gains, and bounded deterministic callback rendering.
The native host owns dormant voice state and clears it on game power-on
and state load. No original Japanese song/effect decoder or event-based
virtual producer has been validated, so **real game playback remains
unchanged** and the Music/SFX UI sliders still only store preferences.

The Windows SDL2 Alpha and Linux NESRecomp integration runs **passed**
([Windows](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38847041444),
[Linux](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38847041479)),
including both C11 audio suites and a 10,000-sample synthetic
Music+SFX scenario with bit-identical output across three buffer sizes.
These are **not** proof of real Japanese-game separate audio playback.
See [JP0647 evidence](../analysis/0647_INDEPENDENT_VIRTUAL_AUDIO_BUS.md).
Owner-tested original gameplay remains the baseline. All modding
features remain deferred until Enhanced Edition completion.

## Original Japanese DMC source milestone — JP0648

A bounded subset of the actual Japanese sound programs is now
**source-authenticated and structurally decoded**: original 15
DMC program descriptors for commands $6F..$7D, the original DMC
priority gate and the six-write control sequence. The reusable host-only
C11 decoder constructs read-only abstract register-write plans; no
DPCM sample bytes, original sound events or PCM samples are generated
for gameplay, and the verified 2A03/VRC6 output remains authoritative.
The event planner is dormant in the native binary until it has an
authenticated original-RAM producer and full sound-sample bank
mapping.

Both [Windows Alpha](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38848854199)
and [Linux NESRecomp](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38848854194)
builds succeeded, with 3,840 synthetic command/priority pairs tested on
each platform, invalid-command refusal and original metadata SHA
checking in the private ROM audit. See
[JP0648 original DMC evidence](../analysis/0648_AUTHENTIC_DMC_SOUND_PROGRAMS.md).

Authentic DPCM playback, original game-to-Mesen sound event matching
and live independent Music/SFX controls remain **NOT DELIVERED**.
R-007 is still open. Default game unchanged; modding remains deferred.

## Latest original-DPCM evidence and bounded decoder — JP0649

The exact original Japanese ROM contains 15 DMC sound descriptors
targeting 8 unique sample CPU spans, fully inside switchable VRC6
$C000–$DFFF. Two variants loop. The physical 8 KiB PRG bank depends
on actual VRC6 $C000 register state, so JP0649 accepts only an
explicit external bank8 snapshot and **does not guess** original
live sound memory mapping.

The dormant production 2A03 DPCM helper validates the preceding
JP0648 six-write event plan and one physical PRG bank, computes
byte/bit counts and NTSC/PAL idealized period sums, and decodes one
bounded raw bitstream into 7-bit delta DAC levels. It is **not**
CPU-DMA-cycle-accurate, not the final audible effect producer,
and never changes verified original gameplay sound or JP0647
Music/SFX slider semantics.

Original-ROM authentication and a ROM-free C11/Python regression
matrix passed; both Windows SDL2 Alpha and Linux NESRecomp native
workflows passed (runs [38850407597](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38850407597)
and [38850407592](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38850407592)).
See [JP0649 technical evidence](../analysis/0649_DPCM_MEMORY_AND_TIMING.md).

Next audio gate: observed original mapper8 state at DMC DMA fetch,
full sample-buffer/CPU timing and independent Mesen/native waveform
comparison, followed by actual sound producers. R-007 remains OPEN.

## Latest native DMC DMA source tracing — JP0650

The owner-private native runtime now has read-only hooks at the exact
2A03 DMC DMA bus-get and VRC6 $C000 bank-write routes. Each actual
DMA read can be correlated to its true physical PRG offset at fetch
time rather than guessing a bank from original sound data. The
Japanese-ROM CSV validator reports bank/byte inconsistencies and
refuses malformed/truncated recordings. It never modifies CPU/mapper/
APU state, original PCM, save states, or the native game.

Windows SDL2 Alpha and Linux NESRecomp full integration passed at
commit 374c0477, including new source-overlay and strict C11 parser
tests: [Windows](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38851826980)
and [Linux](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38851827004).
**No actual owner Japanese gameplay capture or independent original
Mesen DMC sample DMA parity is certified**, and Music/SFX remains
not independently playable. See [JP0650 owner capture and evidence]
(../analysis/0650_DMC_DMA_FETCH_AND_MAPPER_TRACE.md).

Default original audio preserved, modding deferred, R-007 open.

## Latest independent DMC reference comparison infrastructure — JP0651

An independent MesenCE source-pinned hook is now authored for the
genuine DMC sample-transfer branch, not for normal CPU, OAM or
dummy reads. It records actual sample fetch byte, CPU address,
physical mapped PRG offset and cycle to an opt-in owner-private
reference log when a privately built pinned MesenCE emulator runs.
The Python comparison rejects mismatched/missing/truncated source
events, wrong cartridge offsets, altered sample bytes, inconsistent
mapper state and any inter-fetch CPU cycle gap disagreement. It
reports a constant absolute-cycle offset without hiding it.

The cross-platform Windows SDL2 Alpha and Linux NESRecomp workflows
passed strict ROM-free Mesen-source patch and reference/native
pairing tests ([Windows](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38854153989),
[Linux](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38854153973)).
**MesenCE was not compiled or executed in these workflows**, and
**no matched original-Japanese retail gameplay pair was observed**.
A real original-JP CPU/DMC mapper timing claim remains unproven
until owner-local pinned MesenCE build and identical-route comparison.
See [JP0651 evidence and private instructions]
(../analysis/0651_INDEPENDENT_MESEN_DMC_DMA_REFERENCE.md).

The existing playable game audio stays untouched. Authentic Music/SFX
producers are not yet implemented; JP0647 virtual mixer remains
dormant. R-007 open; all modding still deferred.

## JP0652 sound-program source directory (not independent playback)

A ROM-authenticated, read-only catalog now enumerates every original JP indexed
sound descriptor: **125 program IDs**, **325 bank-qualified source references**
(139 raw0C, 102 raw04, 84 raw05), and **15 original DMC source slots**. Its
private JSON output contains no stream payload or sample PCM but may expose
reconstructible commercial descriptor metadata and must remain private.
The full directory, stream pool and DMC table are individually SHA-pinned.
See [JP0652 source catalog](../analysis/0652_COMPLETE_ORIGINAL_SOUND_DIRECTORY.md).

This is not music/SFX voice ownership or a functioning separate audio bus.
The game sound path remains unchanged, JP0647 independent virtual voices
remain dormant, and original-game Mesen/native parity is unverified. R-007
stays open; no source PRG/VPP promotion or new public mod API.

## JP0653 — Original phrase lookup, native-source parity only

The two original Japanese sound phrase-pointer consumers now have a
read-only source-derived C11 resolver. Their indexed source spans are
**128 entries at $A304 and 20 entries at $A404**, with an 8-bit
high-selector alias. The 148 source words have 140 distinct physical
roots covering 1,323 original bytes. Bounded original-opcode/NMOS 6502
vs native C11 tests passed 3,072 cases on the owner's authenticated
Japanese ROM. [JP0653 source evidence](../analysis/0653_ORIGINAL_SOUND_PHRASE_POINTER_NATIVE.md).

This is not an audible phrase decoder, live game sound request replay
or working separate Music/SFX controls. The C11 code is linked but
dormant; the 2A03/VRC6 output remains unchanged. R-007 remains open;
strict semantic PRG and VPP are unchanged.

## JP0654 — NSF static source evidence only

The supplied 28-track Japanese NSF and original Japanese game ROM have
been physically crosswalked. Eleven of the rip's 13 4KiB banks are
byte-identical, but the rip replaces original raw0C $A000–$A2FF and
raw03 $BFF0–$BFFF. The original JP0653 phrase pool, JP0652 sound
directory and JP0648 DMC parameters are preserved byte-for-byte.
[NSF source and modification audit](../analysis/0654_ORIGINAL_JP_NSF_ROM_CROSSWALK.md).

An owner-local, read-only audit confirms source identity and exposes
ROM-free synthetic regressions. The NSF's song INIT/PLAY and synthetic
virtual bank state must not be confused with actual original-game
scheduler/mapper/AUDIO behavior. **No Enhanced gameplay or sound
implementation was changed**, and Music/SFX production remains
unimplemented (R-007 open). Strict source certification/VPP unchanged.

## JP0655 — Authentic ordinary-byte phrase arithmetic (native, dormant)

An original Japanese SHA-pinned PRG0C source lift now reproduces
the $8D15–$8D8F 6502 arithmetic, including cursor advancement,
a repeated-add 8-bit multiplier and 16-bit signed-direction
carry/borrow updates. The original source/control byte boundary
is **$FB**. A compiled, read-only C11 helper matches 5,610
isolated original 6502 paths and passes 385,536 ROM-free tests.
[JP0655 evidence and reproduction](../analysis/0655_ORIGINAL_PHRASE_ARITHMETIC_NATIVE.md).

This helper is **compiled but not connected to actual playback**.
Music/SFX voice ownership, original mapper/DMA timing, sound
event trace parity and authentic gameplay liveness remain open
(R-007). The original sound output and player experience are
unchanged. The existing 49,504-byte strict certificate and VPP
27/100 remain unchanged.

## Independent historical decompilation metrics

Strict semantic PRG **49,504 / 262,144 (18.8843%)**;
VPP **27/100**; certified checkpoint **0508**;
fixed PRG31 frontier **$FB96**; room-loader R-002 **OPEN**.
None measures the percentage of the playable game that works.
