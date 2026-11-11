# JP0844: private seeded Windows Alpha integration

The current Windows Alpha compiler previously invoked JP0575 without the
private --jp0837-dir input, so the JP0842 optimized C11 engine was not used.
Its launcher also reused cached unseeded executables.

JP0844 adds a small shared PowerShell resolver to discover the already
captured owner-private JP0837 profile, explicitly select an alternate path,
or preserve the unseeded fallback. The Python JP0842 gate independently
validates original Japanese ROM fingerprint, pinned engine expectations,
native/interpreter hashes, and physical bank-qualified seed contents.

Build-Alpha.ps1 forwards the verified evidence to the unchanged JP0575
compiler and checks the emitted seed count, SHA-256 and miss-log source
before packaging. Build-And-Play.ps1 rebuilds a stale candidate rather
than silently reusing an unseeded binary, but still reuses a candidate
whose seed provenance and executable hash match.

The release manifest bundles the ROM-free resolver only. It never embeds
the original ROM, controller captures, generated bank-qualified seeds,
or native trace logs. Original/Enhanced rendering, mapper, VRC6 IRQ,
audio and savestate code are not modified.

The automated Windows workflow tests profile discovery, explicit rejection,
hash-based cache freshness, executable tampering and manifest completeness
with synthetic data, and compiles its existing synthetic ROM fixture.

Existing JP0843 evidence: 3901 matching baseline native hashes with
99.999963% CPU cycles executing natively, limited to the same gameplay
route. The new windowed Alpha is not claimed to have been run privately.
