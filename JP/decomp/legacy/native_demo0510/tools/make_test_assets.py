#!/usr/bin/env python3
"""Generate PUBLIC-DOMAIN synthetic test frames for native host CI; no ROM data."""
from pathlib import Path
import sys

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: make_test_assets.py OUTPUT_DIRECTORY")
    d = Path(sys.argv[1]); d.mkdir(parents=True, exist_ok=True)
    for name, rgb in (
        ("title", (15, 25, 42)), ("intro", (50, 25, 45)), ("stage", (32, 59, 64))
    ):
        (d / (name + ".ppm")).write_bytes(
            b"P6\n256 240\n255\n" + bytes(rgb) * (256 * 240))
    # 25x34x4 host sprite, opaque generated pixels only.
    (d / "player.rgba").write_bytes(bytes((231, 224, 184, 255)) * (25 * 34))

if __name__ == "__main__":
    main()
