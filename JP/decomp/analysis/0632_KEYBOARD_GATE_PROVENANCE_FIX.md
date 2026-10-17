# JP0632 — Four-stage keyboard-order regression gate correction

JP0631's exact-line SDL anchor repair advanced the pinned-source CI
to JP0621's event-order assertion. That assertion incorrectly expected
developer shortcuts ahead of F6 Audio and F10 stage. The original
pinned SDL dispatch plus JP0594/JP0620 patch insertion order is
F6 → F10 → developer, and JP0623 prefixes F4. The updated gate
checks the physically generated source ordering while preserving
upstream exact Git-blob authentication and fail-closed source anchors.

This corrects *our previous test/documentation*, not original Japanese
6502 behavior. New CI must still pass; no live Mesen session or
source-byte credit follows from this test repair.

R-002 OPEN; strict PRG 49,504/262,144, VPP27/100, checkpoint0508,
fixed frontier FB96 unchanged.
