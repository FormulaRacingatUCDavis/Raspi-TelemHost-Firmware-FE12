#pragma once

#include <string>
#include <chrono>
#include <unordered_map>

#include <wx/wx.h>
#include <dbcppp/Network.h>

struct can_frame;

namespace frucd
{
    class MainWindow;
    class Telem;

    class MainPanel : public wxPanel
    {
    public:
        MainPanel(MainWindow* mainWnd, Telem& telem);

        void UpdateState(std::string vcuState, std::string bmsState);
        void UpdateTemp(double motorTemp, double mcTemp, double packTemp, double soc);
        void UpdateSpeed(double speedRpm);
        void UpdateGlv(double glvVoltage);
        void UpdateKnob(double knob1Adc, double knob2Adc);

    public:
        inline wxSizer* GetSizer() { return mMainSizer; }

    private:
        void OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);
        void OnMcCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);

    private:
        wxSizer* mMainSizer;
        MainWindow* mMainWindow;

        wxTextCtrl* mMphText;
        wxStaticText* mMphView;

        wxTextCtrl* mPackSocitText;
        wxStaticText* mSocView;
        wxStaticText* mTempView;

        wxTextCtrl* mStateText;
        wxStaticText* mStateView;

        wxTextCtrl* mGlvVoltageText;
        wxStaticText* mGlvVoltageView;

        std::chrono::system_clock::time_point mErrorTimestamp;
        std::chrono::system_clock::time_point mKnobTimestamp;

        bool mBmsError = false;
        bool mVcuError = false;

        // States

        std::string mVcuState = "";
        std::string mBmsState = "";

        std::string mShutdown = "";

        double mMotorTemp = 0.0;
        double mMcTemp = 0.0;
        double mPackTemp = 0.0;
        double mSoc = 0.0;

        double mSpeedRpm = 0.0;
        double mGlvVoltage = 0.0;

        double mKnob1Adc = 0.0;
        double mKnob2Adc = 0.0;

        double mMotorSpeed = 0.0;
        double mTorqueFeedback = 0.0;

        double mThrottle2 = 0.0;

        static std::unordered_map<std::string, wxColor> sValidVcuStateColors;
    };
}