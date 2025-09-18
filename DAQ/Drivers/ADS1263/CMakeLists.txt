add_library(ADS1263
    Driver/ADS1263.c
    Config/DEV_Config.c
    Config/RPI_sysfs_gpio.c
    Config/bcm2835.c
)

# Export include directories
target_include_directories(ADS1263 PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/Driver
    ${CMAKE_CURRENT_SOURCE_DIR}/Config
)

# Match demo build flags
target_compile_definitions(ADS1263 PRIVATE RPI USE_BCM2835_LIB DEBUG)