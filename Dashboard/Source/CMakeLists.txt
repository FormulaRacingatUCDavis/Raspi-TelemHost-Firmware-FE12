# Source

target_sources(frucd_raspi_dash
    PRIVATE
        main.cpp

        display.h
        display.cpp

        main_window.h
        main_window.cpp

        main_panel.h
        main_panel.cpp

        debug_panel.h
        debug_panel.cpp

        gauge_panel.h
        gauge_panel.cpp

        telem.h
        telem.cpp

        utils.h
        utils.cpp

        palette.h
)

target_link_libraries(frucd_raspi_dash
    PRIVATE
        wxgl wxbase wxcore
)
