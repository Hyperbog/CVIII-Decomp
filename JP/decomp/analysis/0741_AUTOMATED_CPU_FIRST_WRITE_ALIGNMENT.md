# JP0741 — Automated first-write comparison: execution boundary and gate

**Checkpoint:** JP0741 internal analysis; last owner-run gameplay test remains
**JP0722**. Existing retail gameplay evidence is from JP0718 MesenCE and older
JP0719 native snapshot replay. The later JP0732/JP0737 executable is a
different generation and must not be described as JP0719 owner validation.

## Concrete status

- Original owner-supplied Japanese Mapper24 ROM SHA-256:
  `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- Recovered original JP0718 archive SHA-256:
  `d2a54d01cbec9d4257d99df7a13a7b628fb41d59d5220bba66eb80c2a2f52878`.
- Recovered original-native JP0719 replay ZIP SHA-256:
  `ea18d677e232cb9fcc574d9453f064f335eacaa00e7ce2c567968ca0f2842aeb`.
- The original JP0718 recording contains 17,562 controller input polls. The
  JP0719 archived schedule matches all masks, but exact CPU $4016/$4017
  bus timing is not authenticated by those polls.
- Exact original MesenCE RAM/cycle anchor pairs extracted and checked:
  local frame **9,376** / CPU cycle **279,249,268**;
  **9,440** / **281,155,220**;
  **9,504** / **283,061,172**;
  **9,576** / **285,205,368**.
- Original recorded player Y (RAM $041C): 79, 80, 101, 155 at those frames.
  Action $0565: 20, 4, 12, 8. Scroll mode $62: 2, 1, 0, 1.
  Original coarse scroll $63 advances from $20 to $40 between
  frames 9,504 and 9,576.
- The older JP0719 native original-generation replay has nominal frame 9,560
  and 9,592 camera X=56 with $62=2 and $63=$20. These *aren't*
  cycle-matched to the original and must not be treated as exact instruction
  writes or native JP0737 playback.

## Local execution feasibility

In the current container, the original Japanese ROM and the two real
archives are accessible. Their ZIP CRCs and ROM hashes pass. The JP0740
synthetic trace parser and source overlay smoke tests pass, and extracting
the four original RAM/cycle anchors succeeds.

A compatible MesenCE executable, its Lua-capable original-Japanese game
runner, and the pinned NESRecomp native executable are **not installed**.
Direct network checkout/download of GitHub sources fails at DNS resolution.
Neither archived ZIP contains actual per-instruction CPU writes or a playable
native executable. Thus neither authentic JP0740 collector could be run
here; **there is no retail original-vs-native ordered CPU-write pair to compare**.

## New JP0741 comparison tool

`JP/decomp/tools/jp0741_first_write_compare.py` accepts two completed
JP0740 observed CPU bus traces and the exact original Japanese ROM,
reusing `jp0740_trace_verify.py` to insist on original historical
snapshot anchors and valid COMPLETE trace footers.

The new comparator requires a **unique trajectory** with at least **32
consecutive** events agreeing on:
- CPU bus operation, normalized RAM/controller address and bus mirror;
- written value and, for RAM writes, previous byte;
- opcode-entry CPU PC and mapped physical PRG location;
- the same **per-event relative CPU cycle differences**.

Overlapping matching 32-event windows of the *same* trajectory are correctly
consolidated; independent matching trajectories are rejected as ambiguous.
A source/native frame separation greater than 32 is rejected as an additional
sanity constraint, **not** used as proof of frame alignment. No match is
invented by shifting sample frames.

When exactly one trajectory is found, the comparator reports the **first
observed watched bus-event difference following the validated matching
prefix**. Such an event may be a consequence of earlier unwatched state
or controller/interrupt timing, so the output always states:
`first_incorrect_cpu_write_certified=false`. This remains true even when
the observed event is a write to **$62**, **$0565**, **$0520** or **$041C**.

Synthetic tests cover successful aligned prefix and subsequent write
difference, ambiguous repeated trajectories, a cycle-drift rejection, and
insufficient events. They do **not** add retail execution evidence.

## To complete the actual comparison

1. Acquire/build a compatible local MesenCE and the pinned NESRecomp engine
   in an environment with emulator binaries or GitHub source access. No new
   owner gameplay session is needed.
2. Run the canonical JP0740 original Lua recorder under the original JP0718
   input schedule **from the correct power-on input origin**. Require exact
   recorded original RAM and CPU-cycle anchors, not approximate state.
3. Replay the same controller intent on the current opt-in native runtime;
   require its own COMPLETE CPU-write recording and physically mapped PCs.
4. Run JP0741 on the two completed traces; validate a unique aligned event
   trajectory. If divergence is reported, use surrounding full CPU registers
   and original-ROM instruction provenance to establish causality before
   any game-behavior patch. Distinguish differences at $4016/$4017 from
   different state writes.
5. A bounded patch is admissible only after a reproducible incorrect writer
   is confirmed, regression evidence exists, and the original ROM byte
   identity is retained.

**No live instruction parity or root cause is established. No game logic,
mapper/PPU, controller data, or additional native handlers changed.**
Certification unchanged: **31/100 VPP**, **49,504/262,144** strict PRG bytes,
and checkpoint **0508**.
