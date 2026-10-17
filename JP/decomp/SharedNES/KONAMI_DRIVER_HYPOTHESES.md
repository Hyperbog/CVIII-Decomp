# Konami NES/FDS audio-engine reuse hypotheses — SOURCE EVIDENCE ONLY

**Evidence class: S0.** This file transcribes a **community's tentative driver-family grouping**, not actual code match or authenticated authorship. The source explicitly warns that Konami used *branches and one-off variants*. The publisher being Konami does not imply shared program code. Source: [VGMPF Famicom/NES Sound Driver List — Konami section](https://vgmpf.com/Wiki/index.php?title=Famicom%2FNES_Sound_Driver_List#Konami), viewed 2026-10-09. See also [Konami composer/driver overview](https://www.vgmpf.com/Wiki/index.php?title=Konami). All titles below are **candidate comparisons until their legally supplied ROMs are independently fingerprinted**.

## Candidate driver family partition

| Source-assigned grouping | Candidate titles | Hypothesis / explicit weakness |
|---|---|---|
| Hidenori Maezawa (named by community) | Castlevania III (NES), Contra, Gradius II, The Goonies II, Super C, Getsu Fuuma Den, Akumajou Dracula (FDS) | Related driver families are **plausible**, but distinct revisions/hardware and unsupported creator attribution require code matching. **Akumajou Densetsu (VRC6) is specifically labeled a VRC6 variant with a question mark**. |
| Atsushi Fujio (named by community) | Metal Gear, Castlevania II: Simon's Quest, Jackal, Blades of Steel, Life Force, Wai Wai World, Top Gun, Bucky O'Hare | Different putative sound family from Castlevania III. `Metal Gear` should not be assumed an exact Match to the JP Castlevania III VRC6 driver. |
| Fujio VRC6 variant | Mouryou Senki Madara | Same VRC6 hardware family as Akumajou Densetsu but community catalog groups its *sound driver* differently. Mapper equivalence **does not** prove engine equivalence. |
| Unknown/unique variants | Esper Dream 2, Akumajou Special: Boku Dracula Kun, Parodius Da!, several others | Despite mapper 26 on Esper Dream 2, sound program relationship is undetermined in this source. |
| FDS driver variants | Akumajou Dracula (FDS), Falsion (FDS), Gyruss (FDS), Dracula II: Noroi no Fuuin (FDS), etc. | Shared disk BIOS interface is independently reusable; game audio engine versions still need their own comparisons. |

## Prioritized test sequence if additional ROMs are legally supplied

1. **Castlevania III Japanese vs Contra or Gradius II (appropriate regional revision)**: highest publisher-and-driver-family lead, subject to distinct mapper and expansion-audio variants. Anchor the known JP bank-$0C sound driver entry at raw `$8850`, as supported by committed [Phase 10/11](../analysis/0508_PHASE11_FINDINGS.md) (caveat: bank and function boundaries must be reconciled first). Compare unique byte windows, full caller/data flow, sound-command selectors and register effects. Do not mask APU/register operands.
2. **Akumajou Densetsu vs Madara**: strongest VRC6 **hardware** reuse, but likely *different* engine-family hypothesis. Use the `nes_mapper_family` adapter to canonicalize VRC6b address pin swap, then compare independent driver data; this is a meaningful **negative-control** for an overly aggressive Konami matcher.
3. **Madara vs Metal Gear**: same community-proposed Fujio grouping, *different hardware*; compare driver logic only, not register addresses or sound-channel count.
4. **Esper Dream 2**: test both families and label unmatched/novel variants without forcing an attribution.
5. **Akumajou Dracula FDS vs Castlevania III JP**: architecture differences likely substantial, but FDS BIOS service and early sound-format genealogies may offer useful clues. Preserve actual disk layout and BIOS revision.

## Per-title acceptance for carrying an existing semantic model

- Record exact source and target image SHA-256, release region/revision, mapper/submapper, physical bank and bank-write producer.
- Select known instruction starts and data boundaries; compare exact code before considering relocation masking; inspect call edges and indirect targets.
- Verify RAM/ZP fields, stack ABI, flags, DSP/APU/VRC6 writes and sound metadata/stream grammar under **target-ROM code**, not only reference program labels.
- Test deterministic input/output contracts and if possible independently sourced register traces.
- Award strict game-specific coverage only after the target's own proof obligations; **no automatic credit from a shared name or code fingerprint**.

No commercial BIOS or game ROMs are included with these hypotheses. No new VPP or strict PRG coverage is claimed.
