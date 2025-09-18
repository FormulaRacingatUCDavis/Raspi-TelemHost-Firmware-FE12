#pragma once

#include <fstream>
#include <functional>
#include <filesystem>
#include <deque>
#include <array>
#include <unordered_map>
#include <memory>
#include <vector>
#include <dbcppp/Network.h>

#include "config.h"

struct can_frame;

namespace frucd::daq
{
    using CanCallback = std::function<void(
        const dbcppp::IMessage&,
        const dbcppp::INetwork&,
        const can_frame&)>;

    class TelemetryManager
    {
    public:
        explicit TelemetryManager(const Config& cfg);
        ~TelemetryManager();

        std::filesystem::path init_csv();

        void init_can();
        void log_can();
        void register_can_observer(const CanCallback& feHandler,
                                   const CanCallback& mcHandler);

        // void init_ad_hat();
        // void log_adc();

    private:
        void write_row(int32_t id, std::array<double, 8>&& values);

        struct TelemObserver
        {
            CanCallback feHandler;
            CanCallback mcHandler;

            TelemObserver(CanCallback feHandler, CanCallback mcHandler)
                : feHandler(std::move(feHandler)),
                  mcHandler(std::move(mcHandler)) {}
        };

        using CanSocket = int;
        static constexpr std::size_t sNumAdcs = 6;
        static constexpr double sRefVoltage = 5;

        Config mConfig;
        std::ofstream mCsvFile;
        std::array<double, sNumAdcs> mAdcData{};

        std::unique_ptr<dbcppp::INetwork> mFeSpec;
        std::unique_ptr<dbcppp::INetwork> mMcSpec;

        CanSocket mCanSock = -1;
        bool mCanInitialized = false;

        std::unordered_map<uint64_t, const dbcppp::IMessage*> mFeMsgs;
        std::unordered_map<uint64_t, const dbcppp::IMessage*> mMcMsgs;

        std::vector<TelemObserver> mObservers;

        static std::filesystem::path get_csv_path(const std::string& logsDir);
        static int64_t get_timestamp();
        static constexpr double get_voltage(uint32_t rawReading);
    };
}