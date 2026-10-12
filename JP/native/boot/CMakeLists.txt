cmake_minimum_required(VERSION 3.16)
project(castlevania3_jp_native_boot_static LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_executable(jp_native_boot boot_native_driver.cpp generated/boot_compiled.cpp ../bank0a/generated/bank0a_compiled.cpp)
target_include_directories(jp_native_boot PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
if(MSVC)
  target_compile_options(jp_native_boot PRIVATE /W4 /WX)
  # MSVC C4702: template-generated 6502 BRK paths throw before a following
  # dispatch return. Suppress ONLY in the generated bank0A translation unit.
  set_source_files_properties(../bank0a/generated/bank0a_compiled.cpp
    PROPERTIES COMPILE_OPTIONS "/wd4702")
else()
  target_compile_options(jp_native_boot PRIVATE -Wall -Wextra -Werror -pedantic)
endif()
enable_testing()
add_test(NAME native_boot_unmapped_fail_closed COMMAND jp_native_boot --self-test)
