cmake_minimum_required(VERSION 3.29)

project(frucd_raspi_dash VERSION 0.1)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(deps.cmake)

add_executable(frucd_raspi_dash)

add_subdirectory(Source)
add_subdirectory(Vendor)