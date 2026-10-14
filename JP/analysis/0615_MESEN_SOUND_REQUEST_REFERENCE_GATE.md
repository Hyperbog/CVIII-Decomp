# JP0615 — Independent original Mesen2 sound-request reference gate

**Status:** ROM-free comparison fixture PASS; a matched-input, original-Japanese-ROM Mesen2-versus-native runtime comparison has **not** been performed. Sound-event ownership and output parity remain OPEN.

## Research question and scope

JP0614 binds the native E249 command, 2A03/VRC6 register and save-state epoch CSVs by SHA-256. It does not establish whether native E249 event state matches the original ROM independently run in Mesen2.

The new [Lua observer](../tools/mesen_jp_sound_requests_0615.lua) registers MesenCE/Mesen2's documented NES CPU execute callback at fixed PRG31:$E249 and reads CPU A/X/Y/SP/P, cycleCount, the game's **software-tracked** bank shadow $23 and two raw stack bytes. It emits a bounded private JP0615_REQ record per execution, with no emulated writes or sound modification. The CPU-state field names and callback API are documented in MesenCE; actual compatibility with the project's **pinned Mesen2 v2.1.1 agent** remains untested without a reference execution.

The [strict comparator](../tools/jp_mesen_sound_requests_0615.py) requires the exact original 393,232-byte JP ROM hash 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28 and separately authenticated Mesen-agent and MesenCore.so executable hashes previously pinned at JP0508. Reference agent JSONL must establish a successful original 2.1.1 NES frame-limited run, no Lua errors, no truncated callback log and at least one original E249 entry. Native evidence must pass the JP0614 GUID/SHA-256/epoch verifier, with exactly one power-on epoch.

For each request ordinal, compare original/native CPU command, X/Y/S, software bank $23 and raw stack bytes, masking only the virtual status bits 4/5 (P & $CF). Success means **request-register sequence equality in the provided pair**, not agreement on NES PPU/APU, full game timing or soundtrack. Inter-request cycle deltas are checked and reported separately. Two recordings are only meaningfully comparable when system region, reset state, controller inputs and run horizon are equivalent.

## New original-JP source-address observations

Authenticated raw bank $0A, physical PRG21, contains three mechanically aligned five-byte immediate-load sound-call sequences:

| CPU source | Authenticated bytes | Meaning |
|---|---|---|
| $B0C8 | A9 06 20 49 E2 | Candidate command $06; low-command branch |
| $B1CE | A9 6A 20 49 E2 | Candidate command $6A; reset/record-install branch |
| $B58C | A9 6B 20 49 E2 | Command $6B; reset/record-install branch |

Only the third is independently exercised on a **conditional** original-ROM 6502 path by [0508 Phase 11](0508_PHASE11_FINDINGS.md). Do not infer liveness for the other two, classify either as music/SFX, or identify dropped game-side requests from byte patterns. The JP0615 ROM-gate checks all three spans.

## Reproduce privately

First rebuild AlphaCandidate from the latest branch and generate a **single-epoch** JP0614 capture by running Launch-Alpha.ps1 -Edition Enhanced -AudioTrace from original reset with no save/load. Retain the three CSVs and GUID manifest together.

Run a real, independently maintained original-ROM Mesen2 / mesen-agent execution with matching inputs and duration. For example, the preexisting original 0508 name-entry route can be used to generate the reference, but will not be comparable to arbitrary manual native play:

    mesen-agent "$JP_ROM" --home "$PRIVATE/original0615" --frames 520 --input '0:start@90-92' --input '0:start@180-182' --input '0:start@300-302' --input '0:right@370-520' --lua JP/tools/mesen_jp_sound_requests_0615.lua > "$PRIVATE/mesen0615.jsonl"

Compare while retaining raw files exclusively outside Git:

    python3 JP/tools/jp_mesen_sound_requests_0615.py --rom "$JP_ROM" --emulator "$MESEN_DIR" --native-dir "$PRIVATE/AlphaCandidate" --mesen-stdout "$PRIVATE/mesen0615.jsonl" --json "$PRIVATE/jp0615_compare.json"

ROM-free CI gate:

    python3 JP/tools/jp_mesen_sound_requests_0615.py --smoke

The synthetic smoke covers matching entries, changed command ID, wrong emulator version, truncated capture and an unsuccessful reference run. This run did not have the matching private Mesen2 binary, native audio capture or original emulator output. Therefore **no original-versus-native runtime parity claim** can be made.

**Remaining R-007:** obtain actual paired independent original execution and matched native input route; then trace producer provenance, delay/suppression decisions and sound-register/PCM output. New strict PRG bytes **0**; strict total **49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint **0508**, fixed frontier **$FB96**. RESUME_STATE.json unchanged.
