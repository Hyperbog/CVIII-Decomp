# 0509 — Independent Mesen actor producer feedback and seven controller forks

**Evidence: independent Mesen2 original Japanese ROM execution; bounded source/gameplay witness.** This is follow-up evidence to [the first original live row-$32 capture](0509_MESEN_ACTOR_LIVE_FINDINGS.md), not a completed strict-byte checkpoint.

## Automated feedback loop

[Python experiment and merger](../tools/audit_mesen_actor_feedback_0509.py) checks the original JP ROM SHA-256, independently captured Mesen agent/core hashes, runs controller-only frames from a verified natural frame-2603 gameplay anchor and observes CPU code execution plus RAM writes through Mesen Lua callbacks. Every CPU-PC observation is qualified by Mesen `emu.convertAddress()` physical PRG mapping to raw 16-KiB bank $0A; tracked game RAM $23 alone is NOT accepted as mapper proof. Callback code never changes RAM, PC, input, bank registers or the stack.

An automatically verified merge rejects duplicate/missing policies, incomplete emulator runs and mismatched anchor hashes, then emits the compact [non-lossless JSON report](0509_MESEN_ACTOR_FEEDBACK_REPORT.json). Policy experiments were actually executed **as seven separate Mesen processes** after an all-in-one driver repeatedly exceeded its wall-clock limit; this is a harness/runtime limitation, not evidence of a game crash. The shared anchor is the previously clean-boot-tested frame-2603 state (private SHA-256 `24c54adbeb75cb03bc4fa825a91b91950f12b68e8271d08b4b1330afeee6d470`). The one-call end-to-end seven-fork run has **not** independently completed; each segmented policy plus the merger passed.

## Controller branching (640 frames per fork)

| Input policy | First authentic row-$32 $8B2C handler, absolute frame | Observed type-$3D actor allocations |
|---|---:|---:|
| Up+Right and timed jumps | 3088 | Two, slots 1 and 2 |
| Right and timed jump/Up pulses | 3092 | Two, slots 1 and 2 |
| Right and timed A+B | 3094 | Two, slots 1 and 2 |
| Idle | Not observed within 640 frames | None |
| Right only | Not observed within 640 frames | None |
| Left only | Not observed within 640 frames | None |
| Right and timed whip | Not observed within 640 frames | None |

These are **4,480 emulator branch frames** in seven independent 640-frame policy replays, not 4,480 new unique chronological frames from the same uninterrupted playthrough. None observed entries $90C5, $90DF or $9133. The negative policies cannot establish global deadness. On the left-only route the original $8143 source writer was observed setting source event row bytes to zero; this is not a type-$3D creation.

## Live producer → data descriptor → object writes

Mesen's actual mapped-source instructions establish: raw bank-$0A $8143 writes $07C2,X=$32 for source objects X=3,4; $8157 initializes their $07E0,X=0 bit field; $8182 initializes the $07C8,X event index; $84F3 calls $8501, which dispatches through original word tables to $8B2C. The handler uses fixed $FF06 and $FF24. Raw $8D90 stores $3D at $054F and $0550. Raw $8B71/$85DD updates original source event $07CB to $11 and $07CC to $21. Real mapped PRG physical offsets are $028143, $028157, $028182, $0284F3, $028501, $028B2C, $028D90, $028B71 and $0285DD.

The same live original-ROM event provides two **bounded five-byte source descriptors**. At $8143 (X=3), zero-page $00/$01 resolves to CPU **$A444**, physical PRG offset **$02A444**, record `32 20 50 00 00`, SHA-256 `550c6e5cbd4b45477ba3eb468c803b4c610d80198ea7665760fe7f3dd9a919c8`. For X=4, it resolves to CPU **$A43F**, physical offset **$02A43F**, record `32 00 B0 00 00`, SHA-256 `8008a85aba35cf7ab577684246ef493f6ff5471ee6cc5503d886f471e65fe1b5`. The first byte of each matches the observed event row $32. The five-byte sample does **not** establish total descriptor/table extent or other live source inputs.

## Reproduce and certification limits

For a fresh run: `python3 JP/tools/audit_mesen_actor_feedback_0509.py ORIGINAL_JP_ROM --mesen-agent /path/to/mesen-agent --report local.json`. For resource-isolated replay, pass `--private-anchor /path/to/verified-frame2603.mss --policies right_jumps` (or another policy), one experiment per process, then merge all seven successful private result JSONs with `--merge-reports ... --report summary.json`. **Do not commit Mesen savestates, ROMs, raw CDL or long full CPU traces.** To accept a private anchor, the script checks its emulator frame number; its hash is recorded by the merger. This script is an evidence gate for the recorded route, not a general native frame-parity or gameplay-completeness certificate.

Local full merge digest SHA-256 `a63d82ef99b5c425b93b2f11211e10b2c0e11726d5c0efbe4360382ed7580ca2`. Original Mesen input-domain coverage remains finite; global $18/$19 room state, stage layout descriptors, PPU/NMI/IRQ/audio/frame parity, all-event row producers and the $90C5/$90DF/$9133 paths remain OPEN. **New strict PRG bytes 0, cumulative 49,504/262,144 (18.8843%), VPP 26/100, completed checkpoint 0508, fixed frontier FB96 unchanged.**
