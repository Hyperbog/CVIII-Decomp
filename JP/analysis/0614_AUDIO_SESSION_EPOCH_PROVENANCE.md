# JP0614 — Bound audio capture session and save/load epochs

**Status:** ROM-free C11/Python regression tests PASS. Private retail-JP-ROM Windows runtime capture and independent MesenCE comparison OPEN.

## Original uncertainty

JP0610 captures actual 2A03/VRC6 chip writes. JP0612 captures actual fixed PRG31:$E249 sound-request entries. JP0613 showed noncausal CPU-cycle proximity but could not prove that two CSVs belonged to one uninterrupted session or correctly handle save-state cycle rewind.

## Owner-private trace provenance

The new [C11 epoch logger](../native/enhanced/cviii_audio_session_0614.c) runs only when enabled by the launcher. A fresh lowercase 32-hex GUID identifies the session. Existing host callbacks **power_on** and **state_loaded** flush both audio CSV files, then append a row to CVIII-Audio-Epochs.csv with session_id, epoch, event, cycle, request_rows and register_rows. Row counts are cumulative and do not rewind when the emulated CPU clock does. Neither 0610's eight-column nor 0612's ten-column event CSV schema was changed.

After successful native game exit, Launch-Alpha.ps1 -AudioTrace writes CVIII-Audio-Session.json containing the session GUID and individual SHA-256 hashes for all three captured CSVs. The [JP0614 verifier](../tools/jp_audio_session_verify_0614.py) checks the exact file names/hashes, marker order, cumulative row-count bounds, within-epoch cycle order, fixed E249 request PC, and audio-chip register labels. CVIII-Audio-Epoch-Verification.json contains counts per epoch, not a claim that any sound request caused a hardware write.

The existing JP0610 **whole-file** register analyzer runs only for a one-epoch capture. The older JP0613 proximity checker is not automatically applied to multi-epoch files. This avoids falsely treating pre-load cycles and rewritten sound-driver state as one timeline.

## Verification and exclusions

- Strict C11 C logger test PASS: start, consecutive loads including cycle rollback 300 to 40, invalid GUID/duplicate open, inconsistent decreasing row count.
- Python verifier fixture PASS: two epochs including 260 to 20 cycle rollback; rejection of mismatched SHA-256 capture and session GUID; syntax compilation passed.
- Pinned NESRecomp revision 2b4fcdb98c9e702be3fb365cfc645003c50b5fc1 has host state_loaded callback after successful cyc_state_load_file. Actual private Windows compilation and gameplay have not yet been executed here.
- GitHub CI regression gates are committed; latest run outcomes are not established.
- SHA-256 file consistency and a self-generated GUID do **not** cryptographically attest emulator provenance, original-console execution or music/SFX causal ownership. State restore paths bypassing the host callback and incomplete recordings need separate checks.
- Source events suppressed before E249, accepted/delayed/rejected commands, voice scheduler semantics, sample/waveform parity and independent polyphony remain OPEN.

The original JP ROM (SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28), its NSF and license-bearing external runtime are not committed.

**Accounting unchanged:** verified semantic PRG 49,504/262,144 (18.8843%), VPP 27/100, certified checkpoint 0508, physical fixed-bank frontier $FB96. RESUME_STATE.json untouched.

**Next gate:** obtain private real-JP-ROM CSVs with a save/load and compare per-epoch source register/caller evidence to independent MesenCE; only then investigate original-game producers and lost events.
