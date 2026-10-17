# Checkpoint 04F4 — `$ED46` pre-render helper preserves ZP `$10`

This checkpoint closes one pre-render NMI dependency from 04F3: whether the fixed-bank helper entered at `$ED46` can modify the persistent OAM attribute cache in zero-page `$10`.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

The checkpoint began with the planned 512-byte window `$ED46-$EF45`. That exposed control-flow edges to `$ED17`, `$EF5C`, and then `$EC85`. Per the project byte-budget policy, the span was expanded once to a still-bounded 1 KiB fixed-bank window that contains the complete reachable graph:

```text
PRG31:$EC00-$EFFF
size: 1024 bytes
SHA-256: e83c0d832fc23590c0dde2448a9943ef217ada4e4f520d0da0e3f85f863dc797
```

## Reachable control flow

Starting at `$ED46`, the audit follows all official-6502 branch and absolute-jump targets inside the 1 KiB window.

The path includes the previously external-looking local targets:

```text
$ED17
$EF5C
$EC85
```

After expanding to `$EC00-$EFFF`, the graph is closed:

- 323 reachable instruction starts;
- no `JSR` leaves the window;
- no `JMP` leaves the window;
- no conditional branch leaves the window.

Therefore there is no remaining transitive helper dependency for `$ED46` itself.

## Write-domain proof

No reachable instruction writes or read-modify-writes ZP `$10` or absolute `$0010`.

There are also no reachable dynamic/indexed store or RMW addressing modes whose effective address could alias `$10`.

The complete set of reachable write destinations is:

```text
ZP $00
ZP $1E
$0300
$2000
$2006
$2007
```

Representative flow around the entry is the PPU-command interpreter:

```asm
ED46  LDY #$00
ED48  LDX $0300,Y
ED4B  BEQ $ED82
...
ED54  STA $2000
...
ED64  LDA $2002
ED67  LDA $0301,Y
ED6A  STA $2006
ED6D  LDA $0300,Y
ED70  STA $2006
```

Other branches stream queued bytes from `$0300,Y` to `$2007` and eventually loop back to `$ED48`. The `$ED17` and `$EC85` paths likewise operate on `$0300` command data and PPU registers only.

## Result

**04F4 result: the NMI-called `$ED46` helper graph preserves ZP `$10`.**

This removes `$ED46` from the remaining pre-render attribute-cache provenance uncertainty.

Current pre-render external dependencies left from 04F3 are now:

```text
raw bank $0C : CPU $89E2
$E7FB / its inline-dispatch targets
```

Scope is intentionally limited to the reachable `$ED46` graph inside `PRG31:$EC00-$EFFF`; unrelated fixed-bank code in the same region is not claimed translated merely because it lies inside the byte window.

Reproducible audit: `tools/audit_nmi_ed46_zp10.py`.
