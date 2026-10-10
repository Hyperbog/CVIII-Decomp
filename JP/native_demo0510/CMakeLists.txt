cmake_minimum_required(VERSION 3.16)
project(CVIII_JP_Native_Stage1_Demo LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_executable(cviii-jp-native-demo src/main.cpp)
if(WIN32)
  target_link_libraries(cviii-jp-native-demo PRIVATE user32 gdi32)
else()
  find_package(X11 REQUIRED)
  target_include_directories(cviii-jp-native-demo PRIVATE ${X11_INCLUDE_DIR})
  target_link_libraries(cviii-jp-native-demo PRIVATE ${X11_LIBRARIES})
endif()
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(cviii-jp-native-demo PRIVATE -Wall -Wextra -Werror -pedantic)
endif()
enable_testing()
add_test(NAME native_jp_demo_state_machine COMMAND cviii-jp-native-demo --self-test)
# No private reference-art assets are committed; visual tests are local only.
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/assets/title.ppm" AND
   EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/assets/intro.ppm" AND
   EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/assets/stage.ppm" AND
   EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/assets/player.rgba")
  add_test(NAME native_jp_demo_stage_frame
    COMMAND cviii-jp-native-demo --assets ${CMAKE_CURRENT_SOURCE_DIR}/assets
            --headless --scene stage --frames 120 --script r)
endif()
