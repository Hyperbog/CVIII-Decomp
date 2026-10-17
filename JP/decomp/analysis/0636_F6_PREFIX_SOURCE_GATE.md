# JP0636 — F6 callback prefix audit repair

JP0621's pinned-source checker sliced its generated SDL event handler
*after* the F6 audio callback and searched that suffix for the guard,
which in the real JP0620 overlay appears immediately *before* it.
The check therefore rejected the authenticated unchanged source.

JP0636 validates one contiguous, exact F6 stage-exclusion guard
plus callback. The ROM-free smoke rejects changes to the guard,
callee or duplicated hook. Upstream SDL blob identity, marker counts,
other keyboard handlers, save/load and frame-pause checks remain strict.

This fixes our source audit, not shipped Japanese 6502 game behavior.
Native/Windows Actions still need to pass. No genuine Mesen capture,
native parity or strict byte promotion is claimed.

Strict PRG 49,504/262,144, VPP 27/100, certified 0508,
frontier FB96, R-002 OPEN.
