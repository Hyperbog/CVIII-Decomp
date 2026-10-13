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
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_edition.c")
endif()
nesrecomp_add_cycle_game(jp_akumajou_densetsu
 ROM "${JP_ORIGINAL_JP_ROM}" ${JP_CYCLE_OPTIONS} ${JP_HOST_SOURCES})
if(JP_EDITION_HOST_EXTRAS)
 target_include_directories(jp_akumajou_densetsu PRIVATE
  "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc")
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

