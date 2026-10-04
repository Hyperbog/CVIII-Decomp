# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory recovery

After any interruption, do not resume from chat memory. Read:

- `docs/INTERRUPTION_RECOVERY.md`
- `docs/ACCELERATION_POLICY.md`
- `analysis/RESUME_STATE.json`

Then run `python tools/check_resume_frontier.py <authoritative JP ROM.nes>`.

Evidence order is: JP ROM / observed JP execution; reproducible ROM-backed audits; NES hardware documentation; then external disassemblies/CDL/Ghidra/retrodisasm/decompilers/nesrecomp/NSF/JP-US matching as accelerators. Never commit the ROM.

Target ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; PRG 256 KiB; CHR 128 KiB; mapper 24 / VRC6a. VPP is **21/100**.

## Stable closed provenance

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
04FF admitted nested fixed head       -> preserves $10
PRG26 renderer                        -> consumes/persists $10 exactly
```

## 04FE — fixed inline dispatch

`$E7FB-$E813` is a stack-return-address tail dispatcher. It consumes the caller JSR return address, indexes inline pointer data using A, restores Y, and jumps through `$0002`; it writes only `$00-$03`.

NMI `$E35E: LDA $18 / $E360: JSR $E7FB` uses 16 encoded pointers at `$E363-$E382`. Conservatively decoding all encoded targets gave 435 fixed instruction starts, one nested `$E7FB` at `$F39A`, 21 mapper-dependent banked exits, and no fixed write capable of aliasing `$10` after indexed-write reconciliation.

Nested first-level state `$04` reaches `$F390`, then loads `$2C` and dispatches through 32 encoded pointers at `$F39D-$F3DC`. Table size is **not** a producer-domain bound. 04FE contributed 957 genuinely new fixed bytes, manifest SHA `a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

## 04FF — bounded nested `$2C` fixed head

04FF is complete as a bounded checkpoint. It does **not** claim full `$2C` producer closure.

Raw investigation window:

```text
PRG31 $F3DD-$F7FF
1059 raw bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

Twenty-six distinct nested-table targets enter this window. The six encoded entries carried into 0500 are:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

Strict 26-root graph:

```text
official instruction starts        401
unknown opcodes                       0
unique genuinely new bytes          931
reachable store/RMW instructions     46
indexed/indirect store/RMW forms      0
boundary/dependency exits           136
```

Exact new-byte manifest:

```text
F3DD-F6AD   721   371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
F6E4-F705    34   cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5
F713-F723    17   4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300
F739-F781    73   b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac
F792-F7B6    37   b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1
F7CF-F7FF    49   13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574
ordered SHA-256 2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

Prior/unreached raw bytes are explicit:

```text
F6AE-F6E3   54 bytes   prior 04FE
F706-F712   13 bytes   unreached
F724-F738   21 bytes   unreached
F782-F791   16 bytes   unreached
F7B7-F7CE   24 bytes   unreached
```

The four unreached gaps total 74 bytes and remain unclaimed until actual secondary-dispatch control flow admits them.

Local explicit `$2C` mutations in 04FF are:

```text
F3FF INC   F443 INC   F486 STA   F4BF INC
F4CF STA   F4DC STA   F4F3 STA   F5CF INC
F629 STA   F635 STA   F64F STA   F6FB INC
F716 INC   F775 INC   F7B4 INC   F7DB STA
```

The bounded graph itself preserves `$10`. External fixed/banked callees are not assumed safe, and the local state values are not promoted to a complete `$2C` bound.

Controlling evidence:

- `analysis/NMI_FIXED_2C_HEAD.md`
- `tools/audit_nmi_fixed_2c_head.py`
- `analysis/NMI_FIXED_2C_PREFIX.md` documents the superseded over-broad 1005-byte accounting.

## Open semantic work

1. first-level `$18` selector producer domain;
2. complete `$2C` producer/alias domain;
3. six deferred primary `$2C` entries;
4. `$68` secondary dispatchers at `$F849` and `$F965` and their producer domains;
5. fixed/banked external callees under actual mapper state.

No pointer-table shape is a selector bound. No CPU `$8000-$DFFF` target may be followed under guessed VRC6 state.

## Next checkpoint — 0500

Resume raw fixed-bank investigation at `PRG31:$F800`.

```text
initial window      $F800-$FBFF   1024 bytes
SHA-256             f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a

verification overlap $F7E0-$F7FF  32 bytes
SHA-256              6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1

frontier fingerprint $F800-$F81F  32 bytes
SHA-256              322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24
```

0500 should:

- reconcile primary targets `$F831/$F839/$F841/$F849/$F965`;
- decode the `$F849` and `$F965` `$68`-indexed inline tables while proving actual `$68` producers rather than using table lengths as bounds;
- admit the 04FF gaps `$F706-$F712`, `$F724-$F738`, `$F782-$F791`, `$F7B7-$F7CE` only when control-flow evidence reaches them;
- continue the whole-ROM `$2C` writer/alias audit, including save/restore paths and indexed/indirect aliases;
- resolve mapper-dependent callees only when VRC6 bank state is proven.

Checkpoint transaction remains: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.