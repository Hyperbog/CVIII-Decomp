# JP 0560 — source-derived C++ room selector for physical VRC6 bank raw0A

This phase prioritizes **6502 ASM → readable native C++**, rather than asking
for gameplay recordings. The original Japanese ROM is already byte-for-byte
reconstructed by the existing 25-module source pipeline.

`JP/native/bank0a/room_selector_native_0560.hpp` provides a reusable,
host-native implementation of the original 6502 $801E–$8046 three-stage
pointer selector. Its hierarchy is data, not executable code: selectors
$34/$35/$36 index $92AE, then a 64-entry middle table, then a
135-choice leaf table. The results correspond to CPU zero-page
$06/$07, $04/$05, and $95/$96 respectively. The two payload classes
are four-byte cells and seven-byte streams; fields are **not** assigned
unsupported gameplay meaning.

The constructor validates 15 stage roots, 64 middle roots, 135
third-level choices, bank-local bounds, and table ordering. The
operation fails closed on invalid selector indexes, out-of-bank
words, malformed hierarchy, or payload addresses outside the original
structural pools. It takes a privately supplied physical bank image at
runtime and embeds no copyrighted ROM bytes.

The existing `static_bank0a_driver.cpp` now independently computes
the native C++ result for **every one of the 135 producer-bounded
selector triples**, comparing all three native pointers to the result
of executing the original statically compiled 6502 instruction path.
The existing `test_static_bank0a_0552.py --rom` will independently
compare that output to the existing original-opcode reference emulator.

The ROM-free `jp_room_selector_native_0560` CTest uses a fully
artificial, structurally valid 15/64/135-link bank image and checks
all 135 selections and invalid-input corruption cases.

## Verification

```sh
cmake -S JP/native/boot -B /tmp/jp-native
cmake --build /tmp/jp-native --parallel 2
ctest --test-dir /tmp/jp-native --output-on-failure

# Additional authenticated original ROM vs compiled CPU vs direct native C++:
python3 JP/tools/test_static_bank0a_0552.py \
  --rom '/private/Akumajou Densetsu (Japan).nes'
```

**Scope:** one bank0A semantic subroutine, not a complete game. Source-derived
data paths do not imply natural entry liveness. Existing 2,357 bank0A
static opcode instruction sites are unchanged, including 1,365 candidates
that stay disabled by default. Historical 49,504/262,144 strict PRG,
4,261 compiled sites, and 27/100 VPP remain unchanged. No hardware
or gameplay-frame parity is claimed.
