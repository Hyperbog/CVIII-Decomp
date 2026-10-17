# 0508 bulk: Native–Python VRC6 IRQ differential

Evidence is ROM-free cross-implementation compatibility, not independent NES hardware/reference-emulator parity. The existing C++ and Python VRC6 IRQ engines receive 4,488 identical ordered commands (F000 latch, F001 control, F002 acknowledge, mapper-24 mirrors and time advancement). The event stream covers 684,904 simulated CPU cycles. Six fields are checked after every command: latch, counter, cycle mode, enabled, enabled-after-ack and pending IRQ. All 4,488 snapshots matched. Deterministic output SHA-256: a4dbc1d52e7209a6b272e64333784510f120a15a5e0e8ade0d6fa7ec33822952.

The sample is not an independent original-emulator reference and earns no new VPP point. Strict PRG remains 49,404/262,144 (18.8461%); overall VPP 25/100; completed semantic checkpoint 0507; physical fixed frontier FB96. GitHub Actions compiles the native driver and runs the Python differential test without an original ROM.
