#pragma once

#include <fstream>
#include <functional>
#include <filesystem>
#include <deque>
#include <array>
#include <unordered_map>

#include <dbcppp/Network.h>

struct can_frame;

namespace frucd
{
    using CanCallback = std::function<void(
        const dbcppp::IMessage&,
        const dbcppp::INetwork&,
        const can_frame&)>;

    class Telem
    {
    public:
        Telem();
        ~Telem();

        void Log();

        void RegisterCanObserver(const CanCallback& feHandler, const CanCallback& mcHandler);

    private:
        void LogCan();
        void LogAdc();

        void WriteRow(int32_t id, std::array<double, 8>&& values);

    private:
        void InitAdHat();
        void InitCan();

    private:
        struct TelemObserver
        {
            CanCallback feHandler;
            CanCallback mcHandler;

            TelemObserver(CanCallback feHandler, CanCallback mcHandler)
                : feHandler(feHandler), mcHandler(mcHandler) {}
        };

        using CanSocket = int;
        static constexpr std::size_t sNumAdcs = 6;
        static constexpr double sRefVoltage = 5;
        
        std::ofstream mCsvFile;

        std::array<double, sNumAdcs> mAdcData;

        std::unique_ptr<dbcppp::INetwork> mFeSpec;
        std::unique_ptr<dbcppp::INetwork> mMcSpec;
        CanSocket mCanSock;

        std::unordered_map<uint64_t, const dbcppp::IMessage*> mFeMsgs;
        std::unordered_map<uint64_t, const dbcppp::IMessage*> mMcMsgs;

        std::vector<TelemObserver> mObservers;

    private:
        static std::filesystem::path GetCsvPath();
        static int64_t GetTimestamp();
        static constexpr double GetVoltage(uint32_t rawReading);
    };
}
