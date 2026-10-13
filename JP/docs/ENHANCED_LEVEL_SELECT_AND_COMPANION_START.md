# Enhanced game-start, level select and companion-role inversion

Status: approved product direction / design backlog, **not** a claim that
the gameplay variants below work yet. Written from the owner's JP0595
requirements.

## Player-facing modes

**Original edition** retains the original Japanese password system,
character progression, stage route selection, partners, original cutscenes
and ordinary gameplay. Debug tools are developer-only and must not alter
reference gameplay when closed. Original/Enhanced must remain selectable.

**Enhanced edition**, optionally, exposes:
- Level select: 18 original JP password checkpoints and, once validated,
  direct-stage initialization without prerecording save states
- Companion select: None, Alucard, Sypha, Grant, while also retaining
  the ordinary game path of unlocking the companions
- Difficulty select: the original Normal/Hard flags, with future
  optional difficulty enhancements explicitly separated
- Clipboard password copy and paste: original 4x4 symbols, strict
  decode/verification and support for the game's ordinary password UI
- Optional starting-character mode: start the campaign as Alucard,
  Sypha or Grant, with Trevor as that route's eventual recruit

Preserve **password play** even when level select is enabled. Passwords
are a core original gameplay feature, not a legacy feature to remove.

## Starting as a companion — future gameplay module

When the player elects to start as one of the companions:
1. Spawn and control the selected companion from the beginning.
   Their intended movement, attack, collision, health and palette
   behavior must be tested in the previously Trevor-only segments.
2. At the route event that would normally unlock that companion,
   place Trevor at that encounter location as the recruitable character.
3. Re-stage the **intro animation only**: the currently controlled
   companion enters from the side of the scene, Trevor stands at the
   encounter location, and the original exchange/dialogue continues,
   with minimal role-consistent text/script adjustments if needed.
   Do not remove the scene or replace the dialogue with a text popup.
4. Allow the normal recruit and character-switch flow to continue.
   Preserve the route conditions and subsequent scenes, bosses and endings
   unless a separately specified change requires an explicit opt-in.

This is a **new Enhanced gameplay mode**, not a reference-ROM bug fix.
It requires script/camera/actor state reconstruction, player actor
generalization, save-version flags, scene-specific assets/animations,
and separate full-route playtests. Handle branch-exclusive characters
and encounter locations explicitly; do not assume each character can
be met on every route. Original mode remains unchanged.

## Debug tools and staging priorities

1. **Already present:** F10 in-game menu loads and captures full-machine
   checkpoints for stage+partner; no unvisited stage initialization.
2. **JP0595 implemented:** external selector accepts copied password
   grids and validates their checksum, name and route. F10 Ctrl+V
   decodes a password into a **checkpoint selection** and the existing
   Enter command can load its captured state. F10 cannot directly use
   that grid as an unsaved stage/companion initializer.
3. **Next highest-priority task:** validate the actual Japanese game
   password handler's input and stage-init transition against independent
   Mesen. Provide F10 direct stage selection and real password paste
   through that original gameplay pathway; do not arbitrarily poke
   stage IDs, mapper registers or a partial CPU state.
4. Once direct warp is proved, make Level/Companion/Difficulty a normal,
   nondebug **Enhanced** New Game option, alongside Password / Continue.
5. Implement companion-only start and Trevor unlock cutscene
   substitution as a separately opt-in mode after safe stage/state loading.

## Evidence gates

Use original JP ROM mapper24, route labels and password tables.
Confirm password name hash, player/partner/difficulty fields, stage
loader and valid route branch. Test game UI loading in private retail
Windows build, verify independent reference emulator startup frame,
full machine checkpoints, original edition no-change hashes, and
Original/Enhanced save-state compatibility. Synthetic CI proves
compilation and interface contracts only, not real retail acceptance.

Strict semantic PRG 49,504/262,144 and VPP 27/100; historical
checkpoint 0508 and PRG31 FB96 frontier unchanged by this design.
