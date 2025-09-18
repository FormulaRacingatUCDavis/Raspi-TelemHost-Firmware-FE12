target_include_directories(frucd_raspi_dash
    PRIVATE
        "${CMAKE_CURRENT_LIST_DIR}"
)

target_link_libraries(frucd_raspi_dash
    PRIVATE
        dbcppp
)

if (LINUX)
    message(STATUS "Compiling Raspberry Pi Utilities")

    target_compile_definitions(frucd_raspi_dash
        PRIVATE
            FRUCD_USE_RASPI=1
            RPI=1
            USE_BCM2835_LIB=1
    )

    target_sources(frucd_raspi_dash
        PRIVATE
            ADS1263/ADS1263.h
            ADS1263/ADS1263.c

            ADS1263/DEV_Config.h
            ADS1263/DEV_Config.c

            ADS1263/Debug.h

            ADS1263/RPI_sysfs_gpio.h
            ADS1263/RPI_sysfs_gpio.c

            ADS1263/dev_hardware_SPI.h
            ADS1263/dev_hardware_SPI.c

            ADS1263/bcm2835.h
            ADS1263/bcm2835.c

            # ADS1263/sysfs_gpio.h
            # ADS1263/sysfs_gpio.c

            # ADS1263/sysfs_software_spi.h
            # ADS1263/sysfs_software_spi.c
    )

    target_link_libraries(frucd_raspi_dash
        PRIVATE
            X11
    )
else ()
    message(STATUS "Not Using Raspberry Pi")
endif()

