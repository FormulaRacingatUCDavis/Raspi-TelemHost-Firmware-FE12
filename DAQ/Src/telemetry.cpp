#include "telemetry.h"
#include "config.h"

#include <chrono>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <numeric>
#include <filesystem>
#include <fstream>

#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

extern "C" {
    #include "ADS1263.h"
    #include "DEV_Config.h"
}

namespace frucd::daq
{
    static constexpr std::string_view gFields = "ID,D0,D1,D2,D3,D4,D5,D6,D7,Timestamp";
    static std::string get_formatted_time();

    TelemetryManager::TelemetryManager(const Config& cfg)
        : mConfig(cfg)
    {
    }

    TelemetryManager::~TelemetryManager()
    {
        if (mCanSock >= 0)
        {
            close(mCanSock);
            mCanSock = -1;
        }
    }

    void TelemetryManager::register_can_observer(const CanCallback& feHandler, const CanCallback& mcHandler)
    {
        mObservers.emplace_back(feHandler, mcHandler);
    }

    std::filesystem::path TelemetryManager::init_csv()
    {
        auto path = get_csv_path(mConfig.logsDir);
        mCsvFile.open(path, std::ios::out | std::ios::trunc);
        if (!mCsvFile.is_open())
            throw std::runtime_error("Failed to open CSV file: " + path.string());

        mCsvFile << gFields << '\n';
        mCsvFile.flush();

        return path;
    }

    void TelemetryManager::init_can()
    {
        std::ifstream feDbc(mConfig.feDbcFile);
        std::ifstream mcDbc(mConfig.mcDbcFile);
        if (!feDbc.is_open() || !mcDbc.is_open())
            throw std::runtime_error("Failed to open DBC files from config.json");

        mFeSpec = dbcppp::INetwork::LoadDBCFromIs(feDbc);
        mMcSpec = dbcppp::INetwork::LoadDBCFromIs(mcDbc);
        if (!mFeSpec.get())
            throw std::runtime_error("Failed to parse FRUCD DBC file.");
        else if (!mMcSpec.get())
            throw std::runtime_error("Failed to parse CM200 Inverter DBC file.");

        for (const auto& msg : mFeSpec->Messages())
            mFeMsgs.insert(std::make_pair(msg.Id(), &msg));
        for (const auto& msg : mMcSpec->Messages())
            mMcMsgs.insert(std::make_pair(msg.Id(), &msg));

        mCanSock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (mCanSock == -1)
            throw std::runtime_error("Failed to open CAN socket!");

        struct sockaddr_can addr{};
        struct ifreq ifr{};
        strncpy(ifr.ifr_name, mConfig.canNode.c_str(), IFNAMSIZ - 1);
        ifr.ifr_name[IFNAMSIZ - 1] = '\0';

        if (ioctl(mCanSock, SIOCGIFINDEX, &ifr) < 0)
        {
            int savedErr = errno;
            close(mCanSock);
            mCanSock = -1;
            throw std::runtime_error("Failed to get CAN interface index for " + mConfig.canNode + ": " + strerror(savedErr));
        }

        timeval tv{};
        tv.tv_sec = 1;
        tv.tv_usec = 0;
        setsockopt(mCanSock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));

        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (bind(mCanSock, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0)
        {
            int savedErr = errno;
            close(mCanSock);
            mCanSock = -1;
            throw std::runtime_error("Failed to bind to CAN interface " + mConfig.canNode + ": " + strerror(savedErr));
        }

        mCanInitialized = true;
        std::cout << "Initialized CAN on " << mConfig.canNode << " (ifindex " << ifr.ifr_ifindex << ")" << std::endl;
    }

    void TelemetryManager::log_can()
    {
        if (!mCanInitialized || mCanSock < 0)
        {
            std::cerr << "log_can called but CAN not initialized!\n";
            return;
        }

        if (!mFeSpec || !mMcSpec)
        {
            std::cerr << "log_can called without loaded DBC specs!\n";
            return;
        }

        can_frame frame{};
        int numBytes = read(mCanSock, &frame, sizeof(can_frame));
        if (numBytes < 0)
        {
            if (errno != EAGAIN && errno != EWOULDBLOCK)
                perror("CAN read failed");
            return;
        }

        uint32_t id = (0x1FFFFFFF & frame.can_id);
        if (auto it = mFeMsgs.find(id); it != mFeMsgs.end())
        {
            auto* msg = it->second;
            for (auto& observer : mObservers)
                observer.feHandler(*msg, *mFeSpec, frame);
        }
        else if (auto it = mMcMsgs.find(id); it != mMcMsgs.end())
        {
            auto* msg = it->second;
            for (auto& observer : mObservers)
                observer.mcHandler(*msg, *mMcSpec, frame);
        }

        std::array<double, 8> values{};
        for (int i = 0; i < frame.can_dlc && i < 8; ++i)
        {
            values[i] = frame.data[i];
        }
        write_row(frame.can_id, std::move(values));
    }

    void TelemetryManager::write_row(int32_t id, std::array<double, 8>&& values)
    {
        mCsvFile
            << id << ','
            << values[0] << ','
            << values[1] << ','
            << values[2] << ','
            << values[3] << ','
            << values[4] << ','
            << values[5] << ','
            << values[6] << ','
            << values[7] << ','
            << (get_timestamp() * 1000) << '\n';
    }

    int64_t TelemetryManager::get_timestamp()
    {
        double fractional_seconds_since_epoch =
            std::chrono::duration_cast<std::chrono::duration<double>>(
                std::chrono::system_clock::now().time_since_epoch())
                .count();
        return (int64_t)fractional_seconds_since_epoch;
    }

    std::filesystem::path TelemetryManager::get_csv_path(const std::string& logsDir)
    {
        std::filesystem::path csvPath = logsDir;
        std::filesystem::create_directories(csvPath);
        return (csvPath / get_formatted_time()).replace_extension(".csv");
    }

    std::string get_formatted_time()
    {
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::put_time(std::localtime(&in_time_t), "%Y%m%d_%H%M%S");
        return ss.str();
    }

    constexpr double TelemetryManager::get_voltage(uint32_t rawReading)
    {
        if (rawReading >> 31 == 0x1)
            return sRefVoltage * 2 - rawReading / 2147483648.0 * sRefVoltage;
        else
            return sRefVoltage * rawReading / 2147483648.0;
    }
}