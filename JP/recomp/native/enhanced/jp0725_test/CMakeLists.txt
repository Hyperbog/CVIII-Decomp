cmake_minimum_required(VERSION 3.20)
project(CVIII_JP0725_Presenter_Validation C)
set(NESRECOMP_EXTERNAL_ROOT "" CACHE PATH "Pinned external NESRecomp checkout")
if(NOT EXISTS "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc/cyc_render.h")
 message(FATAL_ERROR "NESRECOMP_EXTERNAL_ROOT must be the pinned external NESRecomp source")
endif()
add_executable(jp_stage1_host_test_0725
 ../cviii_stage1_rom_0724.c
 ../cviii_stage1_atlas_0724.c
 ../cviii_stage1_host_0725.c
 ../cviii_level_preload_0829.c
 ../cviii_rom_tsa_catalog_0730.c
 ../cviii_stage1_join_0751.c
 ../cviii_level1_world_0803.c
 ../cviii_room_catalog_0657.c
 ../cviii_world_sprites_0807.c
 ../cviii_runtime_resources_0727.c
 ../cviii_resource_cache_0729.c
 ../cviii_chr_index_0598.c
 ../cviii_stage1_host_test_0725.c)
target_include_directories(jp_stage1_host_test_0725 PRIVATE
 ../
 "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc")
set_property(TARGET jp_stage1_host_test_0725 PROPERTY C_STANDARD 11)
target_compile_definitions(jp_stage1_host_test_0725 PRIVATE CVIII_RESOURCE_TEST_SYNTHETIC_0727=1)
enable_testing()
add_test(NAME jp0725_native_framebuffer COMMAND jp_stage1_host_test_0725)

# JP0727: exact production SHA256 gate and a separate, explicitly invented
# test-only source import. A test flag must never reach the retail game target.
foreach(JP_RESOURCE_TEST variant_production variant_synthetic)
 add_executable(jp_runtime_resources_0727_${JP_RESOURCE_TEST}
  ../cviii_stage1_rom_0724.c
  ../cviii_stage1_atlas_0724.c
  ../cviii_runtime_resources_0727.c
 ../cviii_resource_cache_0729.c
 ../cviii_chr_index_0598.c
  ../cviii_runtime_resources_test_0727.c)
 set_property(TARGET jp_runtime_resources_0727_${JP_RESOURCE_TEST} PROPERTY C_STANDARD 11)
 if(JP_RESOURCE_TEST STREQUAL "variant_synthetic")
  target_compile_definitions(jp_runtime_resources_0727_${JP_RESOURCE_TEST}
   PRIVATE CVIII_RESOURCE_TEST_SYNTHETIC_0727=1)
 endif()
 add_test(NAME jp_runtime_resources_0727_${JP_RESOURCE_TEST}
  COMMAND jp_runtime_resources_0727_${JP_RESOURCE_TEST})
endforeach()

# JP0730: cross-stage ROM TSA pattern tables; explicit uncertainty guard.
add_executable(jp_tsa_catalog_test_0730
 ../cviii_rom_tsa_catalog_0730.c
 ../cviii_rom_tsa_catalog_test_0730.c)
set_property(TARGET jp_tsa_catalog_test_0730 PROPERTY C_STANDARD 11)
add_test(NAME jp0730_source_bounded_tilesets COMMAND jp_tsa_catalog_test_0730)

# All-level source preload: tests an invented 15-stage/135-room hierarchy.
# No proprietary ROM, actual enemies, or fake NPC spawn behavior.
add_executable(jp_all_level_preload_test_0829
 ../cviii_level_preload_0829.c
 ../cviii_level_preload_test_0829.c
 ../cviii_room_catalog_0657.c
 ../cviii_rom_tsa_catalog_0730.c
 ../cviii_runtime_resources_0727.c
 ../cviii_resource_cache_0729.c
 ../cviii_stage1_rom_0724.c
 ../cviii_stage1_atlas_0724.c
 ../cviii_chr_index_0598.c)
set_property(TARGET jp_all_level_preload_test_0829 PROPERTY C_STANDARD 11)
target_compile_definitions(jp_all_level_preload_test_0829 PRIVATE
 CVIII_LEVEL_PRELOAD_TEST_SYNTHETIC=1 CVIII_RESOURCE_TEST_SYNTHETIC_0727=1)
add_test(NAME jp0829_all_stage_preload COMMAND jp_all_level_preload_test_0829)
