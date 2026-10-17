# First verified structural cross-edition routine anchor: inline stack dispatch

**Observed source ROMs:** Akumajou Densetsu Japan, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; Castlevania III USA, SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`. ROM bytes remain outside Git.

## Exact structural reuse candidate (C1, not G1)

The Japanese **fixed PRG31** `$E7FB-$E813` routine is exactly **25 bytes / 15 official instructions**, fingerprint `d2adbf45aa9746eb53ba2e8ec8513cb338f8fd30f4bc3627074f186c14439091`. Its bytes occur **once** in the US 256 KiB PRG, at physical offset `$3E86D-$3E885` in PRG31, a *candidate* mapped CPU entry `$E86D`. For comparison, JP physical offset is `$3E7FB-$3E813`.

The common instruction sequence performs the stack-return-address inline-pointer dispatch: `ASL A`, `STY $03`, `TAY`, `INY`, two `PLA`s into pointer `$00/$01`, two `LDA ($00),Y` reads into `$02/$03`, `LDY $03` for saved Y, then `JMP ($0002)`. In each ROM, the exact 25 bytes are pinned by hash, instruction boundaries and opcode signature. Thus **the local algorithm is byte-identical under the same machine inputs**, but a US *live caller*, bank register context and pointer producer domain have **not** yet been proved.

A longer physically contiguous **134-byte exact span** also matches: JP `PRG+$3E7B8-$3E83D` ↔ US `PRG+$3E82A-$3E8AF`, SHA-256 `49a31b22a09167c55a54fc9697817e67adde600d1fe8051ff3c8adc594d1c481`. The immediately adjacent bytes differ at both ends. **This larger interval is not automatically all code or additional verified bytes.** It contains the 25-byte known routine but remains classified as an unverified mixed/unknown region elsewhere.

## Reproduction and limits

```sh
python3 JP/decomp/tools/audit_shared_dispatch_jp_us.py '/private/Akumajou Densetsu (Japan).nes' '/private/Castlevania III - Dracula\x27s Curse (USA).nes' /tmp/shared-dispatch-report.json
python3 JP/decomp/tools/nes_reuse.py compare /private/jp.nes /private/us.nes --manifest JP/decomp/SharedNES/JP_US_DISPATCH_ANCHOR.json --out /tmp/anchor.json
```

This is exactly the user's proposed reuse process: identify a previously known original-ROM routine, find the same bytes at a different physical address in another game version, then mechanically audit both and preserve the distinct provenance. **It cannot justify automatically reusing caller semantics, mapper-dependent buses or stage logic.** JP strict byte total still **49,404/262,144 (18.8461%)**, overall VPP **25/100**, last completed semantic checkpoint **0507**, and fixed frontier `FB96` remain unchanged.
