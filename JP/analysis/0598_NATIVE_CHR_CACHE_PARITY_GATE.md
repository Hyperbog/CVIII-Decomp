# JP 0598 — Native read-only CHR index / parity gate

**Scope:** one complete **presentation-asset subsystem** crossing the
JP0597 authenticated local archive and pinned NESRecomp Windows
Original/Enhanced host. This does not decompile PRG instructions.

The existing CHR archive contains 128 physical mapper24 1 KiB banks and
8,192 2bpp NES tiles. The `jp_asset_runtime_0598.py` exporter writes
a private fixed-size 655,368-byte native index:

- 8-byte ASCII magic `CVIII058`
- 131,072 bytes raw physical CHR (exact bank order, unaltered)
- 524,288 bytes palette-index pixels (64 indices 0..3 per 8×8 tile)

The export path verifies the JP0597 schema and physical table offsets,
recomputes canonical original-JP SHA-256 fingerprints for raw/indexed
CHR, and reproduces every indexed pixel from the raw tiles. A
preexisting index is compared **byte-for-byte** before reuse.

The C11 loader checks file size, marker, both independently recorded
original-JP FNV-1a64 digests, and reversibly reconstructs every byte of
all 8192 raw tiles from its 64 indexed pixels. FNV is an accidental
corruption detection gate, **not cryptographic authentication**.
The stronger SHA-256 provenance check occurs in the private Python
asset build/export path. The native loader does not execute file
instructions and does not mutate game/hardware memory.

`JP/native/enhanced/cviii_edition.c` registers
`--asset-index PATH`, loads valid owner-private data, then does
nothing else with the cache. No native rendering replacement has been
enabled; the existing `cyc_frame_argb` remains authoritative.
Launch-Alpha.ps1 supplies this path for Enhanced only. Original
launch command and game semantics remain unchanged. The index
is optional to preserve compatibility with existing private builds.

**ROM-free gates:** Python synthetic layout/tamper tests; standalone
C11 synthetic acceptance + canonical-JP-refusal + changed-pixel
rejection; actual Windows C11 SDL2 game target compilation and existing
synthetic frame-hash validation. In a local private test the C reader
also successfully accepted the index reconstructed from the owner's
authenticated Japanese ROM. Retail Windows GUI launch/parity and
mid-frame VRC6 bank mapping have not been established by synthetic CI.

Next gate: instrument/observe actual physical CHR bank choices and
active palette/sprite state at a captured retail gameplay frame,
then compare the read-only cached tile pixels with that frame's
engine decoding before allowing an opt-in Enhanced renderer to use them.
Do NOT substitute arbitrary cached pages for PPU address-space data.

Strict PRG 49,504/262,144 and VPP 27/100 unchanged.
