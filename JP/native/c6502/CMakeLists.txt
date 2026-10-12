cmake_minimum_required(VERSION 3.16)
project(JP_C6502_Recompiled C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
option(JP_C6502_HOST_ONLY "Build ROM-free C11 CPU smoke without game-generated code" OFF)
set(JP_C6502_GEN_DIR "" CACHE PATH "Absolute path to authenticated locally generated C11 source")
add_library(jp_c6502_core STATIC cpu.c opcode_table.c)
target_include_directories(jp_c6502_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
if(MSVC)
 target_compile_options(jp_c6502_core PRIVATE /W4 /WX)
else()
 target_compile_options(jp_c6502_core PRIVATE -Wall -Wextra -Werror -pedantic)
endif()
enable_testing()
add_executable(jp_c6502_smoke test_cpu.c)
target_link_libraries(jp_c6502_smoke PRIVATE jp_c6502_core)
add_test(NAME jp_c6502_smoke COMMAND jp_c6502_smoke)
if(NOT JP_C6502_HOST_ONLY)
 if(NOT EXISTS "${JP_C6502_GEN_DIR}/bank0a_compiled.c" OR
    NOT EXISTS "${JP_C6502_GEN_DIR}/boot_compiled.c")
  message(FATAL_ERROR
    "No original-JP generated C files. Run JP/tools/regen_c11_0564.py "
    "--rom ORIGINAL_JP_ROM --out PRIVATE_BUILD_DIR, then configure "
    "-DJP_C6502_GEN_DIR=PRIVATE_BUILD_DIR/gen. "
    "For ROM-free source tests use -DJP_C6502_HOST_ONLY=ON.")
 endif()
 add_executable(jp_c6502 main.c
  "${JP_C6502_GEN_DIR}/bank0a_compiled.c"
  "${JP_C6502_GEN_DIR}/boot_compiled.c")
 target_link_libraries(jp_c6502 PRIVATE jp_c6502_core)
 if(MSVC)
  target_compile_options(jp_c6502 PRIVATE /W4 /WX)
 else()
  target_compile_options(jp_c6502 PRIVATE -Wall -Wextra -Werror -pedantic)
 endif()
endif()
