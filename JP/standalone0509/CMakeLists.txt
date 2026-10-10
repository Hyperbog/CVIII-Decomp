cmake_minimum_required(VERSION 3.16)
project(cviii_standalone_sprite_pipeline LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../src")
add_library(cviii_standalone_sprite_pipeline STATIC
  "${SRC_DIR}/actor_slot_0509.cpp"
  "${SRC_DIR}/actor_event_row32_0510.cpp"
  "${SRC_DIR}/standalone_scene_0509.cpp"
  "${SRC_DIR}/oam_renderer.cpp"
  "${SRC_DIR}/collision_math.cpp")
target_include_directories(cviii_standalone_sprite_pipeline PUBLIC "${SRC_DIR}")
target_compile_options(cviii_standalone_sprite_pipeline PRIVATE -Wall -Wextra -Werror -pedantic)
add_executable(cviii-standalone-preview "${CMAKE_CURRENT_SOURCE_DIR}/../tools/standalone_preview_0509.cpp")
target_link_libraries(cviii-standalone-preview PRIVATE cviii_standalone_sprite_pipeline)
set(TEST_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../tests")
add_executable(actor_slot_0509_test "${TEST_DIR}/actor_slot_0509_test.cpp")
target_link_libraries(actor_slot_0509_test PRIVATE cviii_standalone_sprite_pipeline)
add_executable(standalone_scene_0509_test "${TEST_DIR}/standalone_scene_0509_test.cpp")
target_link_libraries(standalone_scene_0509_test PRIVATE cviii_standalone_sprite_pipeline)
enable_testing()
add_test(NAME actor_slot_0509 COMMAND actor_slot_0509_test)
add_test(NAME standalone_scene_0509 COMMAND standalone_scene_0509_test)
add_test(NAME standalone_preview_rom_free COMMAND cviii-standalone-preview 120 RRRRRRRRRRRRRRRRRRRRJ /tmp/cviii_standalone_ci_0509.ppm)

# Original-JP ROM-free source-lift regressions; does not run the NES emulator.
add_executable(actor_event_row32_0510_test "${TEST_DIR}/actor_event_row32_0510_test.cpp")
target_link_libraries(actor_event_row32_0510_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_row32_source_lift COMMAND actor_event_row32_0510_test)
add_executable(native_row32_replay_0510 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_row32_replay_0510.cpp")
target_link_libraries(native_row32_replay_0510 PRIVATE cviii_standalone_sprite_pipeline)
