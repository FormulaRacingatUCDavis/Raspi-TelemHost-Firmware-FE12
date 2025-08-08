# Source

target_sources(frucd_raspi_dash
    PRIVATE
        main.cpp

        display.h
        display.cpp

        main_window.h
        main_window.cpp

        telem.h
        telem.cpp
)

target_link_libraries(frucd_raspi_dash
    PRIVATE
        wxbase wxcore
)
