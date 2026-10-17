# JP 0550 — Natural Mesen state-13 search across independent Stage-1 input forks

## Why this work exists

0546–0547 establish a verified **conditional** original 6502 → native C++ room-initialization path when RAM `$18 == $0D` and the tested substate is supplied. 0548 demonstrates original reset and one complete first NMI under **scripted PPU status and injected NMI timing**, yielding state `$00`, not `$0D`. This is not a natural controller/PPU frame trace.

Earlier, independently emulated Mesen2 **0508** captured a **real** 1,100-frame route (520 title/name, 220 prayer, 360 Stage 1). The stored sampled states in `JP/decomp/analysis/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE_REPORT.json` include `$00,$02,$03,$04,$09,$0A`, not `$0D`; these historical *samples* cannot rule out unsampled transient states or other input routes. None of the 0547/0548 local tests establishes natural `$0D -> $E526` reachability.

The pinned Mesen-agent v0.1.0 emulator/core is **not present in the current local tool container**. New 0550 gameplay forks **have not been executed** as part of this delivery. Do not publish synthetic fixture hits as emulator evidence.

## Implementation

- `JP/decomp/tools/search_mesen_state13_0550.py`: reproducible **one** original cold-boot route + **five independent forks** from the same Stage-1 Mesen savestate. No raw ROM content, savestate or screenshots are checked into Git.
- Existing `JP/decomp/tools/run_mesen_state13_0549.sh` is used *unchanged* for the authentic 520+220+360-frame parent. The caller authenticates SHA-256 for user-provided retail Japanese ROM, pinned `mesen-agent`, and `MesenCore.so`.
- Five bounded 1,200-frame Stage-1 inputs: **idle**, **right**, **right+jump**, **right+whip**, **hold-jump**. The previously documented 0508 branch-input sequences are reused where possible.
- Every child is loaded from exactly `stage360.mss`; parser verifies it starts at the parent's absolute emulator frame. Child outputs are distinct alternatives, **not** concatenated into a fictional continuous run.
- `JP/decomp/tools/audit_mesen_state13_0549.py` tightens event grammar: malformed `CV0549` events, nonhex bytes, unordered frame events, wrong physical-bank identity, incomplete frame logs and Lua callback errors are rejected.
- `JP/decomp/tools/test_state13_search_0550.py` provides a ROM-free, adversarial contract test. Synthetic positive `$0D/$E526` fixtures are tagged as non-evidence and cannot set `state13_e526_observed=true`.

## Frame accounting

| Route | Frames | Starting point | Evidence now |
|---|---:|---|---|
| Existing 0549 parent route | 520 + 220 + 360 = 1,100 | Reset | 0508 historical real route, new 0549 capture **pending** |
| 0550 `idle_1200` | 1,200 | Same 1,100-frame Stage-1 savestate | **Not run** |
| 0550 `right_1200` | 1,200 | Same savestate | **Not run** |
| 0550 `right_jump_1200` | 1,200 | Same savestate | **Not run** |
| 0550 `right_whip_1200` | 1,200 | Same savestate | **Not run** |
| 0550 `holdjump_1200` | 1,200 | Same savestate | **Not run** |

**Planned emulator work: 7,100 frames total, with 2,300 frames maximum on any continuous input route.** Forks do not form a 7,100-frame uninterrupted game session.

## Reproduce

ROM-free CI smoke:

```sh
python3 JP/decomp/tools/test_mesen_state13_0549.py
python3 JP/decomp/tools/test_state13_search_0550.py
python3 JP/decomp/tools/search_mesen_state13_0550.py --plan
```

Authenticated original-Mesen run (private local paths; Mesen assets must be separately supplied):

```sh
python3 JP/decomp/tools/search_mesen_state13_0550.py \
  --rom "$ORIGINAL_JP_ROM" --emulator "$MESEN_BIN_DIR" \
  --out "$PRIVATE_OUT"
```

Optionally reduce run scope with `--fork idle_1200` or other named fork. The command fails closed if SHA identity, scheduler callback, input-plan, savestate, absolute frame, or end-of-run validation fails. It must **never** upload private emulator inputs or output files to a public GitHub Action. Only a reviewed and bounded derived report may be considered for the repository.

## Completion gate for the next milestone

1. Actually execute all planned branches using an authenticated independent emulator and the unmodified JP ROM.
2. Confirm callback installation and exact physical PRG mapping of `$E526`, `$B873`, `$B7F7`; if no `$0D` path appears, report bounded **negative** evidence instead of a fabricated hit.
3. If an authentic `$0D -> $E526` hit appears, capture the complete actual CPU/mapper/RAM input state and compare it with the native six-script path; the current synthetic fixture cannot substitute for this.
4. Run original and native multi-frame PPU/APU/IRQ parity separately. Do not infer full-frame parity from a subroutine match.

Original matching ASM roundtrip, native conditional parity and independent frame reachability remain **distinct** metrics. No new strict PRG bytes or VPP points are claimed in 0550.
