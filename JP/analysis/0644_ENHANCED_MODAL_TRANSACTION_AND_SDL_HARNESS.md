# JP0644 — Transaction-safe Save/Load and executable seven-layer menu regression

**Focus:** protect the working Japanese game while hardening Enhanced UI. This
checkpoint changes no original 6502/PPU/APU logic, ROM bytes, state-file schema,
CHR art, renderer, audio mixer, or user-gameplay progression.

## Confirmed source integration defect

The JP0625 generated native SDL Save/Load picker previously called
`cviii_pause_slot_accept(&selected)` (which clears the child picker),
assigned `cviii_save_slot=selected`, and invoked the existing pinned
NESRecomp `save_state_slot` or `load_state_slot`. When the host returned
false, the **global quick-save slot stayed changed despite failed I/O**,
and the child slot screen had disappeared without successful serialization.

JP0644 keeps the original host serializer and error notification. The
generated SDL fragment now snapshots the previous slot, temporarily selects
the requested file during I/O, and only keeps it on success. On an I/O failure
it restores the previous global slot and reopens the child picker at the
user's desired slot. The existing native host's failed-state notification
remains authoritative; no duplicate failure message is invented. Retry
reuses the same requested slot; B/Escape cancel returns to the parent
without changing the current quick slot. Successful I/O still closes the
parent modal and uses exactly the old full-machine save format.

This is source/host UI behavior, *not* a claim that a failed low-level
savestate loader is globally atomic in every error circumstance.

## Executable integration evidence

`JP/tools/jp_slot_shell_test_0625.py` now compiles and executes the actual
sixth patched C action shell against the real game-owned slot controller,
including **failing SAVE and LOAD callbacks**, preserved old slot,
preserved pause/child, retry, cancellation, and success, under strict C11
and `NESRECOMP_NET` configurations. `jp_slot_picker_pinned_gate_0625.py`
requires the failed-I/O transaction guard in the actual pinned-source
seven-stage chain. Its negative-source smoke rejects missing anchors.

New `JP/tools/jp_menu_roundtrip_shell_test_0644.py` assembles the
actual JP0623 F4 action shell, applies JP0625's actual Save/Load
transformation and JP0626's actual nested-Audio return transformation,
then links the real host-independent action, slot, audio-level,
audio-controller, and modal-stack C modules. It validates offline
and netplay opening restrictions and a bounded sequence:

1. Enhanced/CHR prerequisites and netplay-open refusal.
2. Save fails in slot 1 while active host slot 0 is unchanged;
   the screen remains open at slot 1; next successful retry commits 1.
3. Load fails in slot 2 while active slot 1 remains; cancel leaves it
   unchanged; reopening, selecting 2 and loading commits 2.
4. F4 → Audio keeps the F4 parent and selected row resident.
   F4 cannot close the hidden parent while Audio is open.
5. Music slider step remains a **saved preference**, not an
   independently working Music PCM gain. Closing Audio restores
   parent focus and the same-event pause predicate remains true.
6. Closing the parent returns gameplay-key ownership;
   standalone F6 closes to gameplay.
7. Quit still requires two deliberate accepts.

The stubbed SDL host **never writes an actual state file, runs a ROM,
presents a window, starts playback, or feeds physical controller events**.
Compilation/execution of this exact generated fixture on Linux plus
Windows source-smoke and complete pinned-source Windows SDL compilation
are independent CI gates; a new owner-private Windows GUI check is still
required. Failure to build must not be reinterpreted as gameplay failure.

## Manual owner QA (new build required)

See [Enhanced UI acceptance checklist](../release/alpha/QA_ENHANCED_MENUS_0644.md)
for minimal final signoff, including deliberately failed load on a
missing slot and no save-file deletion.

## Certification

Strict semantic PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508,
fixed PRG31 frontier $FB96 and R-002 OPEN. Graphics issue #1 stays closed
after owner resolution. Modding, new mechanics, and renderer research remain
deferred.
