# 0512 — Fixed-bank actor scheduler to source-faithful native horizontal displacement

**Scope:** original Japanese Mapper 24 / VRC6a ROM; **verified bounded native semantic slice, not a complete frame**. The `$80E3–$810E` branch at raw physical PRG bank `$0B` is mapped to CPU `$8000–$BFFF` by original fixed scheduler `$FDF2: LDA #$0B; JSR $E2D0`, then invoked by **`$FDF8: JSR $80E3`**. The caller resumes at `$FDFB: JSR $B1F8`. Mesen `NesPrgRom` absolute offset **`$02C0E3`** independently confirms physical bank `$0B`, not just the game's tracked mapper RAM.

## Source semantics and native C++ lift

Original authenticated raw physical bank `$0B:$80E3–$810E` is 44 bytes, SHA-256 `7cb6c954c56b9288f621afd4c03fdf7ccd3658c2597920fd3311cc7330d7cff3`. Authenticated fixed PRG31 source `$FDF2–$FDFD` is SHA-256 `49893822450a81ebc7347ffb15342a12320d7bf1802834b44a3a01e75b0a74c8`. The source entry first preserves original `$0470,X & $FE` at zero-page `$01`, sign-extends the 8-bit `$6B` delta into zero-page `$00`, and branches on the **sign bit of `$65`**. In this tranche **only `$65 & $80 == 0`**, the horizontal path, is natively implemented.

Original `$80F7–$810E` subtracts signed `$6B` from `$0438,X` using `SEC; SBC`, and corrects the ninth horizontal-coordinate bit stored in bit0 of `$0470,X` via the second `SBC $00`. The remaining bits of `$0470,X` are preserved, and the original return A/X/Y/P are reconstructed, including C/V from second subtract and N/Z from final ORA. Exact four RAM stores are `$01`, `$00`, `$0438,X`, and `$0470,X` (including stores that leave bytes unchanged). This updates the **same actor coordinate fields** used by the already lifted original `$0B:$8001` two-axis routine; the two functions must be integrated by the fixed scheduler rather than conflated with provisional host movement.

[Native source lift](../src/actor_displacement_prg0b_0512.cpp), [public interface](../src/actor_displacement_prg0b_0512.hpp), [ROM-free test](../tests/actor_displacement_prg0b_0512_test.cpp), and [native replay executable](../tools/native_displacement_replay_0512.cpp) are compiled in `standalone0509` and `run_native_regressions.sh`. The optimized native test passes **73,742** cases: all **65,536** byte-position/signed-byte-delta pairs, another 8,192 independently folded coordinate/attribute/status cases, 12 unsupported vertical-path rejections and two invalid-X rejections. Sanitized builds using AddressSanitizer/UndefinedBehaviorSanitizer pass. The test checks 9-bit two's-complement position changes, scratch, original status flags, and absence of unrelated writes.

## Independent Mesen natural-input comparison

Independent Mesen2 2.1.1 runs from the **unchanged original Japanese ROM** and a SHA-locked (`c54060fc64196d750c79f222c22325d8ae1829a32f6da96c0fe93d808907a872`) private natural-controller Stage 1 state, already used for 0511 actor movement. Mesen confirms type `$3D` actors in slots 1 and 2 and enters raw bank `$0B:$80E3` in both cases during **frame 2604**. The first `$80E3` call follows natural game execution; after 20 authentic instructions and RTS at `$810E`, fixed caller resumes at `$FDFB`; the second call is located by continuing the first original execution with no RAM/PC edits.

| Mesen call | Original instructions | Physical PRG | Return PC | Exact RAM comparison | Returned A/X/Y/P |
|---|---:|---|---|---|---|
| Type `$3D` slot 1 | 20 | `$02C0E3` | `$FDFB` | 1,792/1,792 non-stack RAM bytes | `$44/$01/$00/$01` |
| Type `$3D` slot 2 | 20 | `$02C0E3` | `$FDFB` | 1,792/1,792 non-stack RAM bytes | `$44/$02/$00/$01` |

**Total native-vs-original Mesen RAM: 3,584/3,584 bytes exactly equal**, original CPU cycles after return 77,522,001 and 77,523,622. The original $0100–$01FF subroutine stack bytes are excluded, since native structured C++ does not emulate JSR/RTS pushes. [Machine report](0512_live_displacement_report.json) contains original pre/post RAM SHA-256 (excluding stack), the two return cycles, and source ROM hashes; no retail ROM, original savestate, or private raw RAM bytes are committed.

**Evidence grade:** The actual live examples have `$65=0, $6B=0` and attribute `$0470,X=$44`. The complete signed-delta range and coordinate wrap are mathematically unit-tested but are **not** proven as naturally observed source cases. In an additional 20-frame original-Mesen observer, both type-`$3D` actors executed physically mapped `$80E3` once per frame (40 calls); both retained zero displacement in that window. This observation does not establish a global actor/frame cadence.

## Replay and limitations

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/decomp/tools/audit_mesen_displacement_0512.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent --private-state /private/actor2603.mss \
  --native-replay build/standalone0509/native_displacement_replay_0512 \
  --report /tmp/jp0512_mesen_displacement.json
```

The ROM-locked [independent Mesen replay audit](../tools/audit_mesen_displacement_0512.py) passed locally. The private state remains outside Git; GitHub CI only runs the ROM-free native tests and Python syntax check. The source `$65`-negative branch from `$810F` includes vertical coordinate change, actor-type logic and downstream `$8843` transfer, and is **not covered**. Nor are a full scheduler frame, `$B1F8` actor postprocessing, collision/OAM, original sprite/PPU or audio parity, or the global live `$6B` producer domain.

**Accounting unchanged:** zero newly *certified* PRG bytes, strict floor **49,504/262,144 (18.8843%)**, **VPP 26/100**, last certified semantic checkpoint **0508**, fixed frontier **`$FB96`**. The ROM hashes authenticate evidence, not a deduplicated physical overlap/lineage manifest. No RESUME_STATE.json update.
