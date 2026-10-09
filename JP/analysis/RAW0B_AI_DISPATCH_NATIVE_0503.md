# 0503 — raw-$0B AI-script dispatcher and native address lift

JP authority: ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

## Proven mechanics, not producer liveness

Verified JP code $BD11-$BD66 implements: stopwatch/carry precheck, script ID $05EF,X zero early RTS, conditional $27 helper $82CD, script pointer lookup from $BEA3 + uint8(script_id*2), four-byte record offset uint8($05C1,X*4), record action byte, and dispatch via $BD67/BE67 based on action bit 7. Pointer addition uses 16-bit carry. Handler entry inherits A=target high byte, Y=uint8(action*2), carry=action bit 7, and Z/N from the last target-high LDA.

The native `decode_ai_script_action` accepts a live mapped CPU-bus reader; it models address lookup after prechecks and returns register/flag values, but DOES NOT execute stopwatch/$27 prechecks or apply 6502 RAM/register side effects. Do not claim complete CPU parity.

Mechanical action $9E indexes $BEA3 and points at $BF79, a fallback script record `19 00 00 00`, not a proved executable handler. All 256 mechanical action values produce 217 candidate bank-window targets; none of that proves an action live.

## Global script writer candidate census

Across all 256 KiB PRG, raw byte-pattern matches at $05EF are: 96 `STA abs,X`, 23 `STA abs,Y`, 5 `STA abs`, 2 `STY abs`, 1 `ORA abs,X`. They are **not** a verified writer inventory and omit aliasing/indirect paths. Audit can export raw-bank and CPU addresses.

## Tests and accounting

Files: `src/ai_script_dispatch.hpp`, `src/ai_script_dispatch.cpp`, `tests/ai_script_dispatch_test.cpp`, `tools/audit_raw0b_ai_dispatch_0503.py`.

```sh
g++ -std=c++17 -Wall -Wextra -Werror -pedantic src/ai_script_dispatch.cpp tests/ai_script_dispatch_test.cpp -o ai_test
./ai_test /path/to/JP.nes
python3 tools/audit_raw0b_ai_dispatch_0503.py /path/to/JP.nes
```

The native test covers 256 mechanical action bytes, authentic JP handler pointer reads, 8-bit multiplication truncation, 16-bit pointer wrapping and script-index aliasing; Python independently audits JP opcodes, table fingerprint, action $9E alias and whole-PRG candidate writer counts.

**0503 adds zero new strict ROM bytes**, since $BD11-$BD66 was admitted in 0501. VPP remains 24/100; strict tracked PRG remains 48,823/262,144 (18.6245%). This checkpoint provides tested native infrastructure, not a claim of parity-tested complete AI.

Next: validate the actual JP $05EF,X and $05C1,X producer/value domains under mapper-aware control flow; intersect proven script records/actions with the mechanical dispatch map; only then promote data bytes and handler code. Fixed raw investigation frontier $FB96 and unclaimed $FAA0-$FAA9 remain unchanged.
