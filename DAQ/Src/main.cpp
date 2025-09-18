#include "telemetry.h"
#include "config.h"
#include <iostream>

int main()
{
    try
    {
        auto cfg = frucd::daq::load_config("DAQ/config.json");
        frucd::daq::TelemetryManager telem(cfg);

        try
        {
            telem.init_can();
        }
        catch (const std::exception& e)
        {
            std::cerr << "init_can failed: " << e.what() << "\n";
            return 1;
        }

        auto csvPath = telem.init_csv();
        std::cout << "Logging to " << csvPath << std::endl;

        while (true)
        {
            telem.log_can();
        }
    }
    catch (const std::exception& e)
    {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
}