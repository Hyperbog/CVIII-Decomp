# CVIII Japanese Castlevania III — Enhanced Alpha 0.2

Version 0.2.0-alpha.1. The original C11 Windows Alpha 0.1 was
owner-tested through Stage 4-0A, including Sypha and character switching.
The NEW experimental extra-sprite Enhanced renderer requires owner QA.


**JP0605 product direction:** One public **Enhanced Edition**. Use
`Play-CVIII.bat` (or `Build-And-Play.bat` for first-time setup).
The historic Original/Enhanced dual-launcher descriptions below are
development history only. Original PPU presentation remains an
**internal reference path** (`Launch-Alpha.ps1 -Edition Original`),
not a separate player-facing edition. Unverified improvements,
including experimental unlimited sprites, are **off by default**.
The shared Stage A-01 pixel corruption and the Stage 1 sprite
overlap reports remain open; this launcher change does not fix either.

## First-run setup — JP0603

The public ZIP contains **only a ROM-free build kit**. It is NOT a
playable game download: there is deliberately no game EXE or SDL2.dll.
Extract the entire ZIP to a writable folder and double-click
**Build-And-Play.bat**. Select the unmodified original Japanese
Akumajou Densetsu .nes ROM in the file picker. After the initial private
C11/SDL2 Windows compilation, the original game will launch.

You can also double-click **Play-CVIII.bat** directly; if this is the public kit rather than a private compiled
candidate, they invoke the same first-run builder automatically.
The setup validates the exact Japanese ROM and looks for Git, CMake,
Python and Visual Studio 2022 MSVC x64 tools before building.
It creates the private executable and SDL2.dll side by side at:

    %USERPROFILE%\CVIII-Alpha\AlphaCandidate\

The original game is compiled ONLY on your own Windows PC, not in
GitHub CI or in the public downloaded kit. Build logs live under
`%USERPROFILE%\CVIII-Alpha\logs\`. Once compiled, subsequent
launches reuse the private result without rebuilding (unless you run
`Build-And-Play.ps1 -Rebuild`). A private
`%USERPROFILE%\CVIII-Alpha\LastRomPath.txt` saves **only the original
ROM path**, so Play-CVIII no longer repeatedly opens a file
dialog. If you move the ROM, delete that path hint to reselect it. The kit never downloads a DLL from
an unrelated site. See the FIRST failing build-log entry if setup
does not complete.

Manual alternative:

Build privately on Windows (CMake, Visual Studio, Git, Python and the
unmodified original Japanese Akumajou Densetsu ROM required):

    powershell -ExecutionPolicy Bypass -File .\Build-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes"

The build kit downloads pinned NESRecomp PolyForm Noncommercial source
to a separate private directory and compiles the original owner ROM into
a local executable. The public build kit contains no ROM or game code.

After build, double-click Play-CVIII.bat in the
private AlphaCandidate directory. For internal comparison only,
developers can use Launch-Alpha.ps1 -Edition Original with the
authenticated Japanese ROM. That is not a separate player product.
The launchers authenticate original Japanese mapper24 ROM SHA256 and
prompt for the cartridge when not supplied.

Enhanced is the sole public launcher. Its initial graphics use the
stock PPU output while the shared mapper/PPU defect remains under
investigation. Optional all-primary-OAM sprite compositing is experimental
and disabled by default; enabling it requires separate owner QA.
CPU/PPU-visible gameplay, sprite-0 hit, IRQ, DMA and collisions remain
original by default. The internal Original PPU path is reserved for
technical A/B diagnosis, not presented as a product edition.

Default input: arrows=movement; Z=A; X=B; Enter=Start;
Backslash=Select. The NESRecomp SDL host supports configurable
keyboard/controller bindings. Builds with the 0591 slot extension
support Ctrl+0..9 slot selection plus F8/F9 save/load.

Not yet supported: true widescreen level geometry, individual channel
gain, independent soundtrack/SFX voices, remastered audio or texture
replacement, and optional new moves. The Stage 2/3?/4-0A shared
background-layer artifacts remain an unresolved Original issue.

Focused authentic-ROM validation: Original and Enhanced 600-frame
headless CPU/PPU/memory hashes match byte-for-byte. This is not
full-game/Windows Enhanced GUI certification. Do not distribute the
copyrighted game EXE, ROM or third-party sound/assets publicly.

## Private Windows stage and companion debug picker

New AlphaCandidate private builds include Debug-Stage-Companion.bat.
Double-click it (Python 3 with Tkinter required); choose a stage/checkpoint,
None, Alucard, Sypha or Grant, and the same name used at game name-entry.
Copy the displayed 4x4 password grid and enter its symbols manually
on the game's password screen. Password symbol keys: W=whip,
R=rosary/cross, H=heart, .=blank.

The original game's Normal difficulty only supports some partners
on each route. The picker rejects unavailable combinations. Hard mode
may allow the combination but changes the game difficulty. This is
an external test aid, not an in-game F10 debug menu, not mid-game warp
or RAM-based companion injection. The Japanese live password path
still needs acceptance testing on the original compiled game.

## JP0594 F10 stage and companion checkpoint warp (new private build)

Inside either Original or Enhanced gameplay, press **F10**. The game
pauses. Up/Down chooses one of 18 stage checkpoints; Left/Right chooses
None, Alucard, Sypha or Grant. **Enter** loads a previously captured
whole-machine checkpoint for the selected stage and companion (true
instant stage warp). **F5** captures the *currently running game*
as the selected stage/companion checkpoint; **Esc/F10** resumes.

Each checkpoint is a separate `saves/<ROM>.debug.stageNN.partnerN.cycstate`,
compatible with the original full-machine F8/F9 serializer. Saving a
checkpoint does NOT create or add a companion: capture when the selected
companion is already actually in the game. Likewise, **a stage cannot
warp before its compatible checkpoint exists.** One can reach it naturally
or start with a valid password and capture once; subsequent stage jumps
are immediate. Checkpoints are specific to the native executable build
and may need recapturing after recompilation. Slot 0..9 saves are separate.
No ROM patching, unproved RAM writes or gameplay state fabrication.
The separate password picker still helps seed a stage from the title.
This initial F10 implementation requires a new private Windows build
and has not been owner-playtested.

## JP0595 password clipboard controls

The external `Debug-Stage-Companion.bat` window now has **Paste
password** as well as Copy. Paste a 4x4 grid of W/R/H/. marks;
the tool checks the original player name, checksum and companion-route
legality before selecting its stage, companion and difficulty. This
does not yet type a password into the NES game automatically.

## JP0595 in-game password clipboard shortcut

Open F10 and press Ctrl+V to paste a 4x4 W/R/H/. password grid.
The ROM-authenticated checksum and stage selector are decoded,
and the current F10 stage and companion are selected accordingly.
Press Enter to load the corresponding PREVIOUSLY CAPTURED checkpoint.
No game CPU RAM, password entry or stage initialization is changed.
F10 cannot yet start an uncaptured stage; the external Python
password tool checks the name as well and can help seed it manually.

## JP0596 one-time password-screen bootstrap (Windows private Alpha)

This is a substantial improvement for testing multiple unvisited stages.
Preserve the original Japanese password system and ordinary New Game paths.

**Once per compatible native executable:** From the original title menu,
open the game's Password feature, enter your test player name and reach
the 4x4 password-entry screen. Press **F10**, then **F6** to capture that
original screen as a reusable whole-machine bootstrap checkpoint. F6
refuses to capture when the original game's $0019 menu state is not $08.

After that, at any point in gameplay press **F10**, use Up/Down for the
18 checkpoints, Left/Right for None/Alucard/Sypha/Grant, and **Tab** to
select Normal/Hard difficulty. Press **Enter**:
- If the corresponding stage/partner/difficulty snapshot already exists,
  it loads instantly (unchanged 0594 behavior).
- Otherwise the engine loads the single original password-screen snapshot,
  encodes a new stage password using the name in that actual saved screen,
  and fills original Japanese password RAM $0790..$079F. **Confirm the
  password using the game's normal confirm control** to begin the level.

The original JP password decoder performs the real game-state and route
initialization; F10 does not pretend it can jump directly to arbitrary
stage code. Normal mode still rejects route-impossible companions; Hard
can admit additional combinations but changes game difficulty. Ctrl+V
inside F10 still selects a checkpoint from a pasted password, and the
external Python picker still supports full password copy/paste.

The bootstrap loading path backs up the current entire machine and rolls
back on a wrong menu state or any RAM-write failure. The existing saves
are preserved; Hard-mode checkpoints use a distinct file suffix. Both
Original and Enhanced can use the **development-only** F10 tool.

**Validation status:** GitHub Windows synthetic UI/C11 compilation does
not establish real JP password acceptance or the first successful
transition. The exact $0019 state, active password UI and subsequent
stage initialization require owner/private Windows or independent Mesen
frame tracing. Treat this as a development test feature until confirmed.


## JP0597 private versioned ROM asset package

Build-Alpha.ps1 now generates or verifies a local **CVIII-Assets.bin**
under AlphaCandidate. It is derived from your authenticated Japanese
mapper24 ROM and included ONLY in the private output/ZIP. The package
is a deterministic ZIP-format archive with a JSON manifest, SHA256 of
every entry, all **128 physical 1 KiB CHR pages (8,192 tiles)**,
all 524,288 decoded CHR palette-index pixels, and the six ROM-confirmed
password tables with physical bank addresses. These are raw physical
CHR tile indices, not final colored sprites or decoded room backgrounds.
The archive preserves every raw CHR byte and tests lossless re-encoding.

To regenerate independently, run (from an up-to-date repo checkout):

    python JP/tools/jp_asset_pack_0597.py --build --rom "C:\Games\Akumajou Densetsu (Japan).nes" --out "C:\Games\CVIII-Assets.bin"

To validate a cached package without reopening the retail ROM:

    python JP/tools/jp_asset_pack_0597.py --verify --out "C:\Games\CVIII-Assets.bin"

A repeated private build reuses an intact package. On a corrupt,
outdated or incompatible archive it fails closed: run the same
--build command with --rebuild to regenerate it from the authenticated
original cartridge. Original-JP assets remain copyrighted and local;
never publish or attach CVIII-Assets.bin to public Git or CI.

**Phase boundary:** The current Original/Enhanced native executable
still executes the original game's ROM-derived native code and requires
the authenticated ROM at private compilation/launch. Neither edition
reads CVIII-Assets.bin yet. Substituting it for the ROM or claiming
renderer parity would be premature. Future stages will identify CHR
bank/register changes and game level/animation structures, then
switch only verified Enhanced presentation reads to the package.

## JP0598 — Read-only CHR cache loaded by Enhanced (first integration gate)

The private Alpha builder now exports **CVIII-CHR-Index.dat** alongside
CVIII-Assets.bin. On Enhanced launch only, the host loads this fixed-size
(655,368-byte) cache through `--asset-index`. The standalone C11 index
reader checks exact geometry, magic, the pinned Japanese CHR content
identities and a complete **tile-by-tile 2bpp reconstruction**.
The Python exporter also verifies the canonical SHA-256 of the original
CHR and decoded tile index. Corrupt or wrong-ROM data fail closed.

**No game rendering has been redirected.** The NESRecomp PPU remains
authoritative for Original *and* Enhanced; no CPU, PPU, APU, VRC6 or
game-state writes are made. This creates a validated in-process CHR
source for later Enhanced rendering without assuming static graphics
can replace the original hardware's changing bank/palette registers.

Original launch does not request the cache. An Enhanced run with
no cache falls back to unchanged ROM graphics. In the private Windows
builder the cache is regenerated only when needed and remains local;
public CI uses synthetic pixels, not copyrighted cartridges.


## JP0599 — Optional VRC6 CHR mapping audit

JP0598 gave Enhanced a verified read-only cache of every original JP
CHR tile. JP0599 now observes which physical bank each of the eight
PPU pattern windows selects at **sampled frame boundaries**, plus
the current PPU palette RAM. To generate a private CSV:

    powershell -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Edition Enhanced -ChrAudit

The opt-in **CVIII-CHR-Audit.csv** is created beside the private EXE.
It records one sample per 60 emulated frames: VRC6 mode/control,
eight physical 1-KiB bank IDs, current 32 PPU palette bytes, and
PASS/FAIL of an independent bank-map calculation against NESRecomp's
reported CHR offsets. Original retains its existing unmodified PPU
presentation; Enhanced does not yet draw from this cache.

**Scope limit:** A frame-end sample cannot see a bank switched in
and out during a scanline. This is not yet proof of pixel/scene
rendering parity. No user gameplay modifications are enabled by
the diagnostic. The editor remains a deferred future product.


## JP0600 — Actual PPU pattern-fetch cache parity, no renderer substitution

With a privately built Japanese Alpha, use the existing opt-in
**-ChrAudit** parameter on **Launch-Alpha.ps1** with **-Edition Enhanced**.
This now produces two separate owner-local reports:
- **CVIII-CHR-Audit.csv** — JP0599 end-of-frame VRC6 CHR bank selection
  and palette RAM every 60 emulated frames.
- **CVIII-CHR-Fetch.csv** — JP0600 sampled *actual PPU pattern reads*
  with the physical CHR-ROM page, cached 2bpp byte/indexed-pixel
  reconstruction parity, and observed CHR bank changes **within each
  scanline**. The native host only observes one out of 60 frames.

Example (run in your private AlphaCandidate directory):

    powershell -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Edition Enhanced -ChrAudit

Validate/summarize the fetch log (Python tool is in JP/tools in the
repository, and requires no ROM for this analysis):

    python JP/tools/jp_chr_fetch_report_0600.py --csv "C:\Games\CVIII-CHR-Fetch.csv" --require-parity

The report lists total sampled pattern reads, bad cached bytes,
invalid mapped addresses, encountered physical CHR pages per PPU
window, and within-line bank changes. A nonzero exit from
--require-parity means that at least one observed read disagreed
with the loaded cache or had an invalid mapping.

**Limitations:** Synthetic CI establishes the instrumentation
interface and checks trace rules, but a privately observed Japanese
retail gameplay trace is still needed to establish acceptance in
real stages. The hook observes pattern reads, not all nametable
accesses, pixel priority or complete rendered-frame equivalence.
Neither Original nor Enhanced currently substitutes cached CHR data
for the stock PPU image. F10/password stage testing is unchanged.

## JP0601 — Synchronized original PPU frame evidence (diagnostic-only)

The opt-in Enhanced `-ChrAudit` private launch now produces an additional
**CVIII-Frame-Evidence.csv** aligned to the JP0600 1-in-60-frame pattern
fetch capture. Each sampled original NES PPU frame records:

- The sample frame number and the actual CHR read/mismatch/invalid counts
- Observed CHR bank switches during sampled scanlines
- Deterministic 64-bit checksums of the PPU's original 9-bit color indices
  (color and emphasis), background-opaque mask, and 240 scanline scroll/mask
  records serialized without C structure padding
- Background opaque pixel count and number of scanlines with background or
  sprite rendering enabled

These hashes are **original PPU observations**, never graphics generated
from the cache. Neither edition changes its default presentation or game
state. The report joins source-byte observations and original PPU outcomes
on the same sampled frames, rejecting missing frames, inconsistent read
counts, bank switch totals or malformed fingerprints.

When launched with `-Edition Enhanced -ChrAudit`, the private launcher
generates **CVIII-Frame-Evidence.json** after the game exits and requires
cache/PPU fetch-source-byte parity. To rerun the validation manually:

    python jp_frame_evidence_report_0601.py --fetch CVIII-CHR-Fetch.csv --evidence CVIII-Frame-Evidence.csv --require-parity

The original retail Japanese game still needs a local Windows GUI playtest
spanning multiple stages and companion routes. Successful source-byte
comparisons and original PPU fingerprints **do not establish independent
cache-backed sprite/background framebuffer parity**. Enhanced still renders
using the original PPU except for separately opted-in experimental effects.
This diagnostic milestone does not increase strict PRG/VPP semantic coverage.


## JP0602 — Private owner-only scene QA matrix

The JP0600/0601 frame/fetch observations are now collected without
overwriting earlier scenes. Use the new **Capture-QA-0602.ps1** in the
private AlphaCandidate directory:

    .\Capture-QA-0602.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Scene village-entry -Area village -Character Trevor -Kind gameplay -Checkpoint 1-01

This starts the real Japanese native game with Enhanced mode's **stock
NES PPU presentation** and the read-only CHR diagnostics. Play the
declared scene and close the game. A distinct folder under local QA/
retains the five evidence CSV/JSON files and an authenticated
capture.json including the owner's ROM fingerprint, current native
EXE/CHR-index hashes and each evidence file's SHA256. Nothing is
automatically uploaded. **Scene/stage labels are user-supplied
annotations, not independent proof of which level was entered.**

Other suggested -Area values: title, clock_tower, forest, ship,
castle, boss and companion; set -Character to Trevor, Sypha, Grant
or Alucard where appropriate. Capture at least 10 sampled frames
per scene (about 600 emulated frames); one out of 60 frames is
instrumented. A shorter capture is retained but reported as shallow.

Then aggregate all local sessions:

    python .\jp_qa_matrix_0602.py --root .\QA --json .\QA\CVIII-QA-Matrix.json

Or pass --require-coverage to ask the checker to fail until all eight
target scene areas have sufficiently sampled trace evidence.
The checker verifies source-ROM declaration, per-file hashes, all
JP0600/0601 original PPU and physical-read count consistency and
stage/character scene coverage. Corrupt captures fail closed.
Different native executable fingerprints are reported, not silently
treated as same-build deterministic comparisons.

**Still not proven:** The actual retail Japanese game has not been
sampled across these routes here. Source CHR-byte matches and
original-PPU fingerprints do not demonstrate independent cached
renderer parity. Original's renderer, gameplay and F10 controls are
unchanged; Universal NES Studio remains future work.

## JP0604 — Git command invocation fix

The earlier first-run builder accidentally invoked bare Git without
the requested `clone` arguments. The cause was using PowerShell's
automatic `$Args` variable as a command-argument parameter.
The builder now supplies `-CommandArguments` explicitly for every
Git and Python subprocess. Windows CI extracts the **actual function**
from `Build-Alpha.ps1` and performs a real Git clone and pull using
a synthetic local repository with spaces in both paths.

**If your build showed Git's general help instead of cloning:**
use the newest ROM-free Alpha Builder Kit. Extract/replace its
`Build-Alpha.ps1` in the folder you run `Build-And-Play.bat` from.
Re-running the builder is safe: the original ROM stays unchanged and
any existing private `CVIII-Alpha` output is reused or refreshed.
Do not reinstall Git or download an SDL2.dll from an unrelated site.

## JP0606 — Stage A-01 shared PPU background corruption investigation

The first JP0606 slice adds **read-only actual nametable and attribute
bus read tracing**, not a speculative rendering change. The pinned
NESRecomp VRC6a mapper's common `$B003 = $20/$24/$28/$2C`
mirroring logic is consistent with NESdev's documented mode-0
behavior, so no hardware mapping is modified without gameplay
evidence. The shared Stage A-01 pixel corruption remains an open
defect in both reference/Enhanced rendering paths.

Rebuild the private native Enhanced candidate and launch Stage A-01 with
`Capture-QA-0602.ps1`. The captured scene folder contains an extra
`CVIII-NT-Fetch.csv` and `CVIII-NT-Fetch.json` in addition to the
preexisting QA-matrix evidence. Every sixtieth emulated frame the new
hook observes actual PPU nametable tile and attribute bytes, their
nametable/CIRAM-versus-cartridge source, timing and per-scanline hash.
The report checks that these samples align with the original PPU
frame fingerprints. Explicit empty samples represent frames with
rendering disabled during title transitions.

These extra JP0606 files do not alter the v1 QA manifest's expected
five files, preserving backward compatibility with older owner
captures. They remain in the same private scene directory for targeted
Stage A-01 analysis and comparison against MesenCE.
There is still **no** retested retail Stage A-01 screenshot proving a
graphics fix; ROM-free CI only verifies the observer, bus report,
private native build, and existing original-frame hash invariants.

## JP0607 - Python not found / Microsoft Store App Execution Alias

The private Windows builder now checks for a **working Python 3.10+
interpreter**, rather than accepting Windows' built-in python.exe
Microsoft Store alias as an installed Python. It tries py -3, python,
and python3, actually executing a tiny validation script for each.
An alias that exits with 9009 is rejected, with installation guidance.

Official installer: https://www.python.org/downloads/windows/
Enable the Python launcher or Add Python to PATH. Open a new
PowerShell window after installation and run:

    py -3 --version
    python --version

At least one should report a real Python 3.10 or newer. If Windows
still redirects to the Store, disable python.exe / python3.exe under
Windows Settings > Apps > Advanced app settings > App execution aliases.

The builder loads the resolver from its freshly updated repository,
so an older extracted kit can work by replacing just Build-Alpha.ps1
with the current version. New kit ZIPs and compiled AlphaCandidate
also package Resolve-Python.ps1 for development QA scripts.
No ROM, game data or save files need to be deleted.

## JP0608 — Optional sprite-history layers (experimental)

The owner reports continued Stage 1 Trevor/torch and doorway flicker
even with UnlimitedSprites enabled. Pinned NESRecomp already renders
all 64 OAM-present sprites over the independently captured background;
it cannot recreate sprites missing from an entire frame's OAM.

The new optional -StableSprites switch captures the two-bit sprite
pixels independently, paints them in original OAM priority order,
and holds unmatched previous-frame pieces for exactly one extra frame.
Transparent pixels, behind-background priority, sprite-enable and
left-edge clipping are preserved. Large changes in OAM population
suppress ghosting; power-on and state loads clear history.

After privately rebuilding the Windows Alpha, run:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -StableSprites

This is host presentation ONLY. Collision, PPU status, CPU, IRQ,
sprite zero and game OAM remain unmodified. It can temporarily ghost
animated sprites, and frame-end CHR mapping still may not reflect
mid-scanline CHR bank switches. Experimental and off by default.
Retail-Japanese Trevor/torch and doorway validation is outstanding.
Stage A-01 background corruption is unrelated and still unresolved.

## JP0609 — Stabilize sprite priority using original PRG26 object order

The original Japanese PRG26 NMI sprite renderer advances $22 by
$44 (17 hardware OAM slots) each frame, then places emitted sprites
at consecutive byte positions spaced by $C4 (-15 physical slots).
Because the NES gives lower physical OAM slots higher priority,
two overlapping pieces can repeatedly exchange foreground/background
priority even when neither is missing. Increasing OAM capacity or
holding last-frame sprite pixels does not remove that priority swap.

JP0609 changes only the optional Enhanced -StableSprites compositor:
it reverses the original physical OAM permutation, draws sprites in
stable logical emission order, then overlays current sprites above
any one-frame rescued pieces. There are NO changes to NES OAM, IRQ,
DMA, sprite zero, CPU state, collisions or gameplay. This is a
hypothesis-driven change, with a synthetic reproducer but NOT yet
a proven retail-JP Trevor/torch fix.

An optional -SpriteTrace captures read-only per-frame $0400-$04C3
game-object arrays and actual 64 PPU OAM slots. The tracer and
analyzer can show whether physical priority swaps while logical
order remains stable, or whether the game drops sprite entries.
The report files are CVIII-Sprite-Objects.csv and .json, private.

After building the newest private Windows AlphaCandidate, run:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -StableSprites -SpriteTrace

Play the first village torch overlap for 5-10 seconds, close the game.
Compare against the same scene with -StableSprites omitted. The
original known A-01 background corruption is a SEPARATE issue.
No HD art, widescreen, gameplay changes or public Original edition
is included in this milestone.

## JP0610 — Music/SFX conflict research (no audio changes yet)

The owner reports effects muting or cancelling other effects and
requests true independently mixed music and SFX. Current original
hardware has 2A03 pulse1/pulse2/triangle/noise/DMC plus VRC6
pulse1/pulse2/saw voices, with one shared register state per voice.
The Japanese PRG bank0C sound scheduler/metadata is partially
authenticated (JP0533/0534) but NOT semantically separated into
independent music-versus-effects producers. An SDL volume slider
or two outputs from the same mixed hardware signal would NOT fix
source-level cancellation.

JP0610 adds *read-only* original 2A03/VRC6 CPU audio register
write instrumentation to the private native runtime (two overlays
over the pinned external NESRecomp hardware sources). It logs
address, value, old register value, CPU cycle, voice, and fast
reprogramming events without modifying CPU, sound registers,
VRC6 voices, mixer output, or game timing. The log is limited to
1,000,000 rows and flushed periodically. These are hardware writes
only: effects discarded by the game before register writes are
invisible to this trace. Classification of actual music/SFX callers
and the separate polyphonic synthesizer remain future milestones.

After rebuilding your private Windows AlphaCandidate, run:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Edition Enhanced -AudioTrace

Cause two effects to overlap, then close the game. Owner-only
`CVIII-Audio-Registers.csv` and `.json` are written alongside the
launcher. Compare the report with original Japanese-game audio; do
not commit original sound samples, NSF or generated ROM-derived data.

Next audio build after this baseline: identify per-event sound
requests, track their scheduling/cancellation priority in the
original bank0C driver, and re-synthesize music and SFX as separate
independent host voices. Only then can separate volume, reverb
and spatial effects be added without silently dropping notes.

## JP0612 — Original sound-request entries alongside chip-register traffic

Rebuild your private AlphaCandidate and use `Launch-Alpha.ps1 -Edition Enhanced -AudioTrace`. In addition to the existing `CVIII-Audio-Registers.csv`, the same session writes owner-only `CVIII-Sound-Requests.csv`. Each recorded original fixed-$E249 CPU entry includes the incoming sound command, CPU cycle, X/Y/S/P, tracked bank $23 and two **uninterpreted** stack bytes. The hook captures either compiled or interpreter-fallback opcode fetches and skips fetches discarded for interrupts. Neither gameplay nor music/SFX output is changed. Commands suppressed before reaching $E249 are not captured; CSV entries are not proof of independent voices, source priority or original waveform parity. The real Windows retail-ROM trace remains to be checked against MesenCE.

## JP0614 — Paired audio capture session safety

With a freshly built private AlphaCandidate, use Launch-Alpha.ps1 -Edition Enhanced -AudioTrace. The launcher now collects CVIII-Sound-Requests.csv, CVIII-Audio-Registers.csv and CVIII-Audio-Epochs.csv; on successful exit, writes CVIII-Audio-Session.json with new GUID and SHA-256 bindings plus CVIII-Audio-Epoch-Verification.json. A loaded saved game begins a new analysis epoch even if CPU cycles rewind. Whole-file JP0610 register analysis is skipped for multi-epoch sessions; JP0613 request/voice proximity is still noncausal. No ROM, sound, PPU, gameplay, or native mixer behavior changes.

## JP0615 — Optional independent Mesen sound-request verification

The private AlphaCandidate kit now includes jp_mesen_sound_requests_0615.py and mesen_jp_sound_requests_0615.lua alongside the JP0614 provenance verifier. For a valid comparison, retain a **single power-on epoch** native -AudioTrace capture and separately replay the identical controller inputs/duration on the SHA-pinned Mesen2 v2.1.1 original-JP ROM agent. Run the JP0615 tool against that private Mesen JSONL and AlphaCandidate directory. Compare sound entry A/X/Y/S/P/software $23 bank/stack; request interval cycle deltas are independent findings. Arbitrary manual play, save-state load epochs, empty output or a different original route cannot establish parity. No audio, music/SFX scheduler or gameplay changes.

## JP0616 — Original Japanese sound priority gate evidence

JP0616 tools ship read-only: jp_sound_priority_paths_0616.py (original ROM bytecode and bounded CPU branch evaluation, with synthetic --smoke), mesen_jp_sound_gates_0616.lua (optional original Mesen execute callbacks for $8842/$884F/$8860 and $8908/$8922/$8928) and jp_mesen_gate_report_0616.py (original emulator JSONL state/pair verifier). The original $884F guard and $8922 DMC early return are source-proven, but not yet live in matching native gameplay. Run the independent original ROM Mesen reference privately; never upload game traces, save states or ROM. There is no change to Enhanced's 2A03/VRC6 audio output, music/SFX volume or independent voices.

## JP0617 — Independent original sound driver decision proof (owner-only)

The private AlphaCandidate kit now contains mesen_jp_sound_decisions_0617.lua and jp_sound_decision_reference_0617.py. Run the Lua observer against the exact Japanese original ROM with a SHA-pinned Mesen2 agent. It observes original CPU $8852 after STA $EF, records $0109/$019E/$06DD and one branch terminal per request. Metadata $885D reset and $8860 installation are one two-stage request. Run the verifier with --rom, --emulator and --mesen-stdout; optionally --native-dir for an authenticated JP0614 single-epoch command-order comparison with matching input script and run duration. The committed --smoke fixture is synthetic only. This does not enable new audio voices, recover SFX suppressed before $E249, or change sound output.

## JP0618 — Enhanced audio preferences (foundation; final health-bar UI pending)

Enhanced is the sole shipping edition, but retains original Akumajou Densetsu gameplay as the mechanical baseline; fixes and improvements are intentional, opt-in or tested changes. The new private native host stores `MasterVolume`, `MusicVolume` and `SoundEffectsVolume` in its normal [Game] config, default 100 each, constrained to 0–100 in steps of 1. Only Master currently affects the mixed 2A03/VRC6 PCM. To test it now, run `Launch-Alpha.ps1 -Edition Enhanced -MasterVolume 50` (optional; no parameter means use persisted settings). Music and SFX require actual independent audio buses and **do not affect sound yet**. The final player menu will use the game's actual health-bar art for all three left/right sliders and original font for the 0–100 numeric readouts; that interface is not implemented here. Original gameplay state, APU timing and sound-register writes are not altered.

## JP0619 — Original game health-bar audio options preview (not yet interactive)

The latest Enhanced private build includes an optional **noninteractive developer preview** of the future Master, Music and SFX sliders: `Launch-Alpha.ps1 -Edition Enhanced -AudioUiPreview`. The overlay draws original Japanese-ROM CHR tiles (health-meter filled $1093 / outlined $1085, pixel font digits $1041–$104A and Latin capitals $1050–$1069), not imitation graphics. The launcher requires its previously authenticated private `CVIII-CHR-Index.dat`. Numeric 0–100 values reflect JP0618's saved settings; orange fill clips across 144 pixels as a 1% volume changes. The preview **does not pause gameplay or accept left/right/up/down controls** and must not be described as finished audio settings. It is off by default. The shipping Enhanced edition still uses original gameplay behavior as the baseline. Current Master gain is live, but Music/SFX remain saved values until independent audio buses are implemented. Use the preview only for visual QA; original palette exactness and native Windows GUI tests remain open.

## JP0620 — Enhanced F6 original-art audio menu (owner Windows QA required)

The windowed Enhanced candidate now builds with an **F6 audio-options modal** layered on the pinned NESRecomp SDL host. Its actual Japanese-ROM CHR health bar tiles and in-game font show Master, Music and SFX values (0–100, 1% steps). **F6** opens/closes; Up/Down chooses a row; Left/Right adjusts 1 at a time (keyboard repeat supported). Gamepad D-pad navigates/adjusts, and gamepad **B or Start**, keyboard **Escape or Backspace**, close the menu. Rebuild the owner-private executable with the latest source before testing. Opening requires `CVIII-CHR-Index.dat` and Enhanced; it is not activated by the old `-AudioUiPreview` flag.

The modal uses the existing host's pause-frame/input-release gating and saves settings on adjustment. The original-art panel plainly says **MUSIC SFX PENDING**: Master audio gain is implemented, but Music/SFX saved values are not sound gains until independent buses exist. RGB color matching to the original HUD still needs verification. The F6 path is independent of optional `recomp-ui` (which this repository's Windows CI disables). **Real owner Windows GUI/keyboard/gamepad/pause/save persistence has not been independently run here**; tests presently cover synthetic SDL source anchors, C11 menu registry and artwork rendering. The future combined Start/Pause menu with Save State, Load State, Audio and Quit and mod pages is not implemented.

## JP0621 — F6 audio menu pinned-source verification gate

For the current Enhanced F6 audio menu, private and CI builds now include `JP/tools/jp_audio_menu_pinned_gate_0621.py`. It requires the exact upstream NESRecomp `runner/cyc/cyc_sdl.c` Git blob and in-memory successful 0591→0594→0596→0620 patch chain. This catches upstream source drift and missing pause/input guards, and verifies F6's priority so it does not accidentally replace the F10 password-debug shortcut. From the repository root, use `python JP/tools/jp_audio_menu_pinned_gate_0621.py --source _external_nesrecomp/runner/cyc/cyc_sdl.c` with the pinned external checkout. The new gate is wired to Windows and Linux CI, but has **not yet produced an independently checked new CI or private Windows gamepad/playback result**. F6 audio menu still needs owner GUI/audio/save-persistence QA before asserting playable completion.

## JP0622 — F6 Audio menu state hardening

[JP0622](../../analysis/0622_ENHANCED_AUDIO_MODAL_STATE.md) makes the host's original-healthbar F6 audio menu navigation a separately testable C11 controller. The menu still requires Enhanced plus the authenticated owner-local CHR index. Master/Music/SFX values remain 0–100, 1% adjustments, with Music/SFX audio outputs explicitly pending separate source buses. The host now closes stale menu state after a power/reset or load-state transition and when switching out of Enhanced. The C11 exact-source regression PASS locally; Windows/real gamepad/native framebuffer/playback verification remains outstanding. The future combined menu Save State/Load State/Audio/Quit is not yet built.

## JP0623 — Expandable Enhanced F4 Start/Pause menu (owner Windows QA outstanding)

After rebuilding the latest private Enhanced Alpha, **F4** opens the Start/Pause menu with authentic Japanese-ROM pixel font. It requires the authenticated private `CVIII-CHR-Index.dat`. Keyboard **Up/Down** navigates, **Enter** selects, **F4/Escape/Backspace** closes; with the menu already open, gamepad **D-pad Up/Down** navigates, **A** selects, **B/Start** closes. **Opening on a gamepad is not yet bound** so NES Start remains a gameplay button. Entries: **Save State**, **Load State**, **Audio**, **Quit**. Save/Load operate on the **current quick-save slot**, chosen during gameplay using `Ctrl+0..9`; graphical slot selection is pending. Audio opens the existing F6 health-meter/font volume controls (Master effective; Music/SFX are stored-only until separate audio buses). Quit requires selecting Quit twice. All 4 actions have stable namespaced IDs, and the C11 registry is sized for more entries, but a player mod loader/editor is not implemented.

The private fifth SDL patch reuses the host's normal paused-frame and input-release logic, corrects F4/F6/F10 vs developer-key priority, and never changes original NES gameplay hardware state. ROM-free **strict C11 tests PASS locally**, while five-layer source generation on the real pinned upstream, owner Windows build, actual keyboard/controller/paused-gameplay and save/load calls are **not yet verified**. These are planned player controls in committed source, not a playtested release guarantee. See [JP0623 evidence](../../analysis/0623_MOD_FORWARD_START_PAUSE_MENU.md).

## JP0624 — Start/Pause action integration test

`JP/tools/jp_start_pause_shell_test_0624.py` imports the **actual JP0623 F4 menu SDL action source fragment** and compiles a ROM-free fake-host regression in offline and netplay configurations, linked against the real Start/Pause registry. Linux CI runs this strict C11 test; Windows CI runs `--smoke` to check exact source extraction. A locally mirrored C11 host fixture PASS in both offline and netplay modes, but the precise source-generated harness and full pinned native Windows SDL build have not yet been independently executed here. This is development-side action/input safety coverage, not a new menu control or a certified owner gameplay build.

## JP0625 — In-menu Save/Load slot chooser (build owner QA outstanding)

In the latest Enhanced F4 Start/Pause source, **Save State** and **Load State** now open their own original in-game-font screen listing the selected quick-save slot **0–9**. Up/Down or Left/Right (keyboard and gamepad D-pad) adjusts by one with wraparound; Enter/gamepad A confirms, Escape/Backspace/B returns to the parent without saving/loading, and F4/gamepad Start closes the menu. The selected slot is applied to the pinned host's existing full-machine Save/Load handlers, not to a new incompatible format; `Ctrl+0..9` and F8/F9 game shortcuts still work. These visuals require the authenticated private `CVIII-CHR-Index.dat` file. The original game input and emulated timing are intended to be unchanged while outside modal UI.

**Verification status:** strict C11 unit + original-font renderer tests PASS locally; pinned six-layer SDL generation, new CI outcomes, actual owner Windows/gamepad/native slot file round-trip are pending. A source commit alone is not proof of playable Alpha acceptance.
