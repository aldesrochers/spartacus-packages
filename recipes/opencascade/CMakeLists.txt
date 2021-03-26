cmake_minimum_required(VERSION 2.8)
project(ConanWrapper)

message(STATUS "Conan CMake Wrapper")
include(conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CMAKE_SOURCE_DIR}/sources)
add_subdirectory("sources")
