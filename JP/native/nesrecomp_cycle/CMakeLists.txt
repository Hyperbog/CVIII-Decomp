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
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_index_0598.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_audit_0599.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_fetch_0600.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_frame_evidence_0601.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_nt_trace_0606.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_sprite_layers_0608.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_0609.c")
endif()
nesrecomp_add_cycle_game(jp_akumajou_densetsu
 ROM "${JP_ORIGINAL_JP_ROM}" ${JP_CYCLE_OPTIONS} ${JP_HOST_SOURCES})
if(JP_EDITION_HOST_EXTRAS)
 target_include_directories(jp_akumajou_densetsu PRIVATE
  "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced")
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
 get_target_property(JP_GAME_SOURCES jp_akumajou_densetsu SOURCES)
 set(JP_PATCHED_SOURCES "")
 set(JP_SDL_REPLACEMENTS 0)
 foreach(JP_FILE IN LISTS JP_GAME_SOURCES)
  if(JP_FILE MATCHES "cyc_sdl\\.c$")
   list(APPEND JP_PATCHED_SOURCES "${JP_BOOTSTRAP_OVERLAY}")
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
 message(STATUS "CVIII: quick-saves, F10 stage/companion and password bootstrap enabled")
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

# JP0609: ROM-free dynamic object/OAM rotation capture unit test.
add_executable(jp_object_oam_test_0609
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_0609.c"
 "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_object_oam_trace_test_0609.c")
set_property(TARGET jp_object_oam_test_0609 PROPERTY C_STANDARD 11)
