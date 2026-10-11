cmake_minimum_required(VERSION 3.16)
project(cviii_standalone_sprite_pipeline LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../src")
add_library(cviii_standalone_sprite_pipeline STATIC
  "${SRC_DIR}/actor_slot_0509.cpp"
  "${SRC_DIR}/actor_event_row32_0510.cpp"
  "${SRC_DIR}/actor_motion_prg0b_0511.cpp"
  "${SRC_DIR}/actor_displacement_prg0b_0512.cpp"
  "${SRC_DIR}/actor_displacement_vertical_prg0b_0513.cpp"
  "${SRC_DIR}/actor_preflight_0514.cpp"
  "${SRC_DIR}/actor_collision_precheck_0515.cpp"
  "${SRC_DIR}/actor_collision_measure_0516.cpp"
  "${SRC_DIR}/actor_collision_result_0517.cpp"
  "${SRC_DIR}/scheduler_postcollision_0519.cpp"
  "${SRC_DIR}/scheduler_bd11_followup_0520.cpp"
  "${SRC_DIR}/actor_animation_ef93_0521.cpp"
  "${SRC_DIR}/scheduler_fe63_0522.cpp"
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

# Original JP raw-bank $0B:$8001 two-axis actor motion semantic lift.
add_executable(actor_motion_prg0b_0511_test "${TEST_DIR}/actor_motion_prg0b_0511_test.cpp")
target_link_libraries(actor_motion_prg0b_0511_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_actor_motion_0511 COMMAND actor_motion_prg0b_0511_test)
add_executable(native_actor_motion_replay_0511 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_actor_motion_replay_0511.cpp")
target_link_libraries(native_actor_motion_replay_0511 PRIVATE cviii_standalone_sprite_pipeline)

# Original JP fixed $FDF8 -> raw $0B:$80E3 horizontal displacement.
add_executable(actor_displacement_prg0b_0512_test "${TEST_DIR}/actor_displacement_prg0b_0512_test.cpp")
target_link_libraries(actor_displacement_prg0b_0512_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_horizontal_displacement_0512 COMMAND actor_displacement_prg0b_0512_test)
add_executable(native_displacement_replay_0512 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_displacement_replay_0512.cpp")
target_link_libraries(native_displacement_replay_0512 PRIVATE cviii_standalone_sprite_pipeline)

# Original $0B:$810F/$8140 vertical paths with $8843 continuation.
add_executable(actor_displacement_vertical_prg0b_0513_test "${TEST_DIR}/actor_displacement_vertical_prg0b_0513_test.cpp")
target_link_libraries(actor_displacement_vertical_prg0b_0513_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_vertical_0513 COMMAND actor_displacement_vertical_prg0b_0513_test)
add_executable(actor_post8843_0513_test "${TEST_DIR}/actor_post8843_0513_test.cpp")
target_link_libraries(actor_post8843_0513_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_post8843_0513 COMMAND actor_post8843_0513_test)
add_executable(native_vertical_replay_0513 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_vertical_replay_0513.cpp")
target_link_libraries(native_vertical_replay_0513 PRIVATE cviii_standalone_sprite_pipeline)

# Native source faithful bank30 actor $6B producer and bank0B B1F8 gate.
add_executable(actor_preflight_0514_test "${TEST_DIR}/actor_preflight_0514_test.cpp")
target_link_libraries(actor_preflight_0514_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_actor_preflight_0514 COMMAND actor_preflight_0514_test)
add_executable(native_preflight_replay_0514 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_preflight_replay_0514.cpp")
target_link_libraries(native_preflight_replay_0514 PRIVATE cviii_standalone_sprite_pipeline)

# Original raw bank $0B:$B217-$B231 collision admission and B1F8 composition.
add_executable(actor_collision_precheck_0515_test "${TEST_DIR}/actor_collision_precheck_0515_test.cpp")
target_link_libraries(actor_collision_precheck_0515_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_collision_admission_0515 COMMAND actor_collision_precheck_0515_test)
add_executable(native_collision_precheck_replay_0515 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_collision_precheck_replay_0515.cpp")
target_link_libraries(native_collision_precheck_replay_0515 PRIVATE cviii_standalone_sprite_pipeline)

# Original JP mapped raw-bank $0B B339 collision measurement, B1F8 composition.
add_executable(actor_collision_measure_0516_test "${TEST_DIR}/actor_collision_measure_0516_test.cpp")
target_link_libraries(actor_collision_measure_0516_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_collision_measure_0516 COMMAND actor_collision_measure_0516_test)
add_executable(native_collision_measure_replay_0516 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_collision_measure_replay_0516.cpp")
target_link_libraries(native_collision_measure_replay_0516 PRIVATE cviii_standalone_sprite_pipeline)

# Original JP bank0B B235 tail, empty follower-slot loop, connected B1F8->FDFE.
add_executable(actor_collision_tail_0517_test "${TEST_DIR}/actor_collision_tail_0517_test.cpp")
target_link_libraries(actor_collision_tail_0517_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_collision_tail_0517 COMMAND actor_collision_tail_0517_test)
add_executable(native_tail_replay_0517 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_tail_replay_0517.cpp")
target_link_libraries(native_tail_replay_0517 PRIVATE cviii_standalone_sprite_pipeline)
add_executable(native_composed_replay_0517 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_composed_replay_0517.cpp")
target_link_libraries(native_composed_replay_0517 PRIVATE cviii_standalone_sprite_pipeline)

# Original JP fixed bank31 FDFE-FE2C actor scheduler branch preflight.
add_executable(scheduler_postcollision_0519_test "${TEST_DIR}/scheduler_postcollision_0519_test.cpp")
target_link_libraries(scheduler_postcollision_0519_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_scheduler_gate_0519 COMMAND scheduler_postcollision_0519_test)
add_executable(native_scheduler_replay_0519 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_scheduler_replay_0519.cpp")
target_link_libraries(native_scheduler_replay_0519 PRIVATE cviii_standalone_sprite_pipeline)

# Original JP bank0B BD11 gate and fixed-bank31 FE34–FE60 continuation.
add_executable(scheduler_followup_0520_test "${TEST_DIR}/scheduler_followup_0520_test.cpp")
target_link_libraries(scheduler_followup_0520_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_scheduler_followup_0520 COMMAND scheduler_followup_0520_test)
add_executable(native_followup_replay_0520 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_followup_replay_0520.cpp")
target_link_libraries(native_followup_replay_0520 PRIVATE cviii_standalone_sprite_pipeline)

# Original fixed bank31 $EF93-$EFD1 animation timer / descriptor 0E and full scheduler prefix.
add_executable(actor_animation_ef93_0521_test "${TEST_DIR}/actor_animation_ef93_0521_test.cpp")
target_link_libraries(actor_animation_ef93_0521_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_actor_animation_0521 COMMAND actor_animation_ef93_0521_test)
add_executable(native_animation_replay_0521 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_animation_replay_0521.cpp")
target_link_libraries(native_animation_replay_0521 PRIVATE cviii_standalone_sprite_pipeline)

# Provisional 0522 original $FE63 bank-$0B tail; no original-Mesen certification.
add_executable(scheduler_fe63_0522_test "${TEST_DIR}/scheduler_fe63_0522_test.cpp")
target_link_libraries(scheduler_fe63_0522_test PRIVATE cviii_standalone_sprite_pipeline)
add_test(NAME native_original_scheduler_fe63_foundation_0522 COMMAND scheduler_fe63_0522_test)
add_executable(native_fe63_replay_0522 "${CMAKE_CURRENT_SOURCE_DIR}/../tools/native_fe63_replay_0522.cpp")
target_link_libraries(native_fe63_replay_0522 PRIVATE cviii_standalone_sprite_pipeline)
