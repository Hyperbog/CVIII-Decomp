# Universal Mod-Forward Development Methodology

> **Repository-wide engineering policy, reusable across game-port projects.**
> Applies to DOS, NES/Famicom, SNES/Super Famicom, Sega Master System/Game Gear,
> Genesis/Mega Drive, and future platforms. Applies to native ports, decompilation,
> recompilation, asset pipelines, interfaces, tests, save systems, and future editors.
>
> **Status:** Normative methodology for all new work. This document is **not**
> an announcement that a mod loader, SDK, editor, or any individual override
> mechanism has already shipped. Each project reports actual support separately.

## Mission

**Make a port play like its original game by default, while making its systems
easy to inspect, replace, extend, configure, and edit.**

The original game is the *behavioral reference*, not a prohibition on enhancements.
Fixes, improved audiovisual output, new menus, accessibility, and gameplay additions
are welcome when intentional and testable. A faithful default installation must
remain distinguishable from a modded or enhanced variant.

**Every change should answer:** *How could a modder change this later without
patching unrelated source code?* If the answer is "edit a hardcoded constant,
replace a switch statement, or manipulate a raw ROM address," identify a better
extension seam before making the change.

The same philosophy works regardless of CPU, cartridge format, graphics hardware,
operating system, or game engine. **Platform knowledge belongs in adapters and
project profiles, not in the shared mod format or core policy.**

## 1. Non-negotiable engineering principles

1. **Default fidelity.** The vanilla content/rules reproduce the target original
   game as closely as the port's independently verified evidence permits.
   Intentional behavior changes are named, documented, isolated, and regression
   tested. Never silently redefine movement, hitboxes, speed, AI, level layout,
   progression, input timing, or sound-event semantics.
2. **Data before hardcoding.** Put tunable values, resource mappings, menu
   definitions, text, stage objects, sound assignments, and related content in
   validated data where practical. Keep engines generic; avoid special cases for
   one level, sprite, mod, or menu row.
3. **Separate responsibilities.** Distinguish immutable historical evidence,
   canonical default content, schema validation, resource lookup, gameplay
   simulation, presentation, persistence, editor tooling, and debugging.
4. **Stable IDs, not addresses.** Public mod references use namespaced,
   human-readable symbolic IDs. Physical bank/offset, file position, CPU address,
   VRAM tile index, DOS segment, or source-code enum may be recorded as provenance
   but is **not** the long-term public mod API.
5. **Explicit extension points.** A subsystem exposes a small registry, resolver,
   event hook, or documented data interface for intended customization. Do not
   require a mod to monkey-patch another subsystem or use undefined memory layout.
6. **Replace as well as add.** Wherever reasonable, permit both swapping an
   existing resource and registering a new one. Treat fallback, precedence,
   duplicate IDs, removal, and missing references as first-class cases.
7. **Determinism and observability.** The same base version, active mod set,
   configuration, inputs, and random seed should resolve the same content and
   game-state results. Explain why a resource won an override and where it came from.
8. **Validate before use.** Reject malformed, out-of-range, incompatible,
   circular, or dangerous content with a precise diagnostic. Do not rely on
   trusted artwork, well-behaved archive metadata, or unverified script inputs.
9. **Keep old evidence immutable.** Never alter commercial originals, golden
   traces, or reference fixtures to make a mod or enhancement appear correct.
   Preserve real-source confidence grades and certification accounting.
10. **Editors and automation use runtime contracts.** A future level editor,
    sprite editor, sound editor, or mod pack builder should author the **same
    schemas and resource IDs the game loads**, not a parallel private format.
11. **Document what actually works.** Distinguish **implemented**, **tested**,
    **experimental**, **proposed**, and **unsupported**. A settings slider that
    persists a value is not a functioning separate audio bus until it controls one.

## 2. The standard architectural boundary

Design new work in layers. A project may combine layers into small modules when
appropriate, but must preserve their contracts.

| Layer | Owns | Must not assume |
|---|---|---|
| Historical/reference | ROM/disk identity, disassembly, evidence, original traces | That speculative code patterns are live or that source data is freely redistributable |
| Platform adapter | CPU/mapper or memory map, cartridge/disk decoding, tile/palette/audio conversion, original input/timing model | A specific game owns every hardware detail |
| Default-content importer | Reproducibly builds authentic local content from authorized originals | That users may redistribute original media or extracted licensed assets |
| Canonical content model | Stable resource IDs, typed records, schemas, defaults | Physical source offsets, hardwired renderer limits |
| Mod resolver | Dependency graph, namespaces, overrides, provenance, validation | Filesystem enumeration order or silent last-wins conflicts |
| Game simulation | Rules, world state, actors, physics, deterministic events | UI screens, mod archive paths, renderer tile IDs |
| Presentation/audio | Graphics, font, HUD, camera, voice/audio buses, menus, accessibility | Mutating gameplay state merely to display a mod |
| Save/settings | Versioned config, game saves, compatible mod-set identity and migrations | Raw pointer layouts surviving binary or mod changes |
| Editors/tools | Import/inspect/edit/validate/export/preview the canonical model | A separate incompatible editor-only representation |

**Rule:** Source-specific decoding happens at the platform/import boundary.
Mods and editors operate on canonical data. Runtime systems consume resolved
content through stable interfaces.

## 3. IDs, assets and configurable content

Use opaque stable IDs such as **base.player.alucard**, **base.stage.01**,
**base.ui.health_meter.full**, **base.audio.event.jump**, or
**publisher.pack.enemy.new_type**. These are examples, not required names.

- IDs are independent of filenames, load order, original hardware numbers,
  and on-disk storage paths. IDs must not be reassigned to different meanings.
- Asset records have explicit types, dimensions, bounds, dependencies,
  version/schema and fallback behavior; public tools can query these.
- Where possible, replace a sprite sheet, palette, font, sound, object,
  animation or menu layout by changing a resource binding, **not** by modifying
  gameplay source.
- Preserve source-to-canonical mappings as separate provenance metadata.
  Platform-specific asset importer changes must not rewrite the public mod ID
  space without migration.
- Expose extension points where behavior genuinely belongs: actor/state
  definitions, validated parameters, animation graphs, stage scripts,
  game events, and menus. Do not promise arbitrary engine-code modification
  from a data-only manifest.

**Prefer reversible changes:** the base content must continue to load without
any mod installed. Cosmetic replacements should not change the deterministic
game-state hash or collision data unless they explicitly declare doing so.

## 4. Portable mod package and load-order contract

Each project should eventually implement a **versioned, data-first package
format** with at least:

- Stable mod ID and readable name; author, license, package version and
  schema/API version.
- Supported game/port ID, build/feature constraints, optional platform
  requirements, dependencies and conflicts.
- A declaration of whether it changes **cosmetics**, **audio/UI**,
  **gameplay/content**, **scripts/code**, or **save compatibility**.
- Resources to add, replace, remove (where safe), or patch with explicit
  canonical types and IDs; integrity hashes for distributable files.
- Optional ordering constraints and documented configuration defaults.

**Resolution must be repeatable:** start with the vanilla/default pack,
resolve dependency ordering, validate incompatible versions and conflicts,
then apply approved explicit overrides. Never let directory iteration order
decide what wins. An unresolved conflict or dependency cycle must produce
a clear error, not accidentally select a random asset.

Maintain a human-readable **resolved-mod manifest or lockfile** for
troubleshooting and reproducible bug reports (IDs, versions, relevant content
hashes and order). Mod priorities and pack format are project design choices
until a tested loader exists; do not falsely label a proposed schema as a
released public compatibility contract.

## 5. Systems to keep moddable

| System | Mod-forward design obligation |
|---|---|
| Graphics and HUD | Replaceable sprites, textures/tiles, tilemaps, fonts, palettes, layers, animation definitions and layout constraints |
| Audio | Typed music and SFX events; independently controlled buses/voices when implemented; replaceable samples/music mappings and mixing configuration |
| Levels and maps | Authored stage/world graph, rooms, tile layers, collisions, entities, exits, checkpoints, camera/scrolling, scripted triggers |
| Characters, enemies and items | Identifiable archetypes, parameters, animation, hitboxes, behavior bindings, drops and interactions |
| Combat and physics | Original defaults, bounded named parameters, intentional override flags and deterministic behavior tests |
| UI and menus | Page/action registry, namespaced entries, configurable binding/order, modal input ownership, persistent settings |
| Input and accessibility | Bindings and assistance as explicit policies, not hardwired platform-key assumptions |
| Text and localization | String IDs, language tables, fallback glyph mappings, text layout constraints |
| Progression and saves | Stable stage/event IDs, versioned saves, mod identity and graceful incompatibility reporting |
| Scripting/hooks | Explicit capabilities and sandboxing/trust policy; safe callbacks, no silent arbitrary code execution |

**Menus are content and behavior, not a fixed four-item list.** Projects may
start with Save State, Load State, Audio, Quit, and add pages for controls,
display, mods, accessibility or debugging. The page registry must not need
a new hardcoded branch to accept a new entry. Pause and modal UI must isolate
gameplay inputs and prevent simulation advances while the menu owns control.

## 6. Platform adapters, not platform-locked methodology

| Platform family | Typical reference-specific responsibilities |
|---|---|
| NES/Famicom | 6502 CPU, mapper/banks, PPU/CHR/nametable/palettes, APU/expansion sound, cycle/frame semantics |
| Sega Master System/Game Gear | Z80 CPU, memory paging, VDP tile/sprite/palette model, PSG/FM variants |
| SNES/Super Famicom | 65C816 and companion chips, VRAM/OAM/CGRAM, PPU layers/modes, SPC700/DSP audio, cartridge mappings |
| Genesis/Mega Drive | 68000/Z80, mapper where relevant, VDP plane/sprite/palette rules, YM2612/PSG sound, timing |
| DOS PC games | Original CPU/ABI/compiler and executable format, memory segments/overlays, VGA/EGA/Mode X, input/timers, AdLib/OPL/MT-32/Sound Blaster and host OS semantics |
| Future systems | Provide a new importer/adapter and evidence profile; reuse the content/mod/editor contracts where meaningful |

These are **examples of adapter duties, not exhaustive hardware specifications**.
Never assume every game on a platform shares a mapper, sound chip, palette,
timer, renderer or executable architecture. Any original-to-native parity
proof remains platform/game/scenario specific. A universal mod policy does
not license claiming universal emulator or sound parity.

## 7. Safe extension and distribution

- Data-only packages are the default. **No automatic arbitrary DLL,
  executable, native plug-in or unrestricted script execution** from a
  mod archive. Any future code extension needs user opt-in, capability
  boundaries, versioned API, and explicit trust/review policy.
- Canonicalize paths and reject traversal/absolute-path escapes, archive
  bombs, unexpected symlinks, duplicate case-colliding filenames, excessive
  counts/sizes and untrusted network references.
- Validate every object/array/string/asset size and cross-reference; reject
  invalid collision, tile, sample, actor and stage inputs before they reach
  emulated or native engine memory.
- Keep original copyrighted ROMs, commercial disk images, music rips and
  proprietary asset packs out of public Git history and CI artifacts.
  Public default-content extraction recipes can use the owner's legally
  obtained local media; mod creators remain responsible for rights to
  distributed content.
- Never let a mod redefine protected engine IDs, alter authenticity hashes,
  silently weaken validation, or rewrite historical evidence.

## 8. Save files, versioning and long-term editor compatibility

Maintain separate version numbers for the **engine/API**, **content schema**,
**mod package format**, and **save format**. Semantic migrations should be
explicit and testable; avoid coupling save files to raw C structs, pointers,
cartridge RAM addresses or object array positions.

A save that depends on active mods should report the relevant mod IDs and
versions/hashes, and should not silently load incompatible stages/actors.
A clean vanilla save must remain a normal supported case.

A future level editor and general editor must work with the runtime's
versioned canonical formats. Required design properties: stable identity,
portable import/export, round-trip preservation of supported fields,
validation, deterministic builds, undo/redo, dependency inspection and
preview by the real runtime when available. Editor UI may arrive later;
**do not block it today by burying level definitions in uneditable control
flow or single-purpose binaries**.

## 9. Tests required when adding a mod-facing seam

A new extensible feature SHOULD ship with a small ROM-/disk-free fixture.
Where original media is needed, separately perform an owner-local authenticated
check and explicitly label any unperformed native/integration checks.

**Minimum review questions:**

- Does the **no-mod baseline** produce the same relevant original behavior?
- Can a replacement use a symbolic ID and data rather than patching C,
  assembly, hardware addresses or other mod source?
- Can two independent packages load in deterministic order? Is conflict
  resolution diagnosable?
- Are missing IDs, dependency cycles, malformed data, hostile sizes, wrong
  schema versions and unsupported formats rejected?
- Can a mod be disabled without leaving stale state? Are cached resources
  invalidated safely?
- Are save/load, content-version migration, settings persistence and
  controller/input isolation covered where applicable?
- Is cosmetic-only replacement mechanically inert? Do gameplay mods clearly
  declare intentional mechanical changes?
- Can future editors import/export the resource without information loss?
- Is the difference between **implemented**, **tested**, **proposed**, and
  **unverified** explicit in docs and release notes?

Where practical, provide one **vanilla fixture**, one **replacement fixture**,
one **additive fixture**, and one **rejected malformed fixture**. A passing
mod resolver does not prove original-to-native gameplay parity.

## 10. How contributors and agents should work

For each feature/change, briefly record:

1. **Target subsystem and default behavior.** What original behavior must
   remain unchanged? What is the intended enhancement?
2. **Extension seam.** Which canonical resource ID, data structure,
   registry/API or adapter boundary lets a modder alter the result?
3. **Replacement and additive cases.** What can a mod swap? Can it add
   another item/page/entity? How are limits and missing references handled?
4. **Schema and compatibility.** What is versioned? What saves/config
   need migration? What priority or conflict rules apply?
5. **Security and provenance.** Where do source bytes/assets originate?
   Which untrusted inputs get validated?
6. **Tests and limitations.** Name actual unit/integration/original-reference
   gates, explicitly mark tests not run, and distinguish baseline behavior
   from intentional differences.

**If a feature cannot reasonably be made fully moddable now**, preserve a
small replaceable interface, avoid cementing physical addresses and magic
constants into callers, document the missing seam, and implement the
verified smallest step. Do not add speculative machinery just to label a
component "mod-compatible."

## 11. Adoption across repositories

**This document is deliberately game- and platform-neutral.** Copy it
unchanged or reference its canonical version in each DOS, NES, SNES, SMS,
Genesis or future project. Each project should also maintain a short
**project-specific modding profile** stating:

- Game/region/build target and what "vanilla faithful" means for that game.
- Current runtime/platform adapter(s) and authorized source-media imports.
- Current resource namespaces, manifest/schema versions and override support.
- Save compatibility policy; available menus, UI hooks and audio buses.
- Tests that actually run, outstanding reference/parity gaps and next
  implementation milestones.

Project-level guidance may **specialize** platform details but must not
quietly weaken authenticity, isolation, deterministic resolution,
security, user rights or the requirement to label unfinished capabilities.

This shared policy deliberately does **not** prescribe the exact address mapping,
renderer, mixer, input driver, executable format, editor UI, or release model for
any particular game. Those belong in the project-specific modding profile, with
links to the actual code and tests.

**This methodology is not a semantic decompilation checkpoint or a parity
certificate.** Original evidence and implementation progress remain
independently audited.
