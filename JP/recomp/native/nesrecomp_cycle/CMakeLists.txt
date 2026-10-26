cmake_minimum_required(VERSION 3.20)
project(JP_Akumajou_Densetsu_Cycle C)
# NESRecomp is an external, separately licensed PolyForm Noncommercial
# dependency. DO NOT vendor its sources or game-derived generated C files.
set(JP_ORIGINAL_JP_ROM "" CACHE FILEPATH "Privately supplied verified original Japanese ROM")
set(NESRECOMP_EXTERNAL_ROOT "" CACHE PATH "External checkout of mstan/nesrecomp")
option(JP_CYCLE_HEADLESS "Build a headless C11 cycle runtime" ON)
option(JP_CYCLE_SYNTHETIC_MEDIA "Allow only the exact synthetic CI fixture" OFF)
# JP0590: compare LLE and experimental HLE PPU render backends on the
# same deterministic input route. Original default remains LLE.
set(JP_PPU_IMPLEMENTATION "LLE" CACHE STRING "NESRecomp PPU backend: LLE or HLE")
set_property(CACHE JP_PPU_IMPLEMENTATION PROPERTY STRINGS LLE HLE)
if(NOT JP_PPU_IMPLEMENTATION STREQUAL "LLE" AND
   NOT JP_PPU_IMPLEMENTATION STREQUAL "HLE")
 message(FATAL_ERROR "JP_PPU_IMPLEMENTATION must be LLE or HLE")
endif()
set(NESRECOMP_PPU_IMPL "${JP_PPU_IMPLEMENTATION}" CACHE STRING
 "External NESRecomp compile-time PPU backend" FORCE)
if(NOT EXISTS "${JP_ORIGINAL_JP_ROM}")
 message(FATAL_ERROR "JP_ORIGINAL_JP_ROM must name the privately owned original ROM")
endif()
if(NOT EXISTS "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/project.cmake")
 message(FATAL_ERROR "NESRECOMP_EXTERNAL_ROOT must contain runner/cyc/project.cmake")
endif()
find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
set(JP_ROM_VALIDATION_EXTRA "")
if(JP_CYCLE_SYNTHETIC_MEDIA)
 list(APPEND JP_ROM_VALIDATION_EXTRA --allow-synthetic)
endif()
execute_process(
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/../../tools/validate_cycle_media_0576.py"
   --rom "${JP_ORIGINAL_JP_ROM}" ${JP_ROM_VALIDATION_EXTRA}
 RESULT_VARIABLE JP_ROM_CHECK
 OUTPUT_VARIABLE JP_ROM_CHECK_OUT
 ERROR_VARIABLE JP_ROM_CHECK_ERR)
if(NOT JP_ROM_CHECK EQUAL 0)
 message(FATAL_ERROR "Unrecognized original-JP ROM: ${JP_ROM_CHECK_ERR}")
endif()
set(NESRECOMP_HEADLESS ${JP_CYCLE_HEADLESS} CACHE BOOL "Disable external SDL/UI when headless" FORCE)
include("${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/project.cmake")
set(JP_CYCLE_OPTIONS "")
if(JP_CYCLE_HEADLESS)
 list(APPEND JP_CYCLE_OPTIONS HEADLESS)
endif()
# JP0589 native C11 edition extension, no external source vendored.
# The original PPU engine continues to drive all CPU-visible NES state.
option(JP_EDITION_HOST_EXTRAS "Add Original/Enhanced native presentation extension" ON)
set(JP_HOST_SOURCES "")
if(JP_EDITION_HOST_EXTRAS)
 list(APPEND JP_HOST_SOURCES HOST_EXTRAS
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_edition.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_lighting.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_index_0598.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_audit_0599.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_fetch_0600.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_frame_evidence_0601.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_nt_trace_0606.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_layers_0608.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_0609.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_bus_0610.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_requests_0612.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_decisions_0646.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_dma_trace_0650.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_source_0648.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dpcm_decode_0649.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_lookup_0653.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_delta_0655.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_control_0656.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_catalog_0657.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_coordinate_0657.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_ppu_stream_0658.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_state0_0658.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_stream_0659.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_session_0614.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_virtual_audio_0647.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_ui_0619.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_registry_0620.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_menu_state_0622.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_menu_0623.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_ui_0623.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_slot_picker_0625.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_stack_0626.c")
endif()
nesrecomp_add_cycle_game(jp_akumajou_densetsu
 ROM "${JP_ORIGINAL_JP_ROM}" ${JP_CYCLE_OPTIONS} ${JP_HOST_SOURCES})
if(JP_EDITION_HOST_EXTRAS)
 target_include_directories(jp_akumajou_densetsu PRIVATE
  "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced")
endif()
# The lighting math is presentation-only and uses libm on POSIX targets.
if(JP_EDITION_HOST_EXTRAS AND NOT WIN32)
 target_link_libraries(jp_akumajou_densetsu PRIVATE m)
endif()
# JP0591: multi-slot save states using upstream's *full machine* serializer.
# Generate a local overlay alongside pinned external cyc_sdl.c; relative
# ../../common/* includes remain correct, and the upstream file is untouched.
# On headless builds the original CLI --save-state/--load-state is unchanged.
option(JP_SAVE_STATE_SLOTS "Ten window quick-save slots, Ctrl+0..9, F8/F9" ON)
if(NOT JP_CYCLE_HEADLESS AND JP_SAVE_STATE_SLOTS)
 set(JP_UPSTREAM_SDL "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc_sdl.c")
 set(JP_SLOTS_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_slots.c")
 if(NOT EXISTS "${JP_UPSTREAM_SDL}")
  message(FATAL_ERROR "Missing pinned cyc_sdl.c, cannot enable save slots")
 endif()
 execute_process(
  COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_savestates_0591.py"
    --source "${JP_UPSTREAM_SDL}" --out "${JP_SLOTS_OVERLAY}"
  RESULT_VARIABLE JP_STATE_PATCH_RESULT
  OUTPUT_VARIABLE JP_STATE_PATCH_LOG
  ERROR_VARIABLE JP_STATE_PATCH_ERROR)
 if(NOT JP_STATE_PATCH_RESULT EQUAL 0)
  message(FATAL_ERROR "Save-slot overlay failed: ${JP_STATE_PATCH_ERROR}")
 endif()
 # JP0594: layer a game-owned F10 stage/companion checkpoint menu on 0591.
 # This writes another private overlay beside the pinned external SDL file;
 # neither upstream code nor ROM bytes are committed.
 set(JP_DEBUG_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_debug.c")
 execute_process(
  COMMAND "${Python3_EXECUTABLE}"
   "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_stage_menu_0594.py"
   --source "${JP_SLOTS_OVERLAY}" --out "${JP_DEBUG_OVERLAY}"
  RESULT_VARIABLE JP_STAGE_PATCH_RESULT
  ERROR_VARIABLE JP_STAGE_PATCH_ERROR)
 if(NOT JP_STAGE_PATCH_RESULT EQUAL 0)
  message(FATAL_ERROR "Stage debug overlay failed: ${JP_STAGE_PATCH_ERROR}")
 endif()
 # JP0596: stage startup from a single original password-screen checkpoint.
 # Generated code is private and preserves the game's password decoder.
 set(JP_BOOTSTRAP_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_stage_bootstrap.c")
 execute_process(
  COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_stage_bootstrap_0596.py"
    --source "${JP_DEBUG_OVERLAY}" --out "${JP_BOOTSTRAP_OVERLAY}"
  RESULT_VARIABLE JP_BOOTSTRAP_PATCH_RESULT
  ERROR_VARIABLE JP_BOOTSTRAP_PATCH_ERROR)
 if(NOT JP_BOOTSTRAP_PATCH_RESULT EQUAL 0)
  message(FATAL_ERROR "F10 password bootstrap overlay failed: ${JP_BOOTSTRAP_PATCH_ERROR}")
 endif()
 # JP0620: owner-private F6 audio modal layer after stage/password patches.
 # No external SDL source is changed in Git; assets remain owner-local.
 set(JP_FINAL_SDL_OVERLAY "${JP_BOOTSTRAP_OVERLAY}")
 if(JP_EDITION_HOST_EXTRAS)
  set(JP_AUDIO_MENU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_audio_menu.c")
  execute_process(
   COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_audio_menu_0620.py"
    --source "${JP_BOOTSTRAP_OVERLAY}" --out "${JP_AUDIO_MENU_OVERLAY}"
   RESULT_VARIABLE JP_AUDIO_MENU_PATCH_RESULT
   ERROR_VARIABLE JP_AUDIO_MENU_PATCH_ERROR)
  if(NOT JP_AUDIO_MENU_PATCH_RESULT EQUAL 0)
   message(FATAL_ERROR "F6 original-art audio menu overlay failed: ${JP_AUDIO_MENU_PATCH_ERROR}")
  endif()
  # JP0623: final host F4 extensible Start/Pause action layer.
  set(JP_START_MENU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_start_menu.c")
  execute_process(
   COMMAND "${Python3_EXECUTABLE}"
     "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_start_menu_0623.py"
     --source "${JP_AUDIO_MENU_OVERLAY}" --out "${JP_START_MENU_OVERLAY}"
   RESULT_VARIABLE JP_START_MENU_PATCH_RESULT
   ERROR_VARIABLE JP_START_MENU_PATCH_ERROR)
  if(NOT JP_START_MENU_PATCH_RESULT EQUAL 0)
   message(FATAL_ERROR "F4 Start/Pause overlay failed: ${JP_START_MENU_PATCH_ERROR}")
  endif()
  # JP0625: a sixth private layer opens a Save/Load 0..9 slot submenu.
  set(JP_SLOT_MENU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_slot_picker.c")
  execute_process(
   COMMAND "${Python3_EXECUTABLE}"
     "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_slot_picker_0625.py"
     --source "${JP_START_MENU_OVERLAY}" --out "${JP_SLOT_MENU_OVERLAY}"
   RESULT_VARIABLE JP_SLOT_MENU_PATCH_RESULT
   ERROR_VARIABLE JP_SLOT_MENU_PATCH_ERROR)
  if(NOT JP_SLOT_MENU_PATCH_RESULT EQUAL 0)
   message(FATAL_ERROR "Save/Load slot menu overlay failed: ${JP_SLOT_MENU_PATCH_ERROR}")
  endif()
  # JP0626: keep Start/Pause resident behind Audio; F6 standalone unchanged.
  set(JP_AUDIO_RETURN_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_audio_return.c")
  execute_process(
   COMMAND "${Python3_EXECUTABLE}"
     "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_audio_return_0626.py"
     --source "${JP_SLOT_MENU_OVERLAY}" --out "${JP_AUDIO_RETURN_OVERLAY}"
   RESULT_VARIABLE JP_AUDIO_RETURN_PATCH_RESULT
   ERROR_VARIABLE JP_AUDIO_RETURN_PATCH_ERROR)
  if(NOT JP_AUDIO_RETURN_PATCH_RESULT EQUAL 0)
   message(FATAL_ERROR "Nested Audio return SDL patch failed: ${JP_AUDIO_RETURN_PATCH_ERROR}")
  endif()
  # Eighth owner-private SDL layer: Home lighting workbench, sliders and mouse routing.
  set(JP_LIGHTING_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_cyc_sdl_lighting.c")
  execute_process(
   COMMAND "${Python3_EXECUTABLE}"
     "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_lighting_editor.py"
     --source "${JP_AUDIO_RETURN_OVERLAY}" --out "${JP_LIGHTING_OVERLAY}"
   RESULT_VARIABLE JP_LIGHTING_PATCH_RESULT
   ERROR_VARIABLE JP_LIGHTING_PATCH_ERROR)
  if(NOT JP_LIGHTING_PATCH_RESULT EQUAL 0)
   message(FATAL_ERROR "Home lighting workbench SDL overlay failed: ${JP_LIGHTING_PATCH_ERROR}")
  endif()
  set(JP_FINAL_SDL_OVERLAY "${JP_LIGHTING_OVERLAY}")
 endif()
 get_target_property(JP_GAME_SOURCES jp_akumajou_densetsu SOURCES)
 set(JP_PATCHED_SOURCES "")
 set(JP_SDL_REPLACEMENTS 0)
 foreach(JP_FILE IN LISTS JP_GAME_SOURCES)
  if(JP_FILE MATCHES "cyc_sdl\\.c$")
   list(APPEND JP_PATCHED_SOURCES "${JP_FINAL_SDL_OVERLAY}")
   math(EXPR JP_SDL_REPLACEMENTS "${JP_SDL_REPLACEMENTS} + 1")
  else()
   list(APPEND JP_PATCHED_SOURCES "${JP_FILE}")
  endif()
 endforeach()
 if(NOT JP_SDL_REPLACEMENTS EQUAL 1)
  message(FATAL_ERROR
   "Expected exactly one upstream cyc_sdl.c in the target, got ${JP_SDL_REPLACEMENTS}")
 endif()
 set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_PATCHED_SOURCES}")
 message(STATUS "CVIII: quick-saves/F10 password bootstrap; optional F6 paused original-art audio menu")
endif()

# A headless-only executable is NOT a playable alpha. In windowed builds
# NESRecomp may silently skip SDL when its dependency is unavailable.
if(NOT JP_CYCLE_HEADLESS)
 get_target_property(JP_ALPHA_HAS_SDL jp_akumajou_densetsu NESRECOMP_CYC_SDL)
 if(NOT JP_ALPHA_HAS_SDL)
  message(FATAL_ERROR
   "Alpha requires an SDL2 window and controller input. "
   "Install/restore the pinned NESRecomp runner/external/SDL2 SDK; "
   "refusing to mislabel a headless build as playable.")
 endif()
 message(STATUS "Alpha: verified SDL2 video/input/audio target is enabled")
endif()


# ROM-free standalone verification of scrolling lights, room gating and HUD.
add_executable(jp_lighting_test
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_lighting.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_lighting_test.c")
set_property(TARGET jp_lighting_test PROPERTY C_STANDARD 11)
if(NOT WIN32)
 target_link_libraries(jp_lighting_test PRIVATE m)
endif()

# JP0598: isolated host-independent C11 CHR reader gate; synthetic data only.
add_executable(jp_chr_index_test_0598
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_index_0598.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_index_test_0598.c")
set_property(TARGET jp_chr_index_test_0598 PROPERTY C_STANDARD 11)

# JP0599: isolated ROM-free C11 mapper-24 CHR mapping contract.
add_executable(jp_chr_audit_test_0599
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_audit_0599.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_audit_test_0599.c")
set_property(TARGET jp_chr_audit_test_0599 PROPERTY C_STANDARD 11)

# JP0600: private physical PPU pattern-read observer. Stock runtime remains untouched.
set(JP_MAPPER_ORIG "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/hw_mapper.c")
set(JP_MAPPER_TAP "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_mapper_fetch.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
   "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_chr_fetch_0600.py"
   --source "${JP_MAPPER_ORIG}" --out "${JP_MAPPER_TAP}"
 RESULT_VARIABLE JP_MAPPER_TAP_RESULT
 ERROR_VARIABLE JP_MAPPER_TAP_ERROR)
if(NOT JP_MAPPER_TAP_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0600 private CHR observer generation failed: ${JP_MAPPER_TAP_ERROR}")
endif()
get_target_property(JP_FETCH_TARGET_SOURCES jp_akumajou_densetsu SOURCES)
set(JP_FETCH_MODIFIED_SOURCES "")
set(JP_FETCH_REPLACED_COUNT 0)
foreach(JP_FILE IN LISTS JP_FETCH_TARGET_SOURCES)
 if(JP_FILE MATCHES "hw_mapper\\.c$")
  list(APPEND JP_FETCH_MODIFIED_SOURCES "${JP_MAPPER_TAP}")
  math(EXPR JP_FETCH_REPLACED_COUNT "${JP_FETCH_REPLACED_COUNT} + 1")
 else()
  list(APPEND JP_FETCH_MODIFIED_SOURCES "${JP_FILE}")
 endif()
endforeach()
if(NOT JP_FETCH_REPLACED_COUNT EQUAL 1)
 message(FATAL_ERROR "JP0600 requires exactly one hw_mapper.c source, got ${JP_FETCH_REPLACED_COUNT}")
endif()
set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_FETCH_MODIFIED_SOURCES}")
message(STATUS "JP0600 read-only physical PPU CHR pattern tap available")

add_executable(jp_chr_fetch_test_0600
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_fetch_0600.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_fetch_test_0600.c")
set_property(TARGET jp_chr_fetch_test_0600 PROPERTY C_STANDARD 11)

# JP0601: standalone read-only sampled PPU frame evidence (ROM-free).
add_executable(jp_frame_evidence_test_0601
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_frame_evidence_0601.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_frame_evidence_test_0601.c")
set_property(TARGET jp_frame_evidence_test_0601 PROPERTY C_STANDARD 11)

# JP0606: private *actual PPU* nametable and attribute observation.
# The pinned hw_ppu.c remains unchanged and all read values are preserved.
set(JP_NT_PPU_SOURCE "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/hw_ppu.c")
set(JP_NT_PPU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_ppu_nt.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
   "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_ppu_nt_0606.py"
   --source "${JP_NT_PPU_SOURCE}" --out "${JP_NT_PPU_OVERLAY}"
 RESULT_VARIABLE JP_NT_PATCH_RESULT
 ERROR_VARIABLE JP_NT_PATCH_ERROR)
if(NOT JP_NT_PATCH_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0606 PPU nametable observer generation failed: ${JP_NT_PATCH_ERROR}")
endif()
get_target_property(JP_NT_SOURCES jp_akumajou_densetsu SOURCES)
set(JP_NT_PPU_PATCHED "")
set(JP_NT_PPU_REPLACED 0)
foreach(JP_FILE IN LISTS JP_NT_SOURCES)
 if(JP_FILE MATCHES "hw_ppu\\.c$")
  list(APPEND JP_NT_PPU_PATCHED "${JP_NT_PPU_OVERLAY}")
  math(EXPR JP_NT_PPU_REPLACED "${JP_NT_PPU_REPLACED} + 1")
 else()
  list(APPEND JP_NT_PPU_PATCHED "${JP_FILE}")
 endif()
endforeach()
if(NOT JP_NT_PPU_REPLACED EQUAL 1)
 message(FATAL_ERROR "JP0606 requires exactly one original hw_ppu.c source, got ${JP_NT_PPU_REPLACED}")
endif()
set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_NT_PPU_PATCHED}")
message(STATUS "JP0606 read-only PPU nametable/attribute diagnostics installed")

add_executable(jp_nt_trace_test_0606
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_nt_trace_0606.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_nt_trace_test_0606.c")
set_property(TARGET jp_nt_trace_test_0606 PROPERTY C_STANDARD 11)

# JP0608: independent ROM-free sprite priority, transparency and 1-frame
# continuity regression. Experimental host presentation, NOT machine state.
add_executable(jp_sprite_layers_test_0608
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_layers_0608.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_layers_test_0608.c")
set_property(TARGET jp_sprite_layers_test_0608 PROPERTY C_STANDARD 11)

# JP0645: strict C11 64-emission OAM-rotation/animation and ghost-negative gate.
# Opt-in host display only; original PPU frame and gameplay remain untouched.
add_executable(jp_sprite_identity_test_0645
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_layers_0608.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_identity_test_0645.c")
set_property(TARGET jp_sprite_identity_test_0645 PROPERTY C_STANDARD 11)

# JP0609: ROM-free dynamic object/OAM rotation capture unit test.
add_executable(jp_object_oam_test_0609
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_0609.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_test_0609.c")
set_property(TARGET jp_object_oam_test_0609 PROPERTY C_STANDARD 11)

# JP0610: observe actual 2A03 and VRC6 sound-register CPU writes without
# changing any hardware write, music envelope, audio output or NES timing.
# Both overlays remain private in the pinned external runtime checkout.
set(JP_AUDIO_APU_ORIG "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/hw_apu.c")
set(JP_AUDIO_APU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_apu_audio.c")
set(JP_AUDIO_MAPPER_ORIG "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_mapper_fetch.c")
set(JP_AUDIO_MAPPER_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_mapper_fetch_audio.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_audio_bus_0610.py"
  --apu "${JP_AUDIO_APU_ORIG}"
  --mapper "${JP_AUDIO_MAPPER_ORIG}"
  --out-apu "${JP_AUDIO_APU_OVERLAY}"
  --out-mapper "${JP_AUDIO_MAPPER_OVERLAY}"
 RESULT_VARIABLE JP_AUDIO_PATCH_RESULT
 ERROR_VARIABLE JP_AUDIO_PATCH_ERROR)
if(NOT JP_AUDIO_PATCH_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0610 audio register overlay failed: ${JP_AUDIO_PATCH_ERROR}")
endif()
get_target_property(JP_AUDIO_ORIGINAL_SOURCES jp_akumajou_densetsu SOURCES)
set(JP_AUDIO_REWRITTEN_SOURCES "")
set(JP_APU_MATCHES 0)
set(JP_MAPPER_MATCHES 0)
foreach(JP_SOURCE IN LISTS JP_AUDIO_ORIGINAL_SOURCES)
 if(JP_SOURCE MATCHES "hw_apu\\.c$")
  list(APPEND JP_AUDIO_REWRITTEN_SOURCES "${JP_AUDIO_APU_OVERLAY}")
  math(EXPR JP_APU_MATCHES "${JP_APU_MATCHES} + 1")
 elseif(JP_SOURCE MATCHES "cviii_hw_mapper_fetch\\.c$")
  list(APPEND JP_AUDIO_REWRITTEN_SOURCES "${JP_AUDIO_MAPPER_OVERLAY}")
  math(EXPR JP_MAPPER_MATCHES "${JP_MAPPER_MATCHES} + 1")
 else()
  list(APPEND JP_AUDIO_REWRITTEN_SOURCES "${JP_SOURCE}")
 endif()
endforeach()
if(NOT JP_APU_MATCHES EQUAL 1 OR NOT JP_MAPPER_MATCHES EQUAL 1)
 message(FATAL_ERROR "JP0610 requires one 2A03 and one VRC6 mapper source")
endif()
set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_AUDIO_REWRITTEN_SOURCES}")
message(STATUS "JP0610 owner-private 2A03/VRC6 sound-register diagnostic wired")

# JP0650: trace actual DMC DMA sample gets and mapper24 $C000 writes.
# Layer only on the JP0610 private APU/mapper overlays. Never vendor or
# modify pinned external hardware, ROM data or original game audio behavior.
set(JP_DMA_APU_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_apu_dma.c")
set(JP_DMA_MAPPER_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_mapper_dma.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_dmc_dma_trace_0650.py"
  --apu "${JP_AUDIO_APU_OVERLAY}"
  --mapper "${JP_AUDIO_MAPPER_OVERLAY}"
  --out-apu "${JP_DMA_APU_OVERLAY}"
  --out-mapper "${JP_DMA_MAPPER_OVERLAY}"
 RESULT_VARIABLE JP_DMA_TAP_RESULT
 ERROR_VARIABLE JP_DMA_TAP_ERROR)
if(NOT JP_DMA_TAP_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0650 pinned DMC DMA fetch overlay rejected: ${JP_DMA_TAP_ERROR}")
endif()
get_target_property(JP_DMA_OLD_SOURCES jp_akumajou_densetsu SOURCES)
set(JP_DMA_NEW_SOURCES "")
set(JP_DMA_APU_MATCHES 0)
set(JP_DMA_MAPPER_MATCHES 0)
foreach(JP_SOURCE IN LISTS JP_DMA_OLD_SOURCES)
 if(JP_SOURCE MATCHES "cviii_hw_apu_audio\\.c$")
  list(APPEND JP_DMA_NEW_SOURCES "${JP_DMA_APU_OVERLAY}")
  math(EXPR JP_DMA_APU_MATCHES "${JP_DMA_APU_MATCHES} + 1")
 elseif(JP_SOURCE MATCHES "cviii_hw_mapper_fetch_audio\\.c$")
  list(APPEND JP_DMA_NEW_SOURCES "${JP_DMA_MAPPER_OVERLAY}")
  math(EXPR JP_DMA_MAPPER_MATCHES "${JP_DMA_MAPPER_MATCHES} + 1")
 else()
  list(APPEND JP_DMA_NEW_SOURCES "${JP_SOURCE}")
 endif()
endforeach()
if(NOT JP_DMA_APU_MATCHES EQUAL 1 OR NOT JP_DMA_MAPPER_MATCHES EQUAL 1)
 message(FATAL_ERROR "JP0650 requires exactly one real APU and one mapper24 audio overlay")
endif()
set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_DMA_NEW_SOURCES}")
message(STATUS "JP0650 optional DMC DMA actual PRG-byte fetch audit installed")

add_executable(jp_dmc_dma_trace_test_0650
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_dma_trace_0650.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_dma_trace_test_0650.c")
set_property(TARGET jp_dmc_dma_trace_test_0650 PROPERTY C_STANDARD 11)

add_executable(jp_audio_bus_test_0610
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_bus_0610.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_bus_test_0610.c")
set_property(TARGET jp_audio_bus_test_0610 PROPERTY C_STANDARD 11)
# JP0612: private dual-path instruction-fetch observer at original fixed $E249.
# Replaces hw_machine.c in generated target ONLY. Original CPU execution,
# mapper/PPU/APU bus behavior and ROM source are unchanged.
set(JP_REQUEST_MACHINE "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/hw_machine.c")
set(JP_REQUEST_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_machine_requests.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_sound_requests_0612.py"
  --source "${JP_REQUEST_MACHINE}" --out "${JP_REQUEST_OVERLAY}"
 RESULT_VARIABLE JP_REQUEST_PATCH_RESULT
 ERROR_VARIABLE JP_REQUEST_PATCH_ERROR)
if(NOT JP_REQUEST_PATCH_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0612 request observer source contract failed: ${JP_REQUEST_PATCH_ERROR}")
endif()
# JP0646: exact second private overlay uses the actual JP0612 dual opcode tap.
# Do not vendor or modify upstream hw_machine.c or original cartridge bytes.
set(JP_DECISION_OVERLAY "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cviii_hw_machine_decisions.c")
execute_process(
 COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_cyc_sound_decisions_0646.py"
  --source "${JP_REQUEST_OVERLAY}" --out "${JP_DECISION_OVERLAY}"
 RESULT_VARIABLE JP_DECISION_PATCH_RESULT
 ERROR_VARIABLE JP_DECISION_PATCH_ERROR)
if(NOT JP_DECISION_PATCH_RESULT EQUAL 0)
 message(FATAL_ERROR "JP0646 private original-sound decision hook rejected: ${JP_DECISION_PATCH_ERROR}")
endif()
get_target_property(JP_REQUEST_ORIGINAL_SOURCES jp_akumajou_densetsu SOURCES)
set(JP_REQUEST_NEW_SOURCES "")
set(JP_REQUEST_COUNT 0)
foreach(JP_SOURCE IN LISTS JP_REQUEST_ORIGINAL_SOURCES)
 if(JP_SOURCE MATCHES "hw_machine\\.c$")
  list(APPEND JP_REQUEST_NEW_SOURCES "${JP_DECISION_OVERLAY}")
  math(EXPR JP_REQUEST_COUNT "${JP_REQUEST_COUNT} + 1")
 else()
  list(APPEND JP_REQUEST_NEW_SOURCES "${JP_SOURCE}")
 endif()
endforeach()
if(NOT JP_REQUEST_COUNT EQUAL 1)
 message(FATAL_ERROR "JP0612 requires exactly one hw_machine.c in runtime")
endif()
set_property(TARGET jp_akumajou_densetsu PROPERTY SOURCES "${JP_REQUEST_NEW_SOURCES}")
message(STATUS "JP0612 private read-only $E249 instruction-entry trace installed")

add_executable(jp_sound_requests_test_0612
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_requests_0612.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_requests_test_0612.c")
set_property(TARGET jp_sound_requests_test_0612 PROPERTY C_STANDARD 11)

# JP0646: read-only driver-branch logger, synthetic five-path/failure test.
add_executable(jp_sound_decisions_test_0646
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_decisions_0646.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sound_decisions_test_0646.c")
set_property(TARGET jp_sound_decisions_test_0646 PROPERTY C_STANDARD 11)

# JP0648: read-only high-command DMC descriptor-to-register event plans.
# The real 60-byte owner-ROM table is never included in this target or Git.
add_executable(jp_dmc_source_test_0648
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_source_0648.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_source_test_0648.c")
set_property(TARGET jp_dmc_source_test_0648 PROPERTY C_STANDARD 11)
# JP0655: ROM-free complete ordinary-byte/nibble/multiplier arithmetic
# regression; the actual original-ROM opcode comparison remains private.
add_executable(jp_phrase_delta_test_0655
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_delta_0655.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_delta_test_0655.c")
set_property(TARGET jp_phrase_delta_test_0655 PROPERTY C_STANDARD 11)

# JP0656 source-authenticated raw0C control command grammar, ROM-free native test.
add_executable(jp_phrase_control_test_0656
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_control_0656.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_phrase_control_test_0656.c")
set_property(TARGET jp_phrase_control_test_0656 PROPERTY C_STANDARD 11)
# JP0657 stage/room source format plus original room-coordinate arithmetic.
add_executable(jp_room_catalog_test_0657
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_catalog_0657.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_catalog_test_0657.c")
set_property(TARGET jp_room_catalog_test_0657 PROPERTY C_STANDARD 11)
add_executable(jp_room_coordinate_test_0657
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_coordinate_0657.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_coordinate_test_0657.c")
set_property(TARGET jp_room_coordinate_test_0657 PROPERTY C_STANDARD 11)
# JP0658 original room-state-zero original 6502 → native RAM + 2048 PPU events
add_executable(jp_room_state0_test_0658
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_ppu_stream_0658.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_state0_0658.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_state0_test_0658.c")
set_property(TARGET jp_room_state0_test_0658 PROPERTY C_STANDARD 11)
# JP0659: original room0A->room0E banked five-record-source native lift.
add_executable(jp_room_stream_test_0659
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_stream_0659.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_room_stream_test_0659.c")
set_property(TARGET jp_room_stream_test_0659 PROPERTY C_STANDARD 11)


# JP0649: dormant bounded source/mapper8 + raw DPCM 7-bit decoder.
# Original-JP sample bytes and ROM-derived fixtures remain owner-private.
add_executable(jp_dpcm_decode_test_0649
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dmc_source_0648.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dpcm_decode_0649.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_dpcm_decode_test_0649.c")
set_property(TARGET jp_dpcm_decode_test_0649 PROPERTY C_STANDARD 11)

# JP0614: owner-local session epochs; host callbacks only, not machine state.
add_executable(jp_audio_session_test_0614
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_session_0614.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_session_test_0614.c")
set_property(TARGET jp_audio_session_test_0614 PROPERTY C_STANDARD 11)

# JP0618 enhanced-only final PCM gain and persistable three volume levels.
add_executable(jp_audio_levels_test_0618
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_test_0618.c")
set_property(TARGET jp_audio_levels_test_0618 PROPERTY C_STANDARD 11)

# JP0647: separate host-only virtual voice mixer with independent gains.
add_executable(jp_virtual_audio_test_0647
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_virtual_audio_0647.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_virtual_audio_test_0647.c")
set_property(TARGET jp_virtual_audio_test_0647 PROPERTY C_STANDARD 11)

# JP0647: separate deterministic event-timed synthetic stage/FX soundtrack.
add_executable(jp_virtual_scene_test_0647
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_virtual_audio_0647.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_virtual_scene_test_0647.c")
set_property(TARGET jp_virtual_scene_test_0647 PROPERTY C_STANDARD 11)

# JP0619: authentic private CHR slider/number renderer, synthetic pixels only.
add_executable(jp_audio_ui_test_0619
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_ui_0619.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_ui_test_0619.c")
set_property(TARGET jp_audio_ui_test_0619 PROPERTY C_STANDARD 11)

# JP0620: namespaced and validated native menu registration, no ROM/SDL.
add_executable(jp_menu_registry_test_0620
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_registry_0620.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_registry_test_0620.c")
set_property(TARGET jp_menu_registry_test_0620 PROPERTY C_STANDARD 11)

# JP0622: actual game-owned F6 modal behavior isolated for deterministic testing.
add_executable(jp_audio_menu_state_test_0622
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_menu_state_0622.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_menu_state_test_0622.c")
set_property(TARGET jp_audio_menu_state_test_0622 PROPERTY C_STANDARD 11)

# JP0623: modular menu actions and original JP font layout (ROM-free).
add_executable(jp_start_menu_test_0623
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_menu_0623.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_menu_test_0623.c")
set_property(TARGET jp_start_menu_test_0623 PROPERTY C_STANDARD 11)
add_executable(jp_start_ui_test_0623
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_menu_0623.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_ui_0623.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_slot_picker_0625.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_ui_test_0623.c")
set_property(TARGET jp_start_ui_test_0623 PROPERTY C_STANDARD 11)

# JP0625: Save/Load action subpage shares the pinned host's ten slots.
add_executable(jp_slot_picker_test_0625
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_slot_picker_0625.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_slot_picker_test_0625.c")
set_property(TARGET jp_slot_picker_test_0625 PROPERTY C_STANDARD 11)

# JP0626: parent menu focus remains paused during nested Audio transitions.
add_executable(jp_menu_stack_test_0626
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_stack_0626.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_start_menu_0623.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_menu_state_0622.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_audio_levels_0618.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_stack_test_0626.c")
set_property(TARGET jp_menu_stack_test_0626 PROPERTY C_STANDARD 11)
