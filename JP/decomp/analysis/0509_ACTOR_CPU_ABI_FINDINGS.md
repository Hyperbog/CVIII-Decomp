# 0509 source-stepped original actor helper ABI regression (provisional)

## Proven scope

The ROM-authenticated fixed PRG31 routines at CPU $FF06, $FF15 and $FF24 are stepped instruction-by-instruction by [the bounded test](../tools/audit_actor_cpu_abi_0509.py). The test verifies original full-file SHA-256 and the already certified $FF06-$FF11 (12 bytes) and $FF14-$FF55 (66 bytes) source-block hashes before execution.

- 4096/4096 occupancy masks across the twelve available actor slots ($054F-$055A): source A/X, zero/negative/carry flags, return stack and unchanged occupancy bytes match the native actor scan contract.
- 256 X values at $FF15 and 256 at $FF24: source indexed STA sequence matches all native 4-field and 18-field offsets; full 2 KiB RAM mutation map, A/X/P and JSR/RTS stack balance are tested.
- 44,538 original-source instructions fetched; deterministic outcome digest **6f554d451b36f06e9d25ea8f40fa3248c6974c34d0a135de25d51a451a371b7b**. [Compact report](0509_actor_cpu_abi_report.json).

## Interpretation / non-claims

This is a bounded independent **test-only** NMOS-6502 interpreter for the exact helper opcodes, not full original-game reference execution or a dynamically connected native decomp runtime. This is stronger than a ROM byte-hash and pure C++ RAM-write check, but is **not** a full native-vs-Mesen register/cycle trace. Synthetic occupancy bitmaps demonstrate input-conditioned code behavior, **not** that the original game executes all such inputs. The full-scan fallthrough uses $FF12-$FF13, which was uncredited in 0508; it remains **uncredited**. Existing strict PRG stays **49,504/262,144**, VPP **26/100**, last completed source checkpoint **0508**, fixed frontier **$FB96**.

Run with the exact original Japanese ROM:

    python3 JP/decomp/tools/audit_actor_cpu_abi_0509.py "Akumajou Densetsu (Japan).nes" --report /tmp/0509_actor_cpu_abi.json
