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

//#ifdef FRUCD_USE_RASPI
#include <ADS1263/ADS1263.h>
//#endif

namespace frucd
{
    static constexpr std::string_view gFields = "ID,D0,D1,D2,D3,D4,D5,D6,D7,Timestamp";

    static std::string GetFormattedTime();

    Telem::Telem()
        : mCsvFile(GetCsvPath())
        , mAdcData{ 0, 0, 0, 0, 0, 0 }
    {
        mCsvFile << gFields << '\n';
        WriteRow(0x0382);

#ifdef FRUCD_USE_RASPI
        InitAdHat();
#endif
    }

    Telem::~Telem()
    {
#ifdef FRUCD_USE_RASPI
        DEV_Module_Exit();
#endif
    }

    void Telem::Log()
    {
#ifdef FRUCD_USE_RASPI
        LogAdc();
#endif
    }

    void Telem::LogAdc()
    {
#ifdef FRUCD_USE_RASPI
        for (std::size_t i = 0; i < sNumAdcs; ++i)
        {
            mAdcData[i] = GetVoltage(ADS1263_GetChannalValue(i));
        }
        WriteRow(0x0382);
#endif
    }

    void Telem::WriteRow(int32_t id)
    {
        double fractional_seconds_since_epoch
            = std::chrono::duration_cast<std::chrono::duration<double>>(
                std::chrono::system_clock::now().time_since_epoch()).count();
        mCsvFile << id << ",0,0,0,0,0,0,0,0," << (GetTimestamp() * 1000) << '\n';
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
        {
            return sRefVoltage * 2 - rawReading / 2147483648.0 * sRefVoltage;
        }
        else
        {
            return sRefVoltage * rawReading / 2147483648.0;
        }
    }
}