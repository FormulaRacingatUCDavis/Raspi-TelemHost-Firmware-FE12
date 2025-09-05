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

        wxTextCtrl* mSocText;
        wxStaticText* mSocView;

        wxTextCtrl* mPackTempText;
        wxStaticText* mPackTempView;

        wxTextCtrl* mShutdownText;
        wxStaticText* mShutdownView;

        wxTextCtrl* mMcTempText;
        wxStaticText* mMcTempView;

        wxTextCtrl* mMotorTempText;
        wxStaticText* mMotorTempView;

        wxTextCtrl* mMcStateText;
        wxStaticText* mMcStateView;

        wxTextCtrl* mVcuStateText;
        wxStaticText* mVcuStateView;

        wxTextCtrl* mGlvVoltText;
        wxStaticText* mGlvVoltView;

        wxTextCtrl* mDebugText;
        wxStaticText* mDebugView;
    };
}