# 0510 — Native PC title → introduction → Stage 1 preview

**Status: playable provisional host-native prototype. NOT original Castlevania III runtime/gameplay parity.**

Source: [C++ host-native runtime](../native_demo0510/src/main.cpp), [CMake project](../native_demo0510/CMakeLists.txt), [build/run guide](../native_demo0510/README.md). The user-specific Linux x86-64 package has the playable binary and offline Japanese Mesen screen-reference asset pack. The public Git source does not embed the original retail ROM, original image stills, savestates, code/data logger, external emulator or lossless game data.

## Implemented / tested

- Real C++20 PC title → timed/tappable intro → Stage 1 sample scene → demo completion/restart; X11 Linux host window and a native Win32/GDI source front-end.
- Native host input: left/right, jump, attack, restart/quit; deterministic headless controls and binary PPM frames; private still-reference raster assets from the user-supplied authenticated Japanese ROM.
- Source-locked **first-free 12-slot actor scan** from original JP fixed PRG31 $FF06 and **eighteen field clear addresses** from fixed $FF24, both already authenticated by [0509 source lift](0509_ROM_FREE_ACTOR_PIPELINE.md). The current native object actions merely demonstrate those local helper contracts.
- Linux GCC14.2 Release compilation, X11 window launch under Xvfb, ROM-free state machine & asset-backed headless frame tests, both repeated under AddressSanitizer/UndefinedBehaviorSanitizer, and fresh-package unpack/rebuild/checksum replay **passed**.

## Explicitly incomplete / uncredited

The intro/title art and one-screen stage background are offline original-emulator screenshots used as **static licensed-reference placeholders**, not decoded original CHR/PPU rendering, scroll, exact room layout or dynamic movie scripting. Host-scripted jump, attack, enemy, floor, stage-clear condition and sprite bitmap presenter are not authenticated source gameplay; the project’s already separately audited native PRG26/0D OAM assembler has **not** been integrated into this new app. VRC6/APU audio, proper player physics, animation/AI, menus, branching, passwords, boss and stage progression are not implemented. The Windows build is source-supported; verify independent CI before claiming packaged Windows compatibility.

**No new strict semantic PRG bytes; strict 49,504/262,144 (18.8843%); VPP26/100; completed semantic checkpoint 0508; fixed PRG31 frontier FB96 unchanged.** This is a native UX and integration stepping stone, not a completed gameplay checkpoint.

## Next source-domain work

Replace preview sprites with the existing source-verified bank-$0D OAM pipeline, derive background/scroll from authentic JP VRC6 CHR and nametable streams, and lift player collision/movement source events with independent Mesen frame goldens. Keep private screenshot art outside Git.
