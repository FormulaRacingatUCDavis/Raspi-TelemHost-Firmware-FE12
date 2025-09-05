include(FetchContent)

# https://stackoverflow.com/questions/66736809/wxwidgets-and-fetch-content-in-cmake
set(wxBUILD_SHARED OFF)
set(wxBUILD_PRECOMP OFF)
set(wxBUILD_MONOLITHIC OFF)

set(build_kcd OFF CACHE BOOL "Enable support for KCD parsing" FORCE)
set(build_tools OFF CACHE BOOL "Build dbcppp utility application" FORCE)

set(build_tests OFF CACHE BOOL "Build tests" FORCE)
set(build_examples OFF CACHE BOOL "Build examples" FORCE)

FetchContent_Declare(
    wxWidgets
    GIT_REPOSITORY https://github.com/wxWidgets/wxWidgets.git
    GIT_TAG 49c6810948f40c457e3d0848b9111627b5b61de5
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)

FetchContent_Declare(
    dbcppp
    GIT_REPOSITORY https://github.com/xR3b0rn/dbcppp
    GIT_TAG b520607559223ac02a7ca87d47b4932cd9f3d21b
)

FetchContent_GetProperties(wxWidgets dbcppp)
FetchContent_MakeAvailable(wxWidgets dbcppp)
