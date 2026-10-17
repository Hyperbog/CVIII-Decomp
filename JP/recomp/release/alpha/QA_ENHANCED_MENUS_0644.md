# Enhanced Windows menu acceptance — JP0644

**Purpose:** final owner QA of the current private Enhanced UI, not a new
feature request. Issue #1 is closed after owner-confirmed graphics resolution;
do **not** reopen it as an artificial prerequisite. No ROM, screenshots,
save states, or proprietary binaries need to be uploaded.

## Setup

- [ ] Preserve the previously working AlphaCandidate as a separate backup.
- [ ] Build a new private Enhanced candidate from the current
      `decompilation` branch using the authenticated original Japanese ROM.
      Verify `CVIII-CHR-Index.dat` exists in the private build. Do not copy
      an old compiled executable over the new one.
- [ ] Confirm a new game starts, Trevor responds normally, audio plays,
      and the scene is visually correct to you. Do not treat this one
      spot-check as complete game parity.

## F4 / Save / Load

- [ ] In Enhanced gameplay press keyboard F4. Confirm gameplay **stops**
      advancing, the original-font Start/Pause page appears, and movement
      inputs do not reach Trevor while the page owns input.
- [ ] Select Save State → slot picker. Navigate slots 0 → 9 → 0 using
      keyboard arrows and gamepad D-pad. B/Escape should cancel to F4
      without writing a file or silently selecting a different host slot.
- [ ] Choose a nonessential test slot, save a state, advance the game,
      then load the same slot; confirm the actual character/room/state
      returns as expected. Do not overwrite the only good save.
- [ ] On a different slot with **no prior state**, choose Load. Confirm
      the pinned host reports failure, the active quick-slot remains
      unchanged, the picker still shows the attempted slot, and
      B/Escape cancels back to F4. Retrying must not crash or unpause.
- [ ] Close F4 with F4/Escape, confirm gameplay resumes normally and
      held input does not stick.

## F6 / Audio / nested focus

- [ ] Press F6 from gameplay. Confirm Original-healthbar-art Audio page
      appears, simulation is paused, and Left/Right changes displayed
      Master in 1% increments. Master 0 should mute the *mixed* audio;
      restoring Master 100 should restore playback.
- [ ] Confirm Music and SFX values can be saved and revisited, but their
      independent audio gains are correctly labeled PENDING.
      **Do not report this as working Music/SFX mixing.**
- [ ] Close standalone F6 with Escape/B/Start; it must return to gameplay.
- [ ] Open F4 → Audio. Move selection, then close Audio with F6 or Escape.
      You must return to the **same selected F4 Audio row**, with no
      transient simulation frame or accidental gameplay attack.
      Close F4 separately to resume.
- [ ] Attempt F4 while nested Audio is open; it must not silently
      destroy the hidden F4 parent. Test gamepad B/Start on each page.
- [ ] Select Quit once and cancel: the game must remain running.
      Quit requires a second deliberate acceptance; test actual exit
      only after safeguarding the current game.

## Signoff

Record the local candidate build SHA/version, Windows build result,
controller model, which keyboard/gamepad checks passed, and the first
specific failing action (if any). Screenshots or recordings are
optional. Owner acceptance of these menu interactions is separate
from 6502 semantic coverage and original-Mesen parity.
