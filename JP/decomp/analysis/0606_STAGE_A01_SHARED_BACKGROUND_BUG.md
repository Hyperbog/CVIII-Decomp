# JP0606 - Stage A-01 shared PPU background corruption

Status: read-only diagnostic implemented; native Linux C11 and Windows
SDL2 CI both passed. Authentic Japanese A-01 comparison still pending.
The owner reported widespread purple/white/noisy backgrounds in A-01
in both internal Original reference and player-facing Enhanced. The
Stage 1 Trevor/torch and doorway flicker reports remain separate.

## Physical JP mapper24 observations

Owner-authenticated JP ROM SHA-256:
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
262,144 PRG bytes and 131,072 CHR-ROM bytes, mapper 24 (VRC6a).

An independent local PRG scan found 12 literal STA $B003 byte motifs.
Several directly preceded by LDA immediates, including:
- PRG 0x01BEE: LDA #$20
- PRG 0x060D1: LDA #$28
- PRG 0x06127 and 0x064BA: LDA #$2C
- PRG 0x064F3, 0x077E1, 0x3E044: LDA #$20
- The indirect load at PRG 0x01F5A refers to a local small table with
  four bytes at physical 0x01F46..0x01F49: $20,$20,$20,$24.

These are STATIC matching bytes, not an execution trace establishing
which writes happen in any particular stage. NESdev VRC6 hardware docs
describe normal Japanese board $B003 values $20,$24,$28,$2C and
bit7-enabled variants. The pinned backend's common mode-0 CIRAM
mapping is structurally consistent with these values. Therefore no
speculative VRC6 mapping change was introduced.
Reference: https://www.nesdev.org/wiki/VRC6

## Diagnostic change

Earlier JP0600 CHR fetch parity measures the physical pattern bytes,
but does not capture the original nametable tile ID or attribute byte.
The JP0606 private hw_ppu.c overlay adds a read-only callback after
the original nametable/CIRAM bus read, only during actual mapper24 PPU
/RD and sampled frames, without substituting any returned byte.

It logs by scanline: original tile and palette-attribute read counts,
first observed values, CIRAM versus cartridge CHR-ROM nametable source,
invalid bus events, and a dot/address/value/source-sensitive hash.
Even rendering-off frames are represented by an explicit empty marker.
The JP0606 report validates row counters and aligns frame IDs against
the original PPU frame fingerprints from JP0601.

The new owner-local diagnostic files are CVIII-NT-Fetch.csv and
CVIII-NT-Fetch.json. The capture workflow preserves its JP0602
five-file v1 manifest for historical compatibility; the new files
remain supplemental evidence in the same private scene directory.

## Private A-01 capture

From the rebuilt private AlphaCandidate directory, run:

    .\Capture-QA-0602.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Scene a01-purple-background -Area castle -Character Trevor -Checkpoint A-01

Substitute the actual authenticated original-Japanese ROM path, warp
to A-01 using the now-tested F10/password bootstrap, allow the glitch
to display for at least 10 seconds, and close normally. Compare with
a screenshot of the exact scene in MesenCE or authentic Famicom.

If MesenCE displays the same noisy pixels, determine whether they are
original stage art or an authentic quirk before altering the output.
If MesenCE does not, use the aligned nametable/attribute, CHR fetch,
mapper register, and frame logs to locate the first divergence.

Known original-JP game bugs include a one-pixel door shake and certain
6-4/6-5 left-edge background glitches; these do not establish that
the owner's widespread A-01 noise is authentic.
Reference: https://www.nesdev.org/wiki/Game_bugs

This work does NOT claim pixel parity, fix the observed A-01 defect,
or touch game timing, CPU/PPU state, mapper registers, sprite priority
or gameplay. Native synthetic CI and Windows target compilation pass,
but retail-JP A-01 runtime validation remains pending.

Strict PRG semantic coverage 49,504/262,144 and VPP 27/100 unchanged.
