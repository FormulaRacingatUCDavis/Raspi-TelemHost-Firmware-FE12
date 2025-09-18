#include "config.h"
#include <nlohmann/json.hpp>

#include <fstream>
#include <iostream>
#include <stdexcept>
#include <filesystem>

namespace frucd::daq
{
    Config load_config(const std::string& path)
    {
        std::filesystem::path abs = std::filesystem::absolute(path);

        std::ifstream f(abs);
        if (!f.is_open())
            throw std::runtime_error("Could not open config file: " + abs.string());

        nlohmann::json j;
        f >> j;

        std::filesystem::path base = abs.parent_path();

        Config cfg;
        cfg.assetsDir = (base / j["paths"]["assets"].get<std::string>()).string();
        cfg.feDbcFile = (base / j["dbc"]["fe"].get<std::string>()).string();
        cfg.mcDbcFile = (base / j["dbc"]["mc"].get<std::string>()).string();
        cfg.canNode   = j["can"]["node"].get<std::string>();

        if (cfg.canNode == "can0")
            cfg.logsDir = (base / j["paths"]["logs"].get<std::string>()).lexically_normal().string();
        else if (cfg.canNode == "vcan0")
            cfg.logsDir = (base / j["paths"]["test_logs"].get<std::string>()).lexically_normal().string();

        std::cerr << "Loaded config from: " << abs << "\n";
        return cfg;
    }
}