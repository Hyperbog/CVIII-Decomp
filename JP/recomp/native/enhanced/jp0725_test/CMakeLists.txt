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
 ../cviii_stage1_host_test_0725.c)
target_include_directories(jp_stage1_host_test_0725 PRIVATE
 ../
 "${NESRECOMP_EXTERNAL_ROOT}/runner/cyc")
set_property(TARGET jp_stage1_host_test_0725 PROPERTY C_STANDARD 11)
enable_testing()
add_test(NAME jp0725_native_framebuffer COMMAND jp_stage1_host_test_0725)
