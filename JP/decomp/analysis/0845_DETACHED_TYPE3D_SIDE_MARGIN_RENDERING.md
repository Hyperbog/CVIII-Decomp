# JP0845 — Detached type-$3D side-margin presentation

## Verified prerequisite

The existing JP0828 Stage1-02 private 6502 movement executor retains
independent 2 KiB actor RAM after a genuinely linked source actor loses its
original CPU slot. This implementation does NOT run independent enemy AI,
animation, collision effects or defeat scripts.

## Implemented integration

The existing PRG26 sprite compositor now projects one or both **already
detached** type-$3D instances into the 426px Enhanced Stage 1 side margins.
It accepts only exact Stage1-02 room key (0,1,0), placed world geometry,
prior actual guest allocation, an independently moved private instance,
matching physical source CPU identity and original parent slot, an
original adjacent-page/OAM-cull witness, and a still-unverified/released
original source. An active guest type3D in the original slot takes
precedence. Guest gameplay/PPU/OAM memory and the central NES framebuffer
are never written.

Pixels are decoded from the same private SHA-authenticated original
PRG26/27 sprite descriptors and live CHR/PPU palette callbacks as the
existing guest side-margin sprites. Position is the private movement
state. Original frame, selector, mirror and palette are held at the last
observed authentic CPU actor snapshot; NO new animation sequence is
inferred. A virtual actor moving into the original 256px gameplay strip
is suppressed rather than creating an uninteractive fake enemy inside
the NES gameplay window.

This is an **incremental side-only visual integration**, not fully
interactive offscreen enemy gameplay. Collision, damage, drop, audio,
despawn/respawn and true offscreen AI parity remain unsupported. Gameplay
authority stays in the original compiled 6502/VRC6 runtime.

## Verification

A newly compiled ROM-free GCC compositor fixture exercises actual
descriptor painting, frozen detached actor frame, left-margin projection,
the central-picture exclusion, private-to-guest RAM isolation, guest
priority, source mismatch, unlinked candidate rejection and room gating.
The existing JP native regression workflow checks it without MesenCE or
copyrighted ROM data. The private Windows executable must still be built
before any direct playable-rendering claim.
