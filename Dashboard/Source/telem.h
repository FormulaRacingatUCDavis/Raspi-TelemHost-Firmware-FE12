#pragma once

#include <fstream>
#include <filesystem>
#include <deque>
#include <array>

namespace frucd
{
    class Telem
    {
    public:
        Telem();
        ~Telem();

        void Log();

    private:
        void LogCan();
        void LogAdc();

        void WriteRow(int32_t id);

    private:
        void InitAdHat();

    private:
        static constexpr std::size_t sNumAdcs = 6;
        static constexpr double sRefVoltage = 5;
        
        std::ofstream mCsvFile;

        std::array<double, sNumAdcs> mAdcData;

    private:
        static std::filesystem::path GetCsvPath();
        static int64_t GetTimestamp();
        static constexpr double GetVoltage(uint32_t rawReading);
    };
}
