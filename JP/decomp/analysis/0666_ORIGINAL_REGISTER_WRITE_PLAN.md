# JP0666 — Authentic source-constrained 2A03/VRC6 register writes (detached)

## Exact scope

JP0665 recovered original Japanese *Beginning* soundtrack program `$51` and the six bank05 roots (`0,1,2,3,4,7`). This checkpoint is **only** the bounded *melodic note to period register* path in raw05 `$811F–$822D`, exiting at `$86DA`, with original `$8274–$8298` detune helper and `$8314` APU write-gate helper. Original raw05 bytes are authenticated against the owner-only 393232-byte Japanese cartridge and historical interpreter-core SHA.

JP0666 supports original descriptor modes `0–4`, not percussion mode `7`. It reads the genuine *caller-provided*, authenticated original JP bank05 pitch tables; no copyrighted tables, notes, stream bytes or score are committed. The source-byte *high nibble* selects pitch-table entry via `($note&$F0)>>3`. The source's `$01A8,X` byte is a positive or sign-and-magnitude negative pitch-table offset. Negative underflow uses the original special lower pitch tables at `$8713` (non-saw) / `$875B` (saw); otherwise `$872B` / `$8773`. After table lookup, original `$01A3,X` octave value produces right-shifts of the 16-bit period until the value `5`. Then original `$0195,X` detune signed-byte operation adds or subtracts its magnitude modulo 65536.

The **exact 6502 register store address, value and store order** for this bounded path are:

| Original descriptor mode | Destination writes (nominal order) | Conditional |
| --- | --- | --- |
| 0 VRC6 pulse 1 | `$9001` low, `$9002` high OR `$80` | always two within this state envelope |
| 1 VRC6 pulse 2 | `$A001` low, `$A002` high OR `$80` | always two |
| 2 VRC6 saw | `$B001` low, `$B002` high OR `$80` | always two |
| 3 APU pulse 1 | `$4003` high OR `$08`, `$4002` low | high write may be suppressed by `$0163/$011B/$017E`; both suppressed if `$010E !=0` |
| 4 APU pulse 2 | `$4007` high OR `$08`, `$4006` low | same with `$010F` |

The non-obvious **APU high-byte write-before-low-byte order** follows authentic `$81AD–$81EC`, rather than the low-first sequence used for VRC6. The `$0163,X` high-byte cache can change even when `$010E/$010F` suppresses physical register stores; the `$019C,X` original low-cache also updates unconditionally. The native result includes these state effects.

## Independent original 6502 opcode comparison

`jp0666_original_cpu_compare.py` executes actual original raw05 **6502 instructions**, not a hand-typed list of register values, from `$811F` through the exit jump to `$86DA`. It supplies deliberately synthetic RAM states with a mock note at RAM `$0200`, sets original voice state arrays and captures all writes to APU/VRC6 physical registers. Its short, strict CPU implements only the ordinary opcodes encountered in the tested branch; unsupported opcodes, runaway instruction loops and altered ROM source bytes fail closed.

The owner-only genuine original-JP comparison to compiled native C11 `cviii_jp_register_plan_0666.c` **passed 69,120/69,120** valid bounded cases:

- 5 melodic modes × 12 upper-nibble notes × 6 octave states × 6 synthetic transpose values × 8 signed detune values × 4 APU gate/cache/flag permutations, with out-of-table combinations deliberately skipped by the fail-closed C11 preconditions.
- 13,824 successful original-6502 vs native cases per mode; every compared case has identical **register addresses, bytes and ordered writes**, original `$01AD/$01B2` un-detuned period cache, final `$EC/$ED` post-detune period, original `$0163` high cache and `$019C` low-cache (APU).
- ROM-free C11 synthetic/witness tests pass GCC and Clang strict C11 (`-Wall -Wextra -Werror -pedantic -DNDEBUG`) and Clang ASan/UBSan.

The comparison is **not a verified original runtime snapshot**. Its RAM is artificial; the input note byte is in synthetic RAM; the CPU is entered *mid-handler* after earlier setup; the full note-trigger scheduler/tempo, `D`/`E` envelope commands, potential other 6502 paths, actual CPU-cycle offsets, hardware synthesis, waveforms, original MesenCE events, and live Music/SFX separation remain **unverified**. The C11 function fails without changing output for inputs outside this branch, including `$06B4` bit7 unset, `$018E` bit4 set, unsupported pitch-table indices and bad memory sizes.

These results **do not** imply the original soundtrack or full note player is reconstructed. JP0665's end-to-end FamiStudio melodic trigger discrepancies are unresolved. They cannot be papered over by this local register-write match. JP0647 mixer still has no authenticated musical producer. No changes to the playable original/Enhanced edition or original sound are made; R-007 remains open, strict PRG 49,504/262,144 and VPP31/100 unchanged.

## Reproduction using local owner materials

```
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  cviii_jp_register_plan_0666.c cviii_jp_register_test_0666.c -o /tmp/jp0666-test
/tmp/jp0666-test
cc -std=c11 -O2 -fPIC -shared cviii_jp_register_plan_0666.c -o /tmp/libjp0666.so
python3 jp0666_original_cpu_compare.py --rom '/private/Akumajou Densetsu (Japan).nes' \
  --lib /tmp/libjp0666.so --json /private/jp0666-aggregate-only.json
```

**Next gate**: recover original per-frame `$0100,X` countdown and full `D/E` envelope progression, then compare original actual original-Japanese Mesen/guest APU-VRC6 register-event traces (including CPU cycle stamps) with native virtual voice event scheduling before activating any native playback.