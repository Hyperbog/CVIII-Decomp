# JP0630 — Original-Mesen selector STA and loader postcondition watchpoints

**Scope:** raw01:$BB57–$BB61 to RAM $07A0, raw0A:$B7F7–$B806.
This is a **capture and parser upgrade**, not a new original-game observation.
**R-002 OPEN; zero new semantic PRG bytes; VPP 27/100; checkpoint 0508; frontier $FB96.**

## Gap closed in the *instrumentation*, not in the gameplay proof

JP0629 logged the producer entry, $07A0 writes, and loader entry.
It did not observe execution at the precise original producer \`STA $07A0\`
(raw01:$BB5E), nor the loader's actual $08/$09 output at
raw0A:$B806. It therefore could not independently compare the pointer
word after the original 6502 completed the lookup.

The new **read-only** Mesen2/MesenCE script watches:

- **P/T:** original raw01:$BB57 producer entry and raw01:$BB5E
  instruction start, authenticated by physical PRG offsets $07B57/$07B5E.
  T records 6502 A before STA (not just an inferred writer PC).
- **R/W:** all four RAM aliases of $0030 and $07A0. The callback
  records the pending byte and pre-write byte; the reporter checks
  consecutive RAM old/new continuity.
- **C/S:** raw0A:$B7F7 pointer-table entry and raw0A:$B806
  postcondition, physically authenticated at $2B7F7/$2B806.
  C reads the currently mapped pointer bytes without CPU side effects;
  S independently reads the actual resulting RAM $08/$09.
- **N/I:** observed NMI/IRQ callbacks and CPU cycles between watchpoints.

Mapping failure, reset, savestate load, event truncation, incomplete
footer, contradictory RAM continuity or out-of-order records cause
rejection. The report preserves **unmatched cases**, source-entry
candidates and postcondition mismatches instead of suppressing them.
A T→W adjacent match is stronger than the earlier source-PC hint;
it is still not proof of an entire cross-bank caller chain, original
playthrough authenticity, or the domain of all producers.

## Owner-local acquisition

With the SHA-authenticated original Japanese ROM running in Mesen2,
load \`JP/tools/mesen_jp_room_chain_0630.lua\`. Play normally and
save the script console log in a private path, then stop the script to
obtain the \`JP0630_END\` footer. Do not load a savestate or reset
during that one capture. Do not commit the retail-ROM log by default.

\`\`\`sh
python3 JP/tools/audit_mesen_room_chain_0630.py --smoke
python3 JP/tools/audit_mesen_room_chain_0630.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --trace "/private/Mesen2-JP0630.log" \
  --out "/private/JP0630-report.json"
\`\`\`

The parser authenticates the ROM SHA-256 and pointer table when a real
log is supplied. **The local tests only exercised synthetic traces,**
including one synthetic log parsed against the owner-supplied retail
ROM. No Mesen executable was available in the testing container.
No real original-emulator script session or separate native replay
has been observed; the postcondition is not yet gameplay-validated.
Lua API callback names were checked against Mesen2's official
\`LuaDocumentation.json\`; Lua execution itself remains untested.

Next: collect a genuine original Mesen session; investigate whether
the recorded original producer STA is the actual last $07A0 writer
before a matched raw0A C→S, and inventory NMI/IRQ interleavings.
Only then consider independently justified byte admission.
