#include "telem.h"

#include <chrono>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <chrono>
#include <numeric>

#include <wx/wx.h>

#ifdef FRUCD_USE_RASPI
    #include <ADS1263/ADS1263.h>
    #include <sys/socket.h>
    #include <sys/ioctl.h>
    #include <net/if.h>
    #include <linux/can.h>
    #include <linux/can/raw.h>
#endif

namespace frucd
{
    static constexpr std::string_view gFields = "ID,D0,D1,D2,D3,D4,D5,D6,D7,Timestamp";

    static std::string GetFormattedTime();

    Telem::Telem()
        : mCsvFile(GetCsvPath())
        , mAdcData{ 0, 0, 0, 0, 0, 0 }
    {
        mCsvFile << gFields << '\n';

        //InitAdHat(); // TODO: need actual hw for this
        InitCan();
    }

    Telem::~Telem()
    {
#ifdef FRUCD_USE_RASPI
        DEV_Module_Exit();
        close(mCanSock);
#endif
    }

    void Telem::Log()
    {
        //LogAdc(); // TODO: test with hw
        LogCan();
    }

    void Telem::RegisterCanObserver(const CanCallback& feHandler, const CanCallback& mcHandler)
    {
        mObservers.emplace_back(feHandler, mcHandler);
    }

    void Telem::LogCan()
    {
#ifdef FRUCD_USE_RASPI
        can_frame frame;
        int numBytes = read(mCanSock, &frame, sizeof(can_frame));

        uint32_t id = (0x1FFFFFFF & frame.can_id);
        if (auto it = mFeMsgs.find(id);
            it != mFeMsgs.end())
        {
            auto* msg = it->second;
            for (auto& observer : mObservers)
                observer.feHandler(*msg, *mFeSpec, frame);
        }
        else if (auto it = mMcMsgs.find(id);
                    it != mMcMsgs.end())
        {
            auto* msg = it->second;
            for (auto& observer : mObservers)
                observer.mcHandler(*msg, *mMcSpec, frame);
        }
#endif
    }

    void Telem::LogAdc()
    {
#ifdef FRUCD_USE_RASPI
        for (std::size_t i = 0; i < sNumAdcs; ++i)
        {
            mAdcData[i] = GetVoltage(ADS1263_GetChannalValue(i));
        }
        WriteRow(0x0382,
                {
                    mAdcData[0], mAdcData[1], mAdcData[2], mAdcData[3],
                    mAdcData[4], mAdcData[5], mAdcData[6], mAdcData[7]
                });
#endif
    }

    void Telem::WriteRow(int32_t id, std::array<double, 8>&& values)
    {
        double fractional_seconds_since_epoch
            = std::chrono::duration_cast<std::chrono::duration<double>>(
                std::chrono::system_clock::now().time_since_epoch()).count();
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
                << (GetTimestamp() * 1000) << '\n';
    }

    void Telem::InitAdHat()
    {
#ifdef FRUCD_USE_RASPI
        DEV_Module_Init();
        
        ADS1263_SetMode(0);

        UBYTE res = ADS1263_init_ADC1(ADS1263_400SPS);
        if (res == 1)
        {
            throw std::runtime_error("No ADS!"); // TODO: Better error handling?
        }

        std::cerr << "Initialized ADS1263!\n";
#endif
        
    }

    void Telem::InitCan()
    {
#ifdef FRUCD_USE_RASPI
        static constexpr std::string_view assetsDir = "Assets";
        static constexpr std::string_view feDbcFile = "FE12.dbc";
        static constexpr std::string_view mcDbcFile = "20230606Gen5CANDB.dbc";
        
        // Init DBC
        const auto cwd = std::filesystem::current_path();
        std::ifstream feDbc(cwd / assetsDir / feDbcFile);
        std::ifstream mcDbc(cwd / assetsDir / mcDbcFile);
        if (!feDbc.is_open() || !mcDbc.is_open())
        {
            throw std::runtime_error("Failed to open dbc files. Is the assets directory visible from the current directory?");
        }

        // interface = socketcan, node = vcan0
        mFeSpec = dbcppp::INetwork::LoadDBCFromIs(feDbc);
        mMcSpec = dbcppp::INetwork::LoadDBCFromIs(mcDbc);

        if (!mFeSpec.get())
        {
            throw std::runtime_error("Failed to parse FE dbc file.");
        }
        else if (!mMcSpec.get())
        {
            throw std::runtime_error("Failed to parse MC dbc file.");
        }
        
        for (const auto& msg : mFeSpec->Messages())
            mFeMsgs.insert(std::make_pair(msg.Id(), &msg));
        
        for (const auto& msg : mMcSpec->Messages())
            mMcMsgs.insert(std::make_pair(msg.Id(), &msg));
        
        static constexpr std::string_view nodeName = "vcan0"; // TODO: change this when using an actual can device
        mCanSock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (mCanSock == -1)
        {
            throw std::runtime_error("Failed to open can socket!");
        }

        // https://www.kernel.org/doc/Documentation/networking/can.txt
        struct sockaddr_can addr;
        struct ifreq ifr;
        strcpy(ifr.ifr_name, nodeName.data());
        ioctl(mCanSock, SIOCGIFINDEX, &ifr);

        timeval tv;
        tv.tv_sec   = 1; // seconds timeout
        tv.tv_usec  = 0;
        setsockopt(mCanSock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));

        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;
        bind(mCanSock, (struct sockaddr*)&addr, sizeof(addr));
#endif
    }

    int64_t Telem::GetTimestamp()
    {
        double fractional_seconds_since_epoch
            = std::chrono::duration_cast<std::chrono::duration<double>>(
                std::chrono::system_clock::now().time_since_epoch()).count();
        return (int64_t)fractional_seconds_since_epoch;
    }

    std::filesystem::path Telem::GetCsvPath()
    {
        auto logDir = std::filesystem::current_path() / "logs";
        std::filesystem::create_directory(logDir); // Creates if doesn't exist
        return (logDir / GetFormattedTime()).replace_extension(".csv");
    }

    std::string GetFormattedTime()
    {
        // https://stackoverflow.com/questions/17223096/outputting-date-and-time-in-c-using-stdchrono
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::put_time(std::localtime(&in_time_t), "%Y%m%d_%H%M%S");
        return ss.str();
    }

    constexpr double Telem::GetVoltage(uint32_t rawReading)
    {
        // https://github.com/waveshareteam/High-Pricision_AD_HAT/blob/master/c/examples/main.c
        if (rawReading >> 31 == 0x1)
            return sRefVoltage * 2 - rawReading / 2147483648.0 * sRefVoltage;
        else
            return sRefVoltage * rawReading / 2147483648.0;
    }
}