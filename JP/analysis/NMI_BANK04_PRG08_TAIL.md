# Checkpoint 04F8 — raw bank `$04` PRG08 tail closure

This checkpoint continues the pre-render shared-ZP `$10` provenance audit from 04F7. It closes the remaining physical PRG08 stream domain and uses a minimal PRG09 extension only where the final PRG08-rooted control-flow cycle requires it.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Exact byte accounting

The dependency span needed to close the PRG08-tail roots is:

```text
raw bank $04 / CPU $920A-$A011
3592 bytes
SHA-256 69e6d56aed2875f3f2840ebb4b5c52b844da4482a150a4db3647cd933bc79b8e
```

CPU `$920A-$9FFF` is physical PRG08. CPU `$A000-$A011` is an 18-byte physical PRG09 extension required by the same question: the stream rooted at `$9E85` reaches `FE FF 85 9E` at `$A010`, which jumps back to `$9E85` and closes the cycle.

04F7 already counted one mode-probe byte at every later bank-$04 root. Eleven of those probed root bytes lie inside the 04F8 span. Therefore:

```text
3592 dependency bytes
-  11 bytes already counted by 04F7
=3581 new ROM bytes for 04F8
```

This remains inside the 500-5000-byte checkpoint budget.

## 04F7 semantic correction

04F7 used the first raw `$FF` after each in-window root as a stream-end marker. That wording was too strong. Eleven of the 23 recorded first-`$FF` positions are actually the `$FF` marker in the command form:

```text
FE FF <pointer-low> <pointer-high>
```

The parser at `$8543` treats that sequence as an absolute stream-pointer load, not a terminator.

This correction does **not** invalidate 04F7's safety result. The 04F8 audit adds a recursive command/pointer decoder that rechecks all 23 prior roots using the actual alternate-parser command grammar. It proves:

- no reachable `$E7` command occurs in the 04F7 root set;
- every `FD`/`FE` pointer edge stays inside `$87AE-$9209`;
- no counted loop lacks a preceding `FB` loop anchor;
- the latest reachable command byte is `$9208`.

So the prior 23 roots remain closed, but the correct reason is command/pointer reachability, not first-raw-`$FF` termination.

## 04F8 metadata domain

Exactly 11 distinct bank-$04 roots begin in physical PRG08 after `$9209`:

```text
sound $5D, instrument $07 -> $920C
sound $5E, instrument $03 -> $92DB
sound $5E, instrument $04 -> $93FA
sound $5E, instrument $07 -> $95E3
sound $5E, instrument $00 -> $967E
sound $5E, instrument $01 -> $974D
sound $5E, instrument $02 -> $9900
sound $60, instrument $03 -> $99E9
sound $60, instrument $04 -> $9BAF
sound $60, instrument $07 -> $9D21
sound $60, instrument $00 -> $9E85
```

All were already proven by 04F7's mode probes to initialize alternate-parser mode.

## Recursive stream/control-flow result

The decoder mirrors the ROM's data-side control semantics for the common alternate parser:

- ordinary/note and `C?` commands advance one byte;
- `D?` consumes its four-byte record on instruments `$00-$04`;
- `E?` command lengths follow the local handler table;
- `FB` saves the loop anchor after itself;
- first `FD` loads a two-byte target and saves a return address; the paired `FD` returns;
- `FE nn` explores both counted-loop continuation and the saved `FB` anchor;
- `FE FF lo hi` loads the absolute stream pointer;
- `FF` is the actual stop command;
- instrument `$07` uses its distinct `$8031` parser rule before the shared `F?` handlers.

Across the 11 04F8 roots the recursive closure visits:

```text
3312 abstract parser states
3025 unique command addresses
```

The earliest reachable command is `$920C`; the latest is `$A010`.

Every resolved `FD`/`FE` pointer target stays inside `$920A-$A011`. The final cross-bank edge is:

```text
$A010: FE FF 85 9E  ->  $9E85
```

which is why the 18-byte PRG09 extension is required.

There are **zero raw `$E7` bytes** in `$920A-$A011`, and therefore zero decoded `$E7` commands. The unbounded `$842D` parameter-table edge cannot be activated by any of these 11 roots.

Because the executable alternate-parser core was already proven `$10`-clean in 04F7 and no new command path reaches `$842D`, these 11 additional roots preserve shared ZP `$10`.

## Result

**04F8 closes the remaining PRG08-rooted bank-$04 stream domain as ZP `$10`-safe.**

After 04F8:

```text
bank-$04 roots total          96
closed in corrected 04F7      23
closed in 04F8                11
remaining later PRG09 roots   62
```

The next unresolved bank-$04 root is `$A014`. Raw bank `$05` and fixed `$E7FB` remain untouched.

VPP remains **21/100** because transitive NMI helper closure is still incomplete.

Reproducible audit: `tools/audit_nmi_bank04_prg08_tail.py`.
