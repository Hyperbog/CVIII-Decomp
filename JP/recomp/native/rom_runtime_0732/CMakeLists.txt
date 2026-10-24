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

# cyc_native_none is an upstream-proven adapter: no unvalidated ROM code
# can be called as native code. cyc_run.c automatically executes all ROM/RAM
# instructions through the same accurate cpu6502_interp.c fallback.
add_executable(jp_akumajou_runtime_0732
 ${NESRECOMP_CYC_SOURCES}
 "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc_native_none.c")
target_include_directories(jp_akumajou_runtime_0732 PRIVATE
 ${NESRECOMP_CYC_INCLUDE_DIRS})
target_link_libraries(jp_akumajou_runtime_0732 PRIVATE
 ${NESRECOMP_CYC_LIBRARIES})
target_compile_definitions(jp_akumajou_runtime_0732 PRIVATE
 _CRT_SECURE_NO_WARNINGS)

if(JP0732_ENHANCED)
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
