cmake_minimum_required(VERSION 3.10)
project(RaspiTelemHost C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Dependencies
include(cmake/deps.cmake)

add_subdirectory(DAQ/Drivers/ADS1263)

# Collect all DAQ sources
set(DAQ_SOURCES
    DAQ/Src/main.cpp
    DAQ/Src/telemetry.cpp
    DAQ/Src/config.cpp
)

add_executable(DAQ ${DAQ_SOURCES})

target_include_directories(DAQ PRIVATE
    DAQ/Inc
)

target_link_libraries(DAQ PRIVATE
    ADS1263
    bcm2835
    m
    dbcppp::dbcppp
    nlohmann_json::nlohmann_json
)

target_compile_definitions(DAQ PRIVATE
    RPI
    USE_BCM2835_LIB
    DEBUG
)

set_target_properties(DAQ PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

add_custom_command(TARGET DAQ POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/DAQ/config.json
        $<TARGET_FILE_DIR:DAQ>/config.json
)