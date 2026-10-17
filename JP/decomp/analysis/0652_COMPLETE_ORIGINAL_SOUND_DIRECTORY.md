# JP0652 — complete original-JP sound-program directory catalog

## Scope and evidence boundary

The authentic Japanese Akumajou Densetsu Mapper 24 ROM has SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
JP0533 classified its indexed sound metadata; JP0648 proved the 15 special DMC
commands. JP0652 joins the **entire 125-ID indexed directory** into a
deterministic, read-only, metadata-only source catalog. This is a complete
structural catalog of the indexed records, **not** a complete sound engine,
note/phrase decoder, Music/SFX classifier, or runtime reachability proof.

Source: physical 16KiB PRG raw bank `0C`, CPU address conditional on mapper
state. The 125 source-index pointers at `$8F60-$9059` lead to 125 distinct
descriptor records occupying `$905A-$9540` exactly once. Authenticated SHA-256
of that combined 1,505-byte region:
`ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154`.
The source-addressed 3,523-byte stream pool `$9541-$A303` is separately pinned
by SHA-256 `0df689b5769e50d65d736abe77cbe5752c2b6980de172164991ef32f78d38721`;
its command-by-command semantics remain open.

## Authenticated indexed directory

| Descriptor type / physical raw bank | Program IDs | Producer source references |
| --- | ---: | ---: |
| Raw `0C` banked source list | 79 | 139 |
| Raw `04` banked source list | 17 | 102 |
| Raw `05` banked source list | 14 | 84 |
| Special `00 09` DMC parameter pointer | 15 | separately indexed DMC table |
| **Total** | **125** | **325 bank-qualified source references** |

The 110 banked-source descriptors contain 1–6 triplets each. The triplet's
first byte is recorded **only as an opaque field**, never silently interpreted
as channel, voice, song, or effect. For all 325 target words, the catalog
preserves raw physical 16KiB bank, mapped *conditional* CPU target, physical
8KiB bank and PRG byte offset. Formula:
`physical_offset = raw_bank16*0x4000 + (cpu_address - 0x8000)`.
This is source provenance, **not a runtime VRC6 mapper observation**.

Indexed original sound IDs `$6F-$7D` reference the fifteen `00 09`
metadata records, each linking to a different ordered four-byte DMC parameter
slot at physical raw0C CPU `$A957 + 4*index`. Pointers are indexed, not
required to be stored monotonically in the metadata area. The exact original
60-byte DMC table has SHA-256
`02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45`.
As with JP0648/JP0649, no audio sample bytes or synthesized PCM are exported.

## Code and verification

`JP/decomp/tools/jp_sound_catalog_0652.py` authenticates the entire owner-supplied
Japanese ROM and independently checks the 1,505-byte directory, 3,523-byte
source pool, DMC table, pointer uniqueness, full descriptor byte coverage,
no overlaps, 110 bounded list records, 15 ordered DMC targets and the exact
325 physical source addresses and histogram. Output is a private **metadata
catalog**, potentially sufficient to reconstruct directory metadata, so
**do not commit or publish generated JSON or commercial-derived bank data**.

Internal evidence IDs `cviii.jp.sound.source.01` through
`cviii.jp.sound.source.7d` are trace/analysis names only, **not a public
modding API**. No gameplay/audio production component consumes this catalog.
It does not change the original game's APU/VRC6 output.

To reproduce:

```sh
python3 JP/decomp/tools/jp_sound_catalog_0652.py --smoke
python3 JP/decomp/tools/jp_sound_catalog_0652.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --json "/private/JP0652-sound-source-catalog.json"
```

Owner-ROM mode passed locally: original SHA, all 125 indexed records,
all 325 references, all fifteen DMC target positions and their source
fingerprints. ROM-free artificial-fixture smoke and seven damaged/short
fixture cases passed. Linux/Windows CI invokes only the synthetic smoke;
public CI never consumes or uploads the original ROM.

## Unresolved

The index and physical source metadata do not establish the played game
sound ID sequence, mapper write/install sequence, phrase opcodes, original
sound request ownership, DMC DMA-cycle behavior, or independent Music/SFX
playback. No live original MesenCE/native paired gameplay has been observed;
R-007 remains OPEN. R-002 stays OPEN. Strict semantic PRG remains
49,504/262,144 (18.8843%), VPP27/100; certified checkpoint0508, fixed
frontier $FB96. No new strict bytes or VPP credit; the working Enhanced
original audio path is unchanged and the JP0647 virtual bus remains dormant.
