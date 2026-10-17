# JP0646 — Native original-Japanese sound-driver terminal observation

**Scope:** independent of the existing playable game and Enhanced audio
output. Introduces an **explicitly opt-in**, read-only trace of the actual
Japanese PRG0C sound command dispatch boundaries. No music/SFX mixer, new
voices, game-state patch, APU/VRC6 emulation change, or audio feature is
presented as complete by this checkpoint.

## Why this work is necessary

The owner wants Enhanced Music and SFX not to steal hardware voices.
The original Japanese game has shared hardware APU/VRC6 register voices.
Splitting one already-mixed PCM stream cannot reconstruct source notes.
The previous JP0612 native trace recorded an entry at fixed PRG31:$E249
but omitted original driver `$0109`, `$019E` and the *actual terminal
decision* after the bank-switch wrapper. The JP0617 independent-Mesen
observer could distinguish the five branches, but had not obtained an
authenticated original gameplay capture. Assigning command IDs to
"music" or "effect" without matching requests to real state is unsound.

## Implementation

New `cviii_sound_decisions_0646.c/.h` owns a bounded, owner-private
CSV logger, activated only with:

```sh
/path/to/jp_akumajou_densetsu "/private/Akumajou Densetsu (Japan).nes" \
  --edition enhanced \
  --sound-decision-trace "/private/CVIII-Sound-Decisions.csv"
```

Use the same authenticated Japanese ROM and private executable as the
existing Alpha launch process. Without the option the logger has no
open file and never emits rows.

The CMake build creates a **second private overlay** from the original
JP0612 generated `cviii_hw_machine_requests.c`, never from modified
retail ROM or committed NESRecomp code. The single existing helper is
still called from both `hw_read` and `hw_read_rom`, so interpreter and
compiled execution paths are observed. It rejects a discarded NMI/IRQ/
reset opcode fetch, requires mapper 24 and matches RAM $23==$0C,
$26==$FF (the original sound wrapper context), and *reads* only
PRG0C:$8852/$885D/$884F/$8860/$8922/$8928. Each PC is also guarded
by its original Japanese opcode byte. Unexpected bytes are explicitly
logged as `invalid_opcode`, never counted as valid sound terminals.
The existing $E249 JP0612 observer is preserved unchanged.

The new CSV fields are:
`event,id,cycle,pc,command,low_state,priority,counter`.
Entry at $8852 occurs **after** original `STA $EF` and records RAM
$EF command, $0109 guard, $019E DMC priority, and $06DD counter.
Events carry unique in-process IDs, monotonic cycles within one epoch,
and one optional metadata marker at $885D. Terminal outcomes:

| Command | Original source predicate | Terminal |
|---|---|---|
| $06–$4F, $0109==$50 | gated low command | `low_return`, $884F |
| Other $00–$4F | lower path | `low_install`, $8860 |
| $50–$6E | JSR $87AE metadata phase then install | `meta_install`, $8860 |
| $6F–$FF, `index=A-$6F` less than old $019E with old priority >=5 | original DMC gate | `dmc_return`, $8922 |
| Other $6F–$FF | original DMC programming path | `dmc_program`, $8928 |

This is **control-flow evidence**, not a claim that hardware writes
occurred, that an effect was inaudible, or that a music channel was
identified. The counter, low-state and priority columns contain
observed values, not fabricated independent voices.

Malformed input order, nested entries, orphan decisions, invalid
opcode witnesses, invalid metadata phases, mismatched terminals,
in-flight reset/state load and CPU-cycle regression are explicitly
marked `invalid_*` rather than silently producing positive reports.
Power-on and state-load are separate marked epochs; logger state is
not included in game savestates and cannot affect guest save files.
The trace is capped at 100,000 rows, with internal overflow counts.

## Validation and operational boundaries

- ROM-free C11 tests exercise **all five original decision outcomes**
  plus malformed ordering, corrupted opcodes, nested/orphan decisions,
  reset/load epochs, nonmutation of a synthetic 2 KiB RAM snapshot
  and log schema. An exact-source Python patch smoke rejects duplicate
  application and missing pinned JP0612 anchors.
- Windows and Linux CI compile the real pinned external
  NESRecomp mapper24 integration, and execute the same standalone
  native logger against a synthetic original-style machine state.
- Original retail-JP **source bytes for these branch predicates**
  were authenticated in JP0616, not newly credited here.
  A *live* Japanese retail gameplay capture and independent-Mesen
  matched state are still **NOT EXERCISED** by public CI.
- A companion future verifier must compare native CSV request/terminal
  sequence to independent JP0617 Mesen trace, with matched input and
  epochs, before promoting any actual owner/gameplay liveness claim.
- This is an incremental first step toward **true independent source
  Music/SFX voices**. Do not connect its output to the current sound
  presentation or mislabel Music/SFX sliders as effective yet.

## Product and accounting

The already working game is the immutable baseline; issue #1 stays
owner-confirmed closed; StableSprites stays opt-in. Modding remains
deferred until the Enhanced Edition is finished.
Strict semantic PRG = 49,504 / 262,144 (18.8843%);
VPP = 27/100; checkpoint0508, frontier $FB96, R-002 OPEN.
The sound-ownership investigation R-007 remains OPEN.
