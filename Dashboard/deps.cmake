include(FetchContent)

# https://stackoverflow.com/questions/66736809/wxwidgets-and-fetch-content-in-cmake
set(wxBUILD_SHARED OFF)
set(wxBUILD_PRECOMP OFF)
set(wxBUILD_MONOLITHIC OFF)

FetchContent_Declare(
    wxWidgets
    GIT_REPOSITORY https://github.com/wxWidgets/wxWidgets.git
    GIT_TAG 49c6810948f40c457e3d0848b9111627b5b61de5
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)

FetchContent_GetProperties(wxWidgets)
FetchContent_MakeAvailable(wxWidgets)
