#pragma once

#include <wx/wx.h>
#include <dbcppp/Network.h>

struct can_frame;

namespace frucd
{
    class MainWindow;
    class Telem;

    class DebugPanel : public wxPanel
    {
    public:
        DebugPanel(MainWindow* mainWnd, Telem& telem);

    public:
        inline wxSizer* GetSizer() { return mMainSizer; }

    private:
        void OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);
        void OnMcCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);

    private:
        wxSizer* mMainSizer;

        wxStaticText* mSocText;
        wxStaticText* mSocView;

        wxStaticText* mPackTempText;
        wxStaticText* mPackTempView;

        wxStaticText* mShutdownText;
        wxStaticText* mShutdownView;

        wxStaticText* mMcTempText;
        wxStaticText* mMcTempView;

        wxStaticText* mMotorTempText;
        wxStaticText* mMotorTempView;

        wxStaticText* mMcStateText;
        wxStaticText* mMcStateView;

        wxStaticText* mVcuStateText;
        wxStaticText* mVcuStateView;

        wxStaticText* mGlvVoltText;
        wxStaticText* mGlvVoltView;

        wxStaticText* mDebugText;
        wxStaticText* mDebugView;
    };
}