cmake_minimum_required(VERSION 3.20)
project(CVIII_JP0732_Runtime C)

# JP0732: compile NESRecomp's interpreter + mapper/PPU/APU as a prebuilt
# host. Original Japanese media is supplied ONLY to the running program.
# This target does not run NESRecomp, prepare_project.py, or consume a ROM
# in CMake. External NESRecomp stays pinned and separately licensed.
set(NESRECOMP_EXTERNAL_ROOT "" CACHE PATH "Pinned NESRecomp source checkout")
if(NOT EXISTS "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc.cmake")
 message(FATAL_ERROR "Supply the pinned NESRECOMP_EXTERNAL_ROOT checkout")
endif()
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
# The pinned upstream host intentionally uses POSIX/GNU extensions for
# clock_gettime, usleep and strdup. Keep gnu11 on Unix and C11 on MSVC.
set(CMAKE_C_EXTENSIONS ON)
option(JP0732_WINDOWED "Enable SDL2 window and normal user controls if SDL2 is present" ON)
option(JP0732_ENHANCED "Compile the existing game-owned Enhanced host presentation" ON)
set(NESRECOMP_PPU_IMPL "LLE" CACHE STRING "Cycle PPU rendering implementation")
include("${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc.cmake")

# JP0740 private diagnostic option; OFF for all normal production builds.
# Create copy-only overlays of the exact pinned NESRecomp sources.
option(JP0740_TRACE_CPU_WRITES
 "Internal original-JP mapped opcode and CPU bus write trace" OFF)
if(JP0740_TRACE_CPU_WRITES)
 if(NOT JP0732_ENHANCED)
  message(FATAL_ERROR "JP0740 requires JP0733 SHA-verified original ROM entry")
 endif()
 find_package(Python3 COMPONENTS Interpreter REQUIRED)
 set(JP0740_OVERLAY_DIR "${CMAKE_CURRENT_BINARY_DIR}/jp0740_private_overlay")
 execute_process(
  COMMAND "${Python3_EXECUTABLE}"
   "${CMAKE_CURRENT_LIST_DIR}/../../tools/jp0740_native_write_overlay.py"
   --machine "${NESRECOMP_CYC_DIR}/hw_machine.c"
   --run "${NESRECOMP_CYC_DIR}/cyc_run.c"
   --output-directory "${JP0740_OVERLAY_DIR}"
  RESULT_VARIABLE JP0740_PATCH_EXIT
  OUTPUT_VARIABLE JP0740_PATCH_OUTPUT
  ERROR_VARIABLE JP0740_PATCH_ERROR)
 if(NOT JP0740_PATCH_EXIT EQUAL 0)
  message(FATAL_ERROR "JP0740 pinned overlay failed: ${JP0740_PATCH_ERROR}")
 endif()
 foreach(JP0740_ORIGINAL hw_machine.c cyc_run.c)
  list(FIND NESRECOMP_CYC_SOURCES
   "${NESRECOMP_CYC_DIR}/${JP0740_ORIGINAL}" JP0740_SRC_INDEX)
  if(JP0740_SRC_INDEX LESS 0)
   message(FATAL_ERROR "JP0740 original CYC source missing")
  endif()
  list(REMOVE_ITEM NESRECOMP_CYC_SOURCES
   "${NESRECOMP_CYC_DIR}/${JP0740_ORIGINAL}")
 endforeach()
 list(APPEND NESRECOMP_CYC_SOURCES
  "${JP0740_OVERLAY_DIR}/cviii_jp0740_hw_machine.c"
  "${JP0740_OVERLAY_DIR}/cviii_jp0740_cyc_run.c")
 message(STATUS "JP0740 opt-in private CPU trace: ${JP0740_PATCH_OUTPUT}")
endif()

# JP0735: the four independently ROM-authenticated reset instructions
# default to narrow native handlers. All other original guest instructions
# remain interpreted. The existing single-opcode JP0734 synthetic-only proof
# is a separate mutually exclusive mode. Neither path uses generated code.
option(JP0735_ENABLE_ORIGINAL_BOOT_NATIVE
 "Original JP fixed PRG31 boot native instructions (4 guarded entries)" ON)
if(JP0735_ENABLE_ORIGINAL_BOOT_NATIVE AND NOT JP0732_ENHANCED)
 message(FATAL_ERROR
  "JP0735 native original instruction dispatch requires authenticated JP0733 game entry; enable JP0732_ENHANCED")
endif()
option(JP0734_TEST_NATIVE_LDA
 "Testing ONLY: generic native LDA #imm on invented Mapper24 ROM" OFF)
option(JP0733_ALLOW_SYNTHETIC_FIXTURE
 "Testing ONLY: accept invented Mapper24 media at entry" OFF)
if(JP0734_TEST_NATIVE_LDA AND
   (NOT JP0733_ALLOW_SYNTHETIC_FIXTURE OR JP0735_ENABLE_ORIGINAL_BOOT_NATIVE))
 message(FATAL_ERROR "JP0734 requires synthetic fixture ON and JP0735 original handlers OFF")
endif()
if(JP0734_TEST_NATIVE_LDA)
 set(CVIII_0734_NATIVE_SOURCE
  "${CMAKE_CURRENT_LIST_DIR}/cviii_test_native_lda_0734.c")
elseif(JP0735_ENABLE_ORIGINAL_BOOT_NATIVE)
 set(CVIII_0734_NATIVE_SOURCE
  "${CMAKE_CURRENT_LIST_DIR}/cviii_original_boot_native_0735.c")
else()
 set(CVIII_0734_NATIVE_SOURCE
  "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc_native_none.c")
endif()
add_executable(jp_akumajou_runtime_0732
 ${NESRECOMP_CYC_SOURCES}
 ${CVIII_0734_NATIVE_SOURCE})
target_include_directories(jp_akumajou_runtime_0732 PRIVATE
 ${NESRECOMP_CYC_INCLUDE_DIRS})
if(JP0740_TRACE_CPU_WRITES)
 target_sources(jp_akumajou_runtime_0732 PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/cviii_jp0740_native_trace.c")
 target_include_directories(jp_akumajou_runtime_0732 PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}"
  "${NESRECOMP_EXTERNAL_ROOT}/common")
endif()
target_link_libraries(jp_akumajou_runtime_0732 PRIVATE
 ${NESRECOMP_CYC_LIBRARIES})
target_compile_definitions(jp_akumajou_runtime_0732 PRIVATE
 _CRT_SECURE_NO_WARNINGS)
if(JP0735_ENABLE_ORIGINAL_BOOT_NATIVE AND JP0733_ALLOW_SYNTHETIC_FIXTURE)
 target_compile_definitions(jp_akumajou_runtime_0732 PRIVATE
  CVIII_JP0735_REPORT_HITS=1)
endif()

if(JP0732_ENHANCED)
 # An independent game-owned entry point checks full ROM SHA256 before
 # delegating to the unchanged upstream host. Rename only upstream main
 # on this target; no code generation, patching or media at build time.
 set_source_files_properties(
  "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc_host.c"
  PROPERTIES COMPILE_DEFINITIONS "main=cviii_upstream_main_0733")
 target_sources(jp_akumajou_runtime_0732 PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/cviii_runtime_entry_0733.c")
 if(JP0733_ALLOW_SYNTHETIC_FIXTURE)
  target_compile_definitions(jp_akumajou_runtime_0732 PRIVATE
    CVIII_JP0733_TEST_SYNTHETIC_ROM=1)
 endif()
 target_compile_definitions(jp_akumajou_runtime_0732 PRIVATE
   CVIII_0732_NO_PRIVATE_OBSERVERS=1)
 target_sources(jp_akumajou_runtime_0732 PRIVATE
   "${CMAKE_CURRENT_LIST_DIR}/cviii_uninstrumented_observers_0732.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_edition.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_index_0598.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_audit_0599.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_chr_fetch_0600.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_frame_evidence_0601.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_nt_trace_0606.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_stage1_rom_0724.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_stage1_atlas_0724.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_stage1_host_0725.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_runtime_resources_0727.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_resource_cache_0729.c"
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_rom_tsa_catalog_0730.c"
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
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced/cviii_menu_stack_0626.c"
 )
 target_include_directories(jp_akumajou_runtime_0732 PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../enhanced")
endif()

if(JP0732_WINDOWED)
 nesrecomp_cyc_enable_sdl(jp_akumajou_runtime_0732 NO_DEV_UI)
endif()

# Pure software backend needs no copyrighted media during configuration.
# Run tests using a separately generated invented mapper24 fixture.
message(STATUS "JP0732 runtime interpreter: no ROM at configure or build time")
message(STATUS "JP0732 external NESRecomp: ${NESRECOMP_EXTERNAL_ROOT}")
