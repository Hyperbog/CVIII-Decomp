# JP0640 — Original raw01 static callsites for selector parent and table suffix

**Evidence:** owner-provided Japanese retail ROM, exact SHA-256
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28,
physical VRC6 PRG raw01 16 KiB SHA-256
8199a7b3cb99e175b7554fc2d8e4ccd593b953aea82b9d636aa881c919391f6d.

The original raw01 CPU $B7EF–$B813 region is authenticated with a
separate window hash and partitioned into **14 instruction boundaries**.
Its eight literal JSRs include two directly relevant calls:

| Source in physical raw01 | Original instruction | Conditional meaning |
|---|---|---|
| $B801 | JSR $B87A | Enters JP0634's bounded selector preparation route |
| $B804 | JSR $B4BB | Instruction immediately after the $B801 call return address |
| $B807 | JSR $B877 | Calls the candidate jump stub following B855 |
| $B877 | JMP $BB6B | Branches over the distinct nine-byte $BB62–$BB6A table |
| $BB6B | A9 00 85 00 A2 05 | Code-like prefix after the source array, not a complete proved routine |

The region also calls $E249, $B3F7, $B855, $B8A0 and $B296,
and ends with JMP $B62B. The entire raw01 bank is censused for
literal 6502 `JSR $B87A` and `JSR $B877` byte patterns; the
only matches are $B801 and $B807 respectively. The script verifies
these are actual original instruction *boundaries* within the
authenticated $B7EF–$B813 code partition. It does **not** prove that
indirect calls or all alternate entries are absent.

This provides a structural in-bank connection to JP0634's
`$B87A → $B919 clamp → $BAEF → $BB57` candidate sequence and
independently reinforces why the $BB62–$BB6A nine-byte table should
not be extended over the $BB6B candidate-code entry. A conditional
6502 return from the $B87A path reaches $B804 **only if the
mapper-visible source and conventional stack return remain intact**.
Calls to fixed helpers within the path, interrupt timing, stage
liveness and mapper restoration still require independent proof.

**No runtime chain to raw0A:$B7F7 is claimed.** R-002 OPEN.
The raw01 callsite finder is not a source-code coverage certificate.

Reproduction (owner ROM stays private):

```sh
python3 JP/tools/audit_room_selector_callers_0640.py --smoke
python3 JP/tools/audit_room_selector_callers_0640.py \
  --rom "/private/Akumajou Densetsu (Japan).nes"
```

**Testing:** exact 4,828-byte committed Python Git blob was matched
to the locally executed owner-ROM and negative-fixture source; private
owner ROM-backed audit and smoke PASS. New Windows/Linux CI smoke is
wired, not yet independently observed.

Strict semantic PRG 49,504/262,144 (18.8843%), VPP 27/100,
checkpoint0508, frontier $FB96; RESUME_STATE unchanged.
