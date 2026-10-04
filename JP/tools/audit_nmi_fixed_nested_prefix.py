#!/usr/bin/env python3
"""Compatibility wrapper for the corrected 04FF bounded audit.

The original version of this tool over-counted the raw `$F3DD-$F7FF` interval by
74 bytes that were not consumed by the admitted 26-root graph.  The controlling
audit is now `audit_nmi_fixed_2c_head.py`, which proves exactly 931 genuinely new
instruction/operand bytes and keeps the four unreached gaps explicit.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("audit_nmi_fixed_2c_head.py")), run_name="__main__")
