# JP 0601 — Synchronized original PPU frame evidence

**Status:** native read-only diagnostic and paired-schema validators added;
authentic Japanese game frame captures are still pending.

## Scope

JP0600 samples actual physical CHR pattern reads during every 60th
frame. These reads can confirm that the original hardware fetches from
the locally cached CHR-ROM bytes, but they cannot by themselves
demonstrate how scrolling, sprites, priority, palette or nametable
selection produces the picture.

JP0601 uses the **original** pinned NESRecomp PPU's publicly exposed
output state *after the same frame* and *before* the CHR hook is
disabled. It emits one metadata-only record per sampled frame
to `CVIII-Frame-Evidence.csv`. The record includes:

1. Unmodified PPU 256×240 9-bit color/emphasis index hash (FNV-1a64).
2. Unmodified background opacity mask hash (FNV-1a64).
3. The 240 per-visible-line `CycLine` records, serialized explicitly as
   `[v_lo,v_hi,fine_x,ctrl,mask]` so C padding cannot vary the hash.
4. Background opaque pixel count, active background lines, active
   sprite lines, total physical CHR reads, mismatched reads, invalid
   mappings and within-scanline bank transitions on that **same frame**.

The host only observes `cyc_frame_index()`,
`cyc_frame_bg_opaque()`, and `cyc_frame_lines()`; they are publicly
supported by the pinned cycle runtime. It performs no emulated hardware
writes, no extra PPU reads, and no image replacement. Frame hashes are
metadata, not image assets or a new renderer.

## Contract tests and reader

`JP/recomp/native/enhanced/cviii_frame_evidence_0601.{h,c}` is a
host-independent C11 implementation. `JP/decomp/tools/
cviii_frame_evidence_test_0601.c` uses invented pixel arrays to check
active-sample gating, rendered-line accounting, and rejection of
out-of-range 9-bit pixels and invalid opacity bits.

`JP/recomp/tools/jp_frame_evidence_report_0601.py` cross-checks the new
frame CSV with the **strict JP0600 per-scanline fetch CSV**. It checks
sorted sampled frame numbers (1,61,121,...), fixed hexadecimal hash
encoding, count/range consistency, and exact per-frame reconciliation
of valid/invalid fetches and observed bank transitions.
A blank frame with zero CHR reads may be present in the frame CSV
without a JP0600 fetch row. A JP0600 fetch record without a
corresponding original PPU frame record is an error.

The private Windows launcher invokes this checker after `-ChrAudit`,
and writes `CVIII-Frame-Evidence.json`. No copyrighted media or
authentic gameplay traces are committed to CI. Both C11 native
and CSV/Python tests use invented data; the complete Windows SDL2
binary and synthetic mapper24 frame hashes are separate CI gates.

## Evidence boundary and next work

A valid JP0601 report proves internal **sample alignment**, not final
pixel equivalence to a hypothetical cache-backed renderer. Source
CHR byte parity and original PPU output evidence are related but
different. Actual Japanese retail gameplay reports from village,
forest, clock tower, ship, castles, bosses and all companions are
still required before implementing a renderer substitution.

Original gameplay and password tools remain unchanged; Universal NES
Studio stays deferred. Strict semantic PRG 49,504/262,144; VPP 27/100
and fixed PRG31 FB96 frontier unchanged.
