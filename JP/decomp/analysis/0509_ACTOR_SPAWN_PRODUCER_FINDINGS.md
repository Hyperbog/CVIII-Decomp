# 0509 raw-bank $0A actor allocation — provisional source-stepped proof

Original JP raw VRC6 bank $0A, physical PRG20/21 CPU $90CA-$90DE executes a concrete actor-slot allocation callsite into fixed PRG31 $FF06. Source $90CE-$90DE is hash-locked to SHA-256 `f4300055beb08d35061b4687f3f479782abc71957523304ad9fb0a685efa069a`; $90CA-$90CD is opcode-pinned. Previous fixed $FF06 helper bytes remain authenticated by `audit_actor_cpu_abi_0509.py`.

## Original instructions at the bounded callsite

```asm
90CA  LDA #$00
90CC  STA $10
90CE  JSR $FF06
90D1  BNE $9128       ; no vacant slot
90D3  LDA #$13
90D5  STA $054E,X     ; first vacant X=01..0C
90D8  LDA #$00
90DA  STA $05EF,X
90DD  BEQ $90F7
```

## Executable original-source proof and boundaries

[The ROM-locked 6502 runner](../tools/audit_actor_spawn_0509.py) executes 4,096 occupancy bitmaps, including 4,095 free-slot results and the one saturated result. It fetches 73,717 original instructions across 17 distinct source instruction addresses, checks A/X and 6502 conditional branches, stack JSR/RTS, exact ordered RAM mutations and unrelated-field preservation. Result digest: `600b9ee5fcc77de39ae83c871325b728881052c5cb07f9aad00a5d40b50f68e9`. [Machine report](0509_actor_spawn_report.json).

Inputs are synthetic occupancy RAM. Mapping is explicitly raw $0A in $8000-$BFFF plus fixed PRG31 at $E000-$FFFF. The runner stops at $90F7 or $9128 without interpreting their successors. It does **not** establish actual caller liveness, mapper-state lifetime, interframe sequencing, player/enemy behavior or final renderer-facing ZP $10 provenance. The local zero write to $10 is a **conditional producer**, not proof of a frame-wide final value.

Reproduce: `python3 JP/decomp/tools/audit_actor_spawn_0509.py ORIGINAL_JP_ROM --report /tmp/0509_actor_spawn.json`.

**Accounting unchanged:** new strict PRG 0, total 49,504/262,144 (18.8843%); VPP 26/100. Completed semantic checkpoint 0508, next 0509; fixed frontier FB96. No lossless ROM/disassembly dump is committed.
