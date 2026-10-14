# Enhanced-only port: extensible menus, moddable game systems and future editor

**Universal parent policy:** [MOD_FORWARD_METHODOLOGY.md](../../MOD_FORWARD_METHODOLOGY.md) governs all DOS/NES/SNES/SMS/Genesis and future game ports. This document is the **JP game-specific implementation profile and roadmap**; it supplies examples and constraints, not exceptions to the shared policy.

**Status:** project direction / architecture contract, **not an implemented mod SDK, editor, menu registry or loader**. Adopted after JP0619. The sole player-facing edition is Enhanced, with original Japanese *Akumajou Densetsu* gameplay as its **default behavioral baseline**. Intentional fixes or improvements are allowed, but changes to movement, physics, enemy timing, hitboxes, level behavior or progression need explicit tests and changelog entries.

## 1. Expandable Start/Pause menu

The future menu must be an expandable registry rather than one hard-coded screen or hard-coded item count. A menu page has a namespaced stable ID, ordering/group metadata, optional child pages, visible/enabled predicates, localized display labels, navigation callbacks and an action handler. Menu rendering and controller navigation must not depend on the number or names of pages.

**Initial player-facing menu plan, order not final:**

| Stable action ID | Display text | Action |
|---|---|---|
| `core.save_state` | Save State | Open slot selector, save only after validation |
| `core.load_state` | Load State | Open slot selector, load only after validation |
| `core.audio` | Audio | Open adjustable three-row volume page |
| `core.quit` | Quit | Confirmation, orderly save/exit |

Keep distinct **entry points** for a future title-screen menu and an in-game Start/Pause menu; both can reference the same action registry but require different state permissions (e.g. a title-screen Load State can exist, while Save State may require active gameplay). Trigger, placement and title wording remain design choices, not committed behaviors.

Submenus may register later for Controls, Display/Video, Mods, Accessibility, Debug/Developer, Gameplay Tweaks, and user-contributed categories. They must not require editing a monolithic switch statement. Mod-owned IDs use a namespace such as `author.package.action`, never reuse protected `core.*` IDs.

Input contract: when the menu owns input, Up/Down navigates; Left/Right changes sliders **1 unit per press**; Accept/Back enter/leave pages. All gameplay buttons must be suppressed during modal UI, including a closing-menu release barrier. Pause must stop game simulation frames rather than merely hide or suppress output, and audio pause/resume must avoid leaked/queued effects. Save/Load must use the existing native state interface and respect restrictions; loading must reinitialize presentation-only state. The exact shortcut to open the Start/Pause menu remains configurable.

Audio page: Master, Music, Sound Effects 0–100 in **1%** increments, default 100, persistent. Use the **authentic original health-bar CHR tiles** ($1093 full/$1085 outline) and **in-game pixel font** (digits $1041–$104A, capitals $1050–$1069) identified at JP0619; original pixels should remain swappable through the asset registry. JP0618 Master is effective; Music/SFX preferences are stored but **must not be advertised as working attenuation until separate source-owned audio buses exist**.

The pinned external host exposes `CycHostExtras.menu_items`, `menu_callbacks` and persistent `[Game]` config hooks. These are existing host extension points, **not** proof that our custom original-art menu or a mod registry is already integrated. Avoid replacing the host ABI or patching upstream code without a bounded, pinned-source test.

## 2. Modder-friendly architecture applies to the entire game

A **vanilla/default content pack** must reproduce the original game. Game-specific content or presentation should be **data-driven and addressable by stable symbolic resource IDs**, not assumed to exist at immutable ROM or native-code offsets. Suggested boundaries, to implement progressively:

| Domain | Replaceable inputs | Contract boundary |
|---|---|---|
| Graphics/UI | CHR-derived tiles, palettes, sprite sets, fonts, HUD layout, menus | Data-only renderer assets; don't require PPU/CPU changes for a skin |
| Audio | Songs, instruments, sound effects, sound banks, independent gains | Separate Music/SFX event/voice buses; no inferred sound ownership |
| Levels | Tile layers, collisions, placements, scrolling/camera, exits, checkpoints | Versioned level schema, validated references, no hidden absolute offsets |
| Actors | Enemy/item/NPC definitions, hitboxes, animation, AI tables | Declarative parameters where feasible; advanced behavior through explicit bounded hooks |
| Player/gameplay | Movement parameters, equipment, abilities, damage, difficulty | Default values match original, overrideable only via explicit changes |
| Text | Strings, translations, descriptions, dialogue, labels | Font mappings, glyph fallback, text resources separate from fixed menu geometry |
| Options/input | Bindings, accessibility, saves, menu pages | Stable setting keys, callbacks, validation, migration |
| Progression | Stage graph, branching, triggers, secrets, save metadata | Stable stage/event IDs and carefully versioned save-state compatibility |

Avoid monolithic globals, magic indexes, duplicated asset definitions, and special cases tied to one new feature. Put storage, serialization, validation, simulation behavior, and rendering in distinct modules. An enhancement should be removable/disabled without rewiring unrelated core gameplay.

### Default pack, overrides and compatibility

This section is a **target format**, not a parser already in the repository.

- Each mod has a manifest with a **stable namespaced ID**, human name, author, format/API version, supported port version, declared dependencies and conflicts, optional load ordering, and declared resource replacements/additions.
- Override resolution must be deterministic: base/default pack first, declared dependencies next, user order where unambiguous. Conflicting replacements generate clear diagnostics rather than silent accidental overwrite.
- Resources are referenced by symbolic IDs (for example `base.hud.health_meter.full`, `base.font.digit.7`, `base.level.stage_01`), not hardcoded CHR addresses in the eventual public mod API. Keep ROM physical IDs available only as provenance metadata.
- Unknown versions, missing assets, out-of-bounds values and incompatible dependencies fail validation **before gameplay**, with a safe fallback to vanilla content where possible.
- Keep distinct categories: cosmetic mods should not alter mechanics; gameplay mods must explicitly declare rule changes. Mod compatibility and save metadata should record IDs/versions and enough hashes to diagnose an incompatible load.
- No arbitrary native DLL or untrusted script execution through a data-mod loader by default. Any future executable extension API needs explicit capabilities and user opt-in.
- Mod packaging and discovery should avoid redistribution of copyrighted ROM, ripped assets or compiled proprietary game data. User-local original-ROM extraction can generate the private default content pack.

## 3. Editor-first resource formats (future work)

Design content records now so a **level editor / broader game editor** can be added later as a frontend to the same schemas the game runtime reads. Do not build a second, incompatible internal format for the editor.

A level format should include stable stage ID, tile/layer references, metatiles, collision maps, camera and scrolling rules, actor/item placements, trigger/exit graph, checkpoint definitions, stage music cues, and explicit version. Validate tile/object bounds, references, overlapping critical triggers, unreachable exits where safely detectable, and compatibility with the runtime coordinate system. Use human-readable files for authoring and optionally deterministic compiled/cached binary blobs for performance.

The editor should eventually support **import → edit → export → reimport** lossless round-trips for supported fields, undo/redo, diff/validation, preview through the actual engine, content packs and mod layering. Avoid editor-only behaviors that the shipping engine cannot reproduce. Debug overlays and provenance mapping back to source ROM can coexist with freely editable enhanced content.

## 4. Incremental implementation policy

The architecture is a target, **not a claim that every subsystem is already moddable**. Keep each phase bounded and testable:

1. JP0620 menu lifecycle/input isolation and an **action/page registration boundary**; no hardcoded limit of the four initial actions. Player-facing UI stays original-art and input-safe.
2. Separate reusable renderer, font/health-bar resource aliases and audio settings model. Keep authentic JP619 art as default data, not buried inside menu logic.
3. Add a minimal versioned **data-only mod manifest/resource resolver**, with deterministic load order and ROM-free contract tests, before exposing more complex content hooks.
4. Convert gameplay subsystems to declarative content progressively, with ROM-backed baseline fixtures and intentional-difference flags. Introduce independent Music/SFX buses before enabling separate volume controls.
5. Design the level/editor schema alongside runtime content loading; implement an editor only when enough editable level entities have a single canonical format.

**Acceptance criteria for future changes:** original gameplay is the default baseline; a new menu page is addable without editing navigation; a cosmetic replacement changes no game-state hashes; malformed content is rejected safely; mod precedence is deterministic; modded save/load is version-aware; original unmodded content remains playable; audio UI's three controls never misrepresent separate channels.

**Current actual state (JP0619 HEAD):** native Enhanced Master PCM gain, persistent Music/SFX values not yet mixed, original-art 3-row developer-only **noninteractive preview**. There is no shipping Start/Pause menu framework, mod loader, external schema, level editor or broad asset/behavior override system yet.

**Progress ledger unaffected by this architecture-only direction:** verified PRG 49,504/262,144 (18.8843%), VPP27/100, certified checkpoint 0508 and fixed frontier $FB96. Do not modify `JP/analysis/RESUME_STATE.json` for a future design note.
