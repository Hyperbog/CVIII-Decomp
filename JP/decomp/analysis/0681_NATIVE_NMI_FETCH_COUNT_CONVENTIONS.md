# JP0681 — CPU-cycle window versus trace-event ordering

The first JP0681 owner-side audit failed with `ValueError: Fetch count disagrees with JP0680 aggregate`. Source review identifies a test-definition mismatch, not a proven CPU execution change.

The earlier JP0680 sanitizer counts `FETCH_PROCEED` with `edge.cyc <= fetch.cyc < discarded_fetch.cyc` independent of trace-record index. JP0681 v1 instead counts strictly after the `EDGE_LATCH` record's index. At CPU-cycle boundaries multiple records can share the same `hw.cycles` value: a fetch logged before the edge in the same numbered cycle satisfies JP0680's filter, but not JP0681's. The owner has not shared the private raw log, so the actual cause must be confirmed by owner-side execution.

The privately delivered JP0681 v2 analyzer computes *both* counts, validates the original JP0680 SHA and count/chronology gates unchanged, and only permits an explained difference consisting of same-cycle pre-edge `FETCH_PROCEED` records. All other mismatches fail closed. Twelve ROM-independent unit tests pass, including same-cycle timestamp collision and tampered count tests. The fix changes neither emulator executable nor emulation timing. The public repository contains no ROM, private events, PC/opcode, bus or executable.

The original JP0680 field named `completed_fetches_after_edge_before_discarded_nmi_fetch` counts non-discarded fetch events, **not completed instructions**. The earlier JP0676 CPU/bus witness independently established the additional completed native instruction. Cross-engine NMI signal/poll-phase parity remains unresolved; no CPU timing patch is authorized.
