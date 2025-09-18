include(FetchContent)

# Disable extras we don’t need
set(build_kcd OFF CACHE BOOL "Enable support for KCD parsing" FORCE)
set(build_tools OFF CACHE BOOL "Build dbcppp utility application" FORCE)
set(build_tests OFF CACHE BOOL "Build tests" FORCE)
set(build_examples OFF CACHE BOOL "Build examples" FORCE)

# dbcppp
FetchContent_Declare(
    dbcppp
    GIT_REPOSITORY https://github.com/xR3b0rn/dbcppp.git
    GIT_TAG b520607559223ac02a7ca87d47b4932cd9f3d21b
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)
FetchContent_MakeAvailable(dbcppp)

if(TARGET dbcppp)
    add_library(dbcppp::dbcppp ALIAS dbcppp)
endif()

# nlohmann/json (header-only)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)
FetchContent_MakeAvailable(nlohmann_json)

if(TARGET nlohmann_json)
    add_library(nlohmann_json::nlohmann_json ALIAS nlohmann_json)
endif()