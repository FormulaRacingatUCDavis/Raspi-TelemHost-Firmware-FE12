#pragma once
#include <string>

namespace frucd::daq
{
    struct Config {
        std::string logsDir;
        std::string assetsDir;
        std::string feDbcFile;
        std::string mcDbcFile;
        std::string canNode;
    };

    Config load_config(const std::string& path);
}