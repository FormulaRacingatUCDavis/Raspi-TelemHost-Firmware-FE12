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

    class GaugePanel : public wxPanel
    {
    public:
        GaugePanel(MainWindow* mainWnd, Telem& telem);

        void UpdateKnobs(double knob);

    public:
        inline wxSizer* GetSizer() { return mMainSizer; }

    private:
        void OnFeCan(const dbcppp::IMessage& msg,
                     const dbcppp::INetwork& net,
                     const can_frame& frame);
        void OnBarPaint(wxPaintEvent& evt);

    private:
        wxSizer* mMainSizer;
        MainWindow* mMainWindow;

        wxStaticText* mPercentView;
        wxPanel* mBarGauge;

        int mKnob{0};
    };
}
