#!/usr/bin/env python3
"""JP0641 synthetic and tamper test. No fake original emulator evidence."""
from __future__ import annotations
import hashlib
import json
import tempfile
from pathlib import Path
from jp_scenario_preflight_0641 import ROM_SHA, SCHEMA, input_events, preflight


def expect_fail(path: Path, **options) -> None:
    record = preflight(path, **options)
    assert record["status"] == "FAIL" and "error" in record, record
    assert not record["gameplay_parity_proved"]
    assert record["checks"]["reference_gameplay"] == "NOT_EXERCISED"


def run() -> None:
    with tempfile.TemporaryDirectory(prefix="jp0641-") as tmp:
        parent = Path(tmp)
        script = parent / "buttons.txt"
        script.write_bytes(b"90 START\n93 -\n")
        digest = hashlib.sha256(script.read_bytes()).hexdigest()
        base = {
            "schema": SCHEMA, "id": "title-start-preflight", "rom_sha256": ROM_SHA,
            "frames": 300, "start": {"type": "power_on"},
            "config": {"ppu": "LLE", "edition": "Original"},
            "input": {"file": script.name, "sha256": digest,
                      "format": "nesrecomp-frame-schedule/v1"},
            "reference": {"engine": "mesen2", "sha256": None},
            "native": {"engine": "nesrecomp-cycle", "sha256": None},
        }
        path = parent / "scenario.json"
        def write(obj):
            path.write_text(json.dumps(obj), encoding="utf-8")
        write(base)
        good = preflight(path)
        assert good["status"] == "PASS" and good["checks"]["manifest_and_input"] == "PASS"
        assert good["checks"]["retail_rom"] == "NOT_EXERCISED"
        assert not good["gameplay_parity_proved"] and good["new_vpp_points"] == 0
        for mutation in (
            {**base, "schema": SCHEMA + "-unknown"},
            {**base, "frames": True},
            {**base, "frames": 12001},
            {**base, "start": {"type": "savestate"}},
            {**base, "config": {"ppu": "HLE", "edition": "Original"}},
            {**base, "rom_sha256": "0"*64},
            {**base, "extra": "unknown"},
            {**base, "input": {**base["input"], "file": "../buttons.txt"}},
            {**base, "input": {**base["input"], "sha256": "0"*64}},
            {**base, "native": {"engine": "nesrecomp-cycle", "sha256": "G"*64}},
        ):
            write(mutation)
            expect_fail(path)
        path.write_text('{"schema":1,"schema":2}', encoding="utf-8")
        expect_fail(path)
        write(base)
        for bad in (b"90 START\n90 -\n", b"90 START\n85 -\n", b"300 START\n",
                    b"90 START+START\n", b"90 FOO\n", b"90 START + B\n",
                    b"90 START\t\n", b"\xff\n", b"# empty\n"):
            try:
                input_events(bad, 300)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid input schedule accepted: " + repr(bad))
        fake = parent / "native.bin"
        fake.write_bytes(b"synthetic-test-only")
        expect_fail(path, native=fake)  # no asserted executable fingerprint
        pinned = {**base, "native": {"engine": "nesrecomp-cycle",
                                    "sha256": hashlib.sha256(fake.read_bytes()).hexdigest()}}
        write(pinned)
        assert preflight(path, native=fake)["checks"]["native_executable"] == "PASS"
        fake.write_bytes(b"tampered-synthetic-exe")
        expect_fail(path, native=fake)
        write(base)
        badrom = parent / "fake.nes"
        badrom.write_bytes(b"NES\x1a")
        expect_fail(path, rom=badrom)
        script.write_bytes(b"90 START\n94 -\n")
        expect_fail(path)
    print("PASS JP0641 ROM-free manifest, input, identity and status negative fixtures")


if __name__ == "__main__":
    run()
