# 0509 — ROM-stepped source scheduler and indexed 1/2/3-actor lifecycle

**Status: PROVISIONAL ORIGINAL-JP ROM EXECUTION.** This is not proof of an original gameplay frame, all-live input domains, or a new strict PRG byte range. ROM identity: SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28, 393,232 bytes, iNES Mapper 24 / Konami VRC6a.

## Real source call graph and pointer bytes

The six-source-object loop begins at raw bank **$0A:$84EA** ($84E9 is the prior RTS). It visits object indices X=0–5, and when $07C2,X is nonzero, stores X at $69 and calls **$8501** at $84F3. After the selected handler returns, it restores X at $84F6. The upstream test deliberately stops at **$84F8**, before the additional call to $83D1; no entire frame is executed.

Original $8501–$8522 is a genuine two-level indirect dispatcher: it doubles **$07C2,X**, loads the row's pointer word from ROM at **$8523+2*row** into zero page $00/$01, then doubles **($07C8,X & $0F)**, reads the indexed handler pointer through authentic 6502 LDA ($00),Y and INY into $02/$03, and finally executes the actual **JMP ($0002)**. The original $84F3 JSR return stays on the stack until the chosen handler RTS.

| Row $07C2,X | Event low nibble $07C8,X | Handler CPU entry | Requested actors | $054E,slot type | $05EF,slot |
|---:|---:|---:|---:|---:|---:|
| $08 | 0 | $90DF | 2 | $68 | $60 |
| $09 | 0 | $90C5 | 1 | $13 | $00 |
| $09 | 2 | $90DF | 2 | $68 | $60 |
| $0A | 0 | **$9133** | 3 | $12 | $00 |

The third handler starts at **$9133**, NOT $9131. $9131 belongs to the preceding pointer table; $917B is the real three-actor handler return RTS. The $07C8 high nibble is correctly ignored during dispatch (tested incoming $00 and $F0 prefixes) but the full byte is incremented upon completion. These four pointer cases are only a **tested subset**, not a proof of the live row or selector ranges.

## Guard, state changes, and partial-allocation behavior

The common source $8CDD guard reads $53 and then $07E0,original-X; either nonzero exits without starting actor creation. Only both zero proceeds through the fixed **$FF06** scanner to find the earliest free actor slot X=1–12, a different range from source objects X=0–5. A saturated scan also exits without starting a new allocation.

Every spawned actor receives original-ROM positional offsets and type-specific field initialization. Type $13 has offset (80,40) hex and $0470=$C8; type $68 emits (C0,40), then (40,50), with $0470=$C8 and $05C1=0; type $12 emits (D0,50), (B0,50), then (30,50), writes $0470=$88 and $0645=$82,$81,$80. Critically type $12 does **not** clear $05C1 in this handler. All types clear $04F2/$0509/$0520/$0537 in selected destination slots; the script ID $05EF is set to the values above.

Source **partial-commit** contract: if two or three actors were requested but available slots run out after the first successful assignments, those earlier actors stay installed. The handler does not roll them back, and does not increment the originating object's event byte $07C8,original-X. The event byte increments only on complete success. Local ZP $10 writes and decrement/branch paths are byte-verified; no claim of its last value at the actual OAM renderer is made.

## Regression and proof boundaries

The [original-ROM bounded CPU audit](../tools/audit_actor_dispatch_chain_0509.py) runs **4 routes × 4,096 occupancy bitmaps × 3 gate states × 2 entry modes = 98,304 cases**, with **6,174,946 original fetched instructions** at **111 distinct CPU instruction addresses**. Both entry modes (direct $8501 and $84EA parent) execute through the selected original source path; the latter preserves its JSR return and source X. Assertions include original indirect pointer fetch, 6502 branch flags, stack depth, exact *ordered* RAM stores (including data values), no other mutation, per-actor offsets, partial failure and high-bit masking.

Actor-count histogram: 0 actors: 65,544 cases; 1 actor: 8,262; 2 actors: 16,464; 3 actors: 8,034. These are *synthetic state counts*, not measured gameplay probabilities. The deterministic result digest is **119d21b0dc793e70731914b7ee4b162e8485cada3fdd2eb559d466e00880d532**. [Machine report](0509_actor_dispatch_chain_report.json). The raw-bank $0A source hash witnesses include $84EA–$8500, $8501–$8522, $8533–$8538, $8CDD–$8CE9 and the **mixed code/data** $90BC–$917B block. A hash of mixed code/data does *not* mark every byte inside it executable.

Reproduce with the provided original JP ROM: python3 JP/tools/audit_actor_dispatch_chain_0509.py ORIGINAL_JP_ROM --report /tmp/0509_actor_dispatch_chain.json

**OPEN:** original Mesen reset-to-stage/frame reachability of $84F3 with raw bank $0A, original $07C2/$07C8 producer domain, $53/$07E0 indexed live guard values, onward $83D1 object movement, interrupt timing, frame-level ZP $10 last writer, OAM/PPU/APU/audio native parity. [Optional independent Mesen capture checklist](../docs/0509_MESEN_ACTOR_DISPATCH_CAPTURE.md) is provided.

**Strict accounting unchanged:** 0 new credited PRG bytes; verified PRG **49,504 / 262,144 (18.8843%)**, VPP **26/100**. Last completed semantic checkpoint **0508** and fixed PRG31 frontier **FB96** remain unchanged. This research commit does not edit RESUME_STATE.json.
