cmake_minimum_required(VERSION 3.20)
project(CVIII_ReShade_Lighting_Addon LANGUAGES CXX)
# Experimental external ReShade add-on: Windows x64 only, never part of
# the playable C11 Alpha and never redistributes the ReShade runtime.
if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
 message(FATAL_ERROR "CVIII ReShade add-on is Windows x64 only")
endif()
set(CVIII_RESHADE_SDK_ROOT "" CACHE PATH "A local ReShade 6.8 SDK checkout with initialized deps/imgui")
if(NOT EXISTS "${CVIII_RESHADE_SDK_ROOT}/include/reshade.hpp" OR
   NOT EXISTS "${CVIII_RESHADE_SDK_ROOT}/deps/imgui/imgui.h")
 message(FATAL_ERROR "Set CVIII_RESHADE_SDK_ROOT to a full ReShade SDK checkout with deps/imgui populated")
endif()
add_library(cviii_reshade_lighting SHARED cviii_lighting_reshade_addon.cpp)
target_compile_features(cviii_reshade_lighting PRIVATE cxx_std_17)
target_include_directories(cviii_reshade_lighting PRIVATE
 "${CVIII_RESHADE_SDK_ROOT}/include"
 "${CVIII_RESHADE_SDK_ROOT}/deps/imgui"
 "${CMAKE_CURRENT_LIST_DIR}/../native/enhanced")
target_compile_definitions(cviii_reshade_lighting PRIVATE
 NOMINMAX WIN32_LEAN_AND_MEAN)
set_target_properties(cviii_reshade_lighting PROPERTIES
 PREFIX "" OUTPUT_NAME "CVIII_Lighting" SUFFIX ".addon64")
