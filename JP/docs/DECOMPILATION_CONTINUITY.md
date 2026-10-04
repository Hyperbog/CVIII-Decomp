# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory recovery

After any interruption, do not resume from chat memory. Read:

- `docs/INTERRUPTION_RECOVERY.md`
- `docs/ACCELERATION_POLICY.md`
- `analysis/RESUME_STATE.json`
- `analysis/04FF_WORKING_NOTE.md` while 04FF is blocked

Then run `python tools/check_resume_frontier.py <authoritative JP ROM.nes>`.

Evidence order is JP ROM / observed JP execution, reproducible ROM-backed audits, NES hardware documentation, then external disassemblies/CDL/Ghidra/retrodisasm/decompilers/nesrecomp/NSF/JP-US matching as accelerators. Never commit the ROM.

Target ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; PRG 256 KiB; CHR 128 KiB; mapper 24 / VRC6a. VPP remains **21/100**.

## Stable closed provenance

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
PRG26 renderer                        -> consumes/persists $10 exactly
```

04FE proved `$E7FB-$E813` is a stack-return-address inline tail dispatcher writing only `$00-$03`. The NMI `$18` table is `$E363-$E382`; nested state `$04` reaches `$F390`, loads selector `$2C`, and calls `$E7FB` at `$F39A`. The 32 nested pointer pairs are `$F39D-$F3DC`; table size is **not** a `$2C` bound. 04FE contributed 957 genuinely new bytes, ordered-manifest SHA-256 `a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

## 04FF is blocked / partial

`analysis/RESUME_STATE.json` must remain `blocked` at fixed `$F3DD` until the `$2C` producer domain and admitted nested graph are closed. Do not promote a linear `$F800` frontier merely because bytes through `$F7FF` were inspected.

Controlling 04FF evidence:

- `analysis/NMI_FIXED_2C_HEAD.md`
- `tools/audit_nmi_fixed_2c_head.py`
- `analysis/04FF_WORKING_NOTE.md`

The raw investigation window `$F3DD-$F7FF` is 1059 bytes, SHA-256 `72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6`.

Twenty-six distinct nested roots enter that window. Six encoded primary entries are deferred:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

Strict decode of only the admitted 26 roots gives 401 official instruction starts, zero unknown opcodes, 16 explicit local `$2C` writers, no indexed/indirect zero-page write, and **931 genuinely new consumed instruction/operand bytes**.

Exact manifest:

```text
F3DD-F6AD   721   371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
F6E4-F705    34   cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5
F713-F723    17   4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300
F739-F781    73   b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac
F792-F7B6    37   b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1
F7CF-F7FF    49   13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574
ordered SHA-256 2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

Unclaimed gaps are explicit: `$F706-$F712` (13), `$F724-$F738` (21), `$F782-$F791` (16), `$F7B7-$F7CE` (24). `$F6AE-$F6E3` is prior 04FE coverage. The former 1005-byte claim is superseded because it counted those 74 unreached bytes from physical contiguity alone; `analysis/NMI_FIXED_2C_PREFIX.md` records the correction and its old audit redirects to the strict tool.

The bounded fixed graph itself preserves `$10`. Its local `$2C` constant stores remain within the encoded state family and conservative local INC association reaches at most `$1C -> $1D`, but this is not a transitive producer proof because callees may mutate `$2C`.

Deferred probing has exposed two secondary tail dispatchers:

```asm
F849  LDA $68
F84B  JSR $E7FB

F965  LDA $68
F967  JSR $E7FB
```

Their encoded table lengths are not `$68` producer bounds.

## Open work before releasing 04FF hold

1. reconcile the six deferred primary `$2C` entries;
2. prove the `$68` producer domains and admitted secondary targets at `$F849` and `$F965`;
3. resolve fixed/banked callees under actual mapper state before assuming `$2C` or `$10` preservation;
4. `$18` producer-domain closure remains separately open.

The next useful raw investigation window is `$F800-$FBFF` (1024 bytes), SHA-256 `f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a`. Alignment only: `$F7C0-$F7FF` SHA `0654eeccd284ba39d016f954cdfbe17b34b7218a1afe2bc6eca799a2713a13f7`; `$F800-$F81F` SHA `322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24`.

Checkpoint discipline remains: analysis -> audit -> run exact ROM -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker/head confirmation. Raw physical contiguity is never sufficient evidence for coverage or selector bounds.
