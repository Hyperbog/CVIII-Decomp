# JP0846 — Detached actor B447 gameplay input integration

JP0845 renders only source-proven, previously genuine detached type3D
actors in the Enhanced side margins. JP0846 connects the original
bank0B:$B447 partner collision-input calculation to that private
per-frame movement, after source and camera authentication.

For real original partner slots 20, 21 and 22 it records proximity,
original B447 partner masks, and explicitly unsupported special-branch
states. The source must match its original CPU record and parent slot,
have a genuine adjacent-page OAM-cull detachment witness, remain outside
the original 256px viewport, and not conflict with a reused original
guest type3D allocator slot. All original positions are read-only.

The per-source snapshots live in the private Enhanced world, not guest
RAM. Scene/savestate resets clear them. All computed 'near' results are
**collision inputs, not damage authorization**. Original B486/B525
completion, bank0C:$8850 sound, independent AI, death, score and drops
are not implemented; guessed gameplay side effects remain prohibited.
The native CPU/PPU/mapper and Original edition are untouched.

ROM-free GCC and Clang ASan/UBSan tests cover source linkage,
masking, unsupported branches, room/viewport exclusion, original-slot
priority and isolated state reset. No new Mesen capture is required.
