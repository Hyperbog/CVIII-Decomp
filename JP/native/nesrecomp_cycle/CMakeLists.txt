cmake_minimum_required(VERSION 3.20)
project(JP_Akumajou_Densetsu_Cycle C)
# NESRecomp is an external, separately licensed PolyForm Noncommercial
# dependency. DO NOT vendor its sources or game-derived generated C files.
set(JP_ORIGINAL_JP_ROM "" CACHE FILEPATH "Privately supplied verified original Japanese ROM")
set(NESRECOMP_EXTERNAL_ROOT "" CACHE PATH "External checkout of mstan/nesrecomp")
option(JP_CYCLE_HEADLESS "Build a headless C11 cycle runtime" ON)
if(NOT EXISTS "${JP_ORIGINAL_JP_ROM}")
 message(FATAL_ERROR "JP_ORIGINAL_JP_ROM must name the privately owned original ROM")
endif()
if(NOT EXISTS "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/project.cmake")
 message(FATAL_ERROR "NESRECOMP_EXTERNAL_ROOT must contain runner/cyc/project.cmake")
endif()
find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
execute_process(
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/../../tools/nesrecomp_cycle_0568.py"
   --validate-rom "${JP_ORIGINAL_JP_ROM}"
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
nesrecomp_add_cycle_game(jp_akumajou_densetsu
 ROM "${JP_ORIGINAL_JP_ROM}" ${JP_CYCLE_OPTIONS})
