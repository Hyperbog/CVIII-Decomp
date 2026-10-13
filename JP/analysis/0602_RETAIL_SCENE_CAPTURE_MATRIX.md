# JP0602 — Repeatable owner-only retail gameplay PPU/CHR scene QA

**Implementation status:** capture management, integrity/provenance
metadata, matrix validator and synthetic CI are available. No
authentic Japanese *gameplay* capture is claimed by this change.

JP0600 and JP0601 already correlate actual mapper24 physical CHR
pattern reads with original PPU frame hashes. However, all diagnostic
runs initially wrote the same CSV/JSON paths under AlphaCandidate,
overwriting prior stages. This prevented credible multi-stage QA.

## JP0602 scope

- Launch-Alpha.ps1 adds opt-in -AuditOutDir, only with -ChrAudit.
  All CHR-Audit/CHR-Fetch/Frame-Evidence CSV and JSON reports are
  written under that directory. Existing defaults are preserved.
- Capture-QA-0602.ps1 runs the authenticated Japanese retail ROM
  with Enhanced's **original PPU renderer**, producing a new private
  QA/<scene>-<timestamp>-<random> folder every run. Users label
  area, scene, companion, event type and optional checkpoint.
- All 5 required evidence files get size and SHA256 attributes in a
  capture.json manifest, plus native executable and asset-index
  SHA256 and the pinned ROM fingerprint. No ROM or CHR bytes are put
  into the QA metadata.
- jp_qa_matrix_0602.py verifies each manifest and original-JP
  declared fingerprint, hashes and bounded file sizes, disallows
  symlinked evidence, reruns strict JP0600/0601 cross-checks, and
  compares saved summaries against original diagnostic CSVs.
- It reports which of eight target areas (title, village, clock
  tower, forest, ship, castle, boss, companion) and characters have
  adequately sampled source-byte evidence, defaults to >=10 samples,
  and flags corruption, frame shortage, source-byte mismatches and
  mixed native executables.

The metadata and scene labels are user claims, not runtime-authenticated
stage IDs. A valid scene trace means the *observed* hardware CHR
source bytes matched the cache on the sampled frames, not that a
separate cached renderer produced equivalent final pixels. It also
does not test the correct dialogue, encounter scripting, gameplay
recruitment or original password stage initialization.

## Gates and follow-up

ROM-free Python self-test uses invented CSV streams, a paired
original PPU fingerprint, file hash tampering, a falsely updated
summary and a wrong ROM ID. Both Linux C11 and Windows SDL2 test
workflow trigger paths include this script, without ever handling
the commercial ROM. Private Windows executable captures are the
next required owner action. Once representative traces exist, compare
actual frame outputs from any opt-in cache renderer side by side;
do not enable substitution before that test.

No PRG semantic reconstruction change. Strict PRG 49,504/262,144,
VPP 27/100 and the PRG31 $FB96 frontier remain unchanged.

## JP0602 mapper evidence gate

The JP0602 matrix now parses and validates every JP0599 mapper/palette
sample against the exact original-PPU frame-evidence sample IDs. It
requires sequential samples at frames 1, 61, 121, etc., valid VRC6
control/mode, eight physical CHR banks, and a 32-byte palette field.
Out-of-range banks, missing samples and altered fields fail closed.
Actual mapper FAIL samples become a mapper_mismatch quality state and
do not satisfy area or character coverage, even if CHR source bytes
match. This is observational integrity, not independent pixel parity.

## JP0604 — First-run Git CLI recovery

Owner-provided Windows screenshot confirmed that the previous
`Build-Alpha.ps1` executed `git` with no subcommand. Its
PowerShell function named an external argv parameter `$Args`,
which is also an automatic PowerShell variable. The builder now
calls Git and Python with an explicitly named `-CommandArguments`
array, and CI tests the actual wrapper against a local synthetic
clone and pull (including spaces in repository paths). The
downloadable public build kit still contains no game or ROM data.

This build fix changes no gameplay or graphics renderer; strict
semantic PRG/CHR documentation metrics remain unchanged.
