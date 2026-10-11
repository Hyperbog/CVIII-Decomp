# 0532 JP bulk bank04 scripts and shared sound parser

This archive contains the source generator and **25 generated original-ROM-derived bank assembly files**. The original Japanese source ROM is NOT bundled. Generated assembly contains original source bytes, for use with the ROM supplied by the project owner. The portable Python generator requires the existing `JP/tools/audit_nmi_fixed_scheduler_banked.py`, `JP/tools/test_recomp_6502_0525.py`, `JP/tools/test_recomp_6502_0526.py` from Git branch `decompilation` along with the four checked-in hand-authored `JP/recomp/*.asm` files.

Verified 0532 reconstruction: authenticated bank04 sound-script/data `$87AE-$BE7D` (14,032 physical PRG bytes); sound parser source `$8001-$87AD` in raw banks 04, 05 and 0C (each 1,965 physical bytes, 786 official 6502 instruction starts / 1,716 opcode-operand bytes / 249 local lookup bytes). Source code branch/jump targets that land in the proved CFG are symbolic. Metadata rooted bank04 script streams are labeled at all 96 source-root addresses. This adds **19,927 genuinely classified source bytes** compared with 0531; these physical PRG bytes were already historically verified and are not newly credited strict certification.

Total PRG classification: 12,294 6502 instruction and operand bytes; 907 inline/local lookup and pointer bytes; 28,200 source-confirmed script data bytes; combined **41,401/262,144 PRG bytes classified**. Remaining PRG 220,743 bytes deliberately unclassified; CHR 131,072 graphical source bytes. Full 393,232-byte original retail Japanese iNES roundtrip PASS. Independent original Mesen parity not run; native gameplay parity not claimed.

Reproduce in the project checkout:

```bash
python3 JP/tools/test_bank04_parser_0532.py
python3 JP/tools/build_whole_cart_recomp_0529.py --smoke
python3 JP/tools/test_bank04_parser_0532.py --rom '/path/to/Akumajou Densetsu (Japan).nes'
python3 JP/tools/build_whole_cart_recomp_0529.py --rom '/path/to/Akumajou Densetsu (Japan).nes' --out /tmp/cviii_0532_banks
```

Original ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

Strict semantic PRG certified remains 49,504/262,144; VPP 27/100; semantic 0508 and fixed frontier FB96 unchanged. Source classification is a separate measurement from newly certified ROM bytes and native platform execution.
