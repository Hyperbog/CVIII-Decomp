# JP0648 — Authenticated 15 original-JP DMC programs and event plans

## Scope

This checkpoint makes a **genuine original-Japanese sound-data path** machine-readable, without inventing audio samples or modifying the playable game.

The earlier JP0533 investigation authenticated 125 bank0C indexed sound descriptors. IDs $6F–$7D are 15 four-byte special bank00 descriptors whose source targets cover **original PRG0C:$A957–$A992**. The JP0616 original opcode audit authenticated the high-command priority guard and the exact **$4010–$4013 DMC register-write routine**. JP0648 joins those two independently documented structures to produce conservative *read-only host DMC event plans*. It does **not** produce decoded DPCM waveform samples or music, does not assign music/SFX ownership, does not replace the 2A03 APU, and does not connect this builder to gameplay.

## Original Japanese ROM source proof

The optional private-ROM verifier `JP/tools/jp_dmc_original_source_0648.py` authenticates the 393,232-byte Japanese mapper24 iNES ROM with SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. It then checks:

- Original PRG0C metadata `$8F60–$9540`: SHA-256 `ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154`.
- The original priority branch `$8908–$8953`: SHA-256 `ffaacc4b3eb0372295e0402162915ebe6eacc8c8329678432de8472af0d62afd`.
- Exact program-to-register writer `$8928–$8953`: SHA-256 `b6f771d46d16919b2a00a8505ad3a5ddca3cffc75ccaafe6750df524804dde70`.
- The 60 owner-ROM DMC parameter bytes `$A957–$A992`: SHA-256 `02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45`.
- The sound metadata pointers for IDs 111–125, each resolving to a special descriptor `00 09 [little-endian address]`, and each address pointing to the corresponding 4-byte DMC slot. Pointers are **indexed**, not assumed to be monotonically ordered.

The 15 original four-byte entries are owner-private cartridge data. Git contains only hashes, decoder rules, and synthetic patterns; it does not distribute the 60 bytes or DPCM sample payloads.

## Authentic decoded **control-flow** behavior

For original command `A=$6F+index` with bounded `index=0..14`:

1. The driver computes `index=A-$6F` and writes it to original $EF.
2. When `index >= $0D`, it increments original RAM `$06DD` **before** checking DMC priority.
3. The driver returns without DMC programming if `old $019E >= $05` and `index < old $019E`. The counter increment can therefore survive a rejected sound.
4. If accepted, original `$019E` becomes `index`, and the driver writes these six APU values in order:

| Order | Register | Original value |
|---|---|---|
| 1 | `$4015` | `$0F` |
| 2 | `$4010` | descriptor byte 0 |
| 3 | `$4011` | descriptor byte 1 |
| 4 | `$4012` | descriptor byte 2 |
| 5 | `$4013` | descriptor byte 3 |
| 6 | `$4015` | `$1F` |

The primitive `cviii_dmc_plan_0648` accepts a caller-authenticated 60-byte table, command and original DMC priority. It returns a validated *event plan* with accepted/denied status, priority after the gate, the independent counter-increment bit, and up to six abstract APU writes. **The event plan does not execute any writes.** The function refuses commands below $6F and above $7D, including the original driver's wider mathematically possible high-input domain: past $7D the pointer arithmetic leaves the 15 authenticated descriptor entries and can reach unrelated bytes/code. This conservative refusal is not a claim the retail game never issues other byte values.

The caller must authenticate owner-ROM bytes using the SHA-locked private-ROM verifier. The C planner is pure and does **not** by itself compute a cryptographic ROM digest.

## Validation

- Owner-local original-JP SHA + physical metadata/driver/table fingerprints and special descriptor chain: **authenticated**.
- ROM-free Python `--smoke`: 3,840 source-independent command/priority cases, guarded decision and counter parity, malformed size/priority/command rejection.
- C11 production implementation `cviii_dmc_source_0648.c` with `cviii_dmc_source_test_0648.c`: the same 3,840 cases, 15 descriptor indices, all six abstract register writes and mutation-safe output for invalid inputs; `NDEBUG` assertions remain active in Windows Release.
- Full external NESRecomp mapper24 Linux and Windows Alpha SDL2 native CI compile the dormant decoder. No original ROM, genuine gameplay or proprietary NESRecomp source is checked into the repo.

```sh
python3 JP/tools/jp_dmc_original_source_0648.py --smoke
python3 JP/tools/jp_dmc_original_source_0648.py --rom "/private/Akumajou Densetsu (Japan).nes"
```

## Not established

**Not yet decoded:** original DPCM sample bytes/paging, DMA clocking and audible waveform, low-command music phrase opcode semantics, scheduler voice ownership, event liveness on an actual original-JP playthrough, Mesen/native cycle/PCM parity, and any real Music/SFX separation. JP0647's independent voice mixer remains dormant and original Japanese sound output remains authoritative.

Next: recover DPCM sample-source bank mapping and lifetime from actual CPU/mapper/DMA traces; then use validated independent original sound events to feed real host producers. Do not claim a playable, audibly correct effect before this evidence exists.

No modding features are introduced; modding is deferred until Enhanced release. Graphics issue #1 remains owner-confirmed closed. Strict semantic PRG **49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint **0508**, fixed frontier **$FB96**, R-002 **OPEN**, audio investigation R-007 **OPEN**.
