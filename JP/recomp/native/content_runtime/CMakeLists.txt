cmake_minimum_required(VERSION 3.20)
project(CVIII_Content_0731 C)
# This content-only subtree is intentionally independent of NESRecomp,
# SDL2, Python and JP_ORIGINAL_JP_ROM. Original media is passed only to
# the already-built executable at launch, never at CMake configure time.
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CVIII_CONTENT_SOURCES
 ../enhanced/cviii_stage1_rom_0724.c
 ../enhanced/cviii_stage1_atlas_0724.c
 ../enhanced/cviii_chr_index_0598.c
 ../enhanced/cviii_runtime_resources_0727.c
 ../enhanced/cviii_resource_cache_0729.c
 ../enhanced/cviii_rom_tsa_catalog_0730.c)

add_library(cviii_original_rom_content_0731 STATIC ${CVIII_CONTENT_SOURCES})
target_include_directories(cviii_original_rom_content_0731 PUBLIC ../enhanced)
add_executable(cviii_content_probe_0731 cviii_content_probe_0731.c)
target_link_libraries(cviii_content_probe_0731 PRIVATE
 cviii_original_rom_content_0731)

enable_testing()
add_executable(cviii_content_production_test_0731
 ../enhanced/cviii_runtime_resources_test_0727.c)
target_link_libraries(cviii_content_production_test_0731 PRIVATE
 cviii_original_rom_content_0731)
add_test(NAME JP0731_ProductionRejectsSynthetic
 COMMAND cviii_content_production_test_0731)

# Never add this test-only synthetic bypass to the production content
# library or the production launcher.
add_executable(cviii_content_synthetic_test_0731
 ${CVIII_CONTENT_SOURCES}
 ../enhanced/cviii_runtime_resources_test_0727.c)
target_include_directories(cviii_content_synthetic_test_0731 PRIVATE ../enhanced)
target_compile_definitions(cviii_content_synthetic_test_0731 PRIVATE
 CVIII_RESOURCE_TEST_SYNTHETIC_0727=1)
add_test(NAME JP0731_SyntheticImportCacheRoundTrip
 COMMAND cviii_content_synthetic_test_0731)

add_executable(cviii_content_tsa_test_0731
 ../enhanced/cviii_rom_tsa_catalog_test_0730.c)
target_link_libraries(cviii_content_tsa_test_0731 PRIVATE
 cviii_original_rom_content_0731)
add_test(NAME JP0731_CrossStageDefinitions
 COMMAND cviii_content_tsa_test_0731)
