# JP0729 — Private versioned and integrity-checked original-ROM resource cache

## Actual functionality

`cviii_resource_cache_0729.c/.h` implements a private, canonical little-endian `CVRSC029` schema-v1 file. It contains the source-authenticated original Japanese Stage 1 world atlas and the entire 8,192-tile CHR index, derived from the **owner-selected ROM**. The user's ROM is SHA-256 checked **on every launch**, before any cache data is trusted. A source mismatch, unknown schema, truncation, impossible room geometry, invalid palette index, CHR bitplane/pixel mismatch or payload SHA-256 mismatch causes an ordinary miss/rebuild.

Payload semantics (688,832 bytes): eight 24-byte room records (192 bytes), Stage 1's 16,640 tile IDs and 16,640 palette indexes (33,280 bytes), all 131,072 authentic CHR plane bytes, and 524,288 2-bit decoded CHR pixel values. Header (80 bytes) contains magic, schema, declared size, source ROM SHA-256, and payload SHA-256. Source indices are *not* guest state; none is written to original CPU or PPU RAM. Serialize values byte-by-byte; never serialize C pointers/padding/native struct layout.

The cache file is written to a process-specific temporary sibling and moved to its destination only after a complete write and close. On POSIX use `rename`; on Windows use `MoveFileExA(REPLACE_EXISTING | WRITE_THROUGH)`. A missing, unwritable or corrupted cache is an optional optimization failure, **not a game startup failure**. The game rebuilds the in-memory resources from the already-authenticated ROM. Cache bytes are copyright-derived and remain privately on the owner's machine; do not commit or distribute them.

The Windows Enhanced launcher passes `--stage1-resource-cache` under LocalApplicationData's `CVIII-Decomp/ResourceCache/japanese-vrc6-stage1-chr-v1.dat`, and `--stage1-world-rom` with the original SHA256-validated ROM. The core loader has a null-cache uncached API for clients that cannot write to disk. The current implementation does not yet persist/reuse the install-level ROM picker path between runs.

## Regression contract

- Both Linux strict-C11 and Windows-MSVC **Release** test variants exercise the actual runtime SHA-256 and original-image rejection logic; synthetic tests alone enable `CVIII_RESOURCE_TEST_SYNTHETIC_0727`.
- New synthetic cases verify disk roundtrip of all tile IDs, palette IDs and CHR source/pixel buffers, wrong source-ROM digest, a tampered SHA-256 checksum, an unknown schema version, cache repair from unchanged source, and a **different malformed ROM** not masked by a previously valid cache.
- Windows Release tests explicitly keep `assert` enabled; otherwise `NDEBUG` silently drops test assertions and their setup side effects.
- Loading cache is transactional for resources: any malformed file preserves the previously loaded atlas and index. Writing is best effort. Exact ROM hash remains a prerequisite for trusting *any* private cache.
- Game logic is **not** sourced from the cache, and this file is **not** a general editable/mod resource-pack format. A separate read-only default game-resource registry and mod override layer will be needed.

## Scope boundary

Cached: Stage 1 layout+attributes and 8,192 CHR patterns. Not cached yet: enemy placements, collision definitions, motion/interaction tables, special effects, other stage room layouts, music driver data, sound channels, localized text or gameplay code. Proven static atlas vs correct offscreen per-frame palette/CHR-bank animation remain different verification targets.

No original ROM/CHR/graphics files were added to Git. VPP 31/100, strict semantic PRG 49,504/262,144 unchanged.
