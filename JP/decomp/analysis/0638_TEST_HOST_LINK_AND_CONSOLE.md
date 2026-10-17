# JP0638 — CI host mock and Windows console encoding corrections

The JP0637 Linux cycle workflow (run 38828810766) completed
the pinned JP0621/0623/0625/0626 source gates, then failed in the
ROM-free C11 edition link:

    undefined reference to cyc_cycle_count

The exact upstream pinned `cyc_core.h` declares
`uint64_t cyc_cycle_count(void)`. This is provided by the linked
NESRecomp CPU core in the real host but absent from the standalone
test executable. JP0638 adds an explicit inert `uint64_t`
mock returning zero to `test_cviii_edition.c`, not to the production
C11 edition module. Audio-session cycle epochs are not authentic
CPU-time evidence in this ROM-free fixture.

The same JP0637 Windows workflow (run 38828810587) passed the
pinned 4-, 5- and 6-stage source checks, then failed while printing
a JP0626 smoke message containing a Unicode bidirectional arrow
under the Windows CP1252 output encoding. Replacing that diagnostic
with ASCII `Audio<->Pause` preserves the test and SDL patch semantics.

Both corrections concern test infrastructure only. Fresh independent
CI must establish whether the underlying seven-layer native build
and complete host verification now pass; no actual Mesen gameplay
capture, original 6502/native replay, or Windows playtest is claimed.

Strict semantic PRG 49,504/262,144 (18.8843%), VPP27/100,
checkpoint0508, $FB96 frontier and R-002 remain unchanged.
