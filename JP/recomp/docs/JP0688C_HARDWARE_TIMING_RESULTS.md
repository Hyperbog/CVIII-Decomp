# JP0688c — Pinned NESRecomp hardware-timing validation results

**Evidence status:** **16/16 tests report PASS**; independently cross-checked against the owner's WRAM excerpts. No CPU, PPU, IRQ, game or Enhanced Edition source modifications.

## Inputs and exact scope

- Standalone NESRecomp `cyc_interp` source pin: `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`.
- Public test ROMs (Blargg / `christopherpow/nes-test-roms`) pin: `95d8f621ae55cee0d09b91519a8989ae0e64753b`.
- Four **public NROM tests**, each using a *private header-only copy* with iNES byte 8 set to 1 (8 KiB PRG RAM) for Blargg's `$6000` test-output protocol; no test program/CHR bytes changed.
- CPU/PPU alignments `0, 1, 2, 3`; 900 frames per run, WRAM sampled after frame 899.

| Blargg test | Align 0 | Align 1 | Align 2 | Align 3 |
| --- | --- | --- | --- | --- |
| `02-vbl_set_time` | PASS | PASS | PASS | PASS |
| `04-nmi_control` | PASS | PASS | PASS | PASS |
| `05-nmi_timing` | PASS | PASS | PASS | PASS |
| `5-branch_delays_irq` | PASS | PASS | PASS | PASS |

Every recorded exit code is `0`, every status byte `$6000=00` and every test signature `$6001-$6003=DE B0 61`. Evidence excerpts agree with the JSON results in all 16 cases; the independent checker exits `0`. The three 32-byte WRAM excerpts for each test are identical across alignments.

### Diagnostic checks against the Blargg sources

- `02-vbl_set_time`: the recorded nine-line sequence is `- V` four times, `- -` once, and `V -` four times (the documented expected pattern).
- `05-nmi_timing`: the recorded sequence is `4 4 4 3 3 3 3 3 3 2`, matching the test's source documentation.
- `04-nmi_control`: the recorded text includes `Passed`.
- `5-branch_delays_irq`: each result is `00`, but the preserved 96-byte excerpt does **not** include the complete diagnostic text; this gate relies on the test's own internal CRC/status check for its terminal PASS.

### Verification provenance

Owner-supplied JSON matrix SHA-256:
`48f7a2d463c47a7ad40cbcd79d30ac58798441d71e73565481875f6ce147ebfb`

Owner-supplied WRAM excerpt SHA-256:
`48bf7c0c477c2eb8988f8feb08dd62f5f8933dcca84bb05cfc668df6f077fc46`

The checker verifies **internal consistency of independently provided result and WRAM files**; these SHA-256 values identify the reviewed uploads. They do not independently authenticate the live Windows execution, ROM build environment, or reference hardware.

## Interpretation / exclusions

Under these test conditions the pinned standalone NESRecomp interpreter passes all 16 selected NMI/VBlank/branch-IRQ tests. **No demonstrated defect** calls for changing its hardware core. This is not a comprehensive NES hardware certification, a Mesen2-vs-native paired run, or proof of cycle-exact Japanese Castlevania III gameplay/audio parity. No original/gameplay/Enhanced regression was rerun for this stage, because no runtime code was changed. VPP and certified PRG scores remain unchanged.

This commit contains only a ROM-free runner, evidence verifier, procedure and compact results. Public ROM binaries, private header copies, game ROMs/NSF, `*.mem.txt`, `*.log`, and owner Windows binaries are excluded. **Draft PR #11 remains unmerged**.
