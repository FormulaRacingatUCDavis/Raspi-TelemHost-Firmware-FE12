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

        void UpdateKnobs(double knob1, double knob2);

    public:
        inline wxSizer* GetSizer() { return mMainSizer; }

    private:
        void OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);
    
    private:
        wxSizer* mMainSizer;
        MainWindow* mMainWindow;
        
        wxStaticText* mPercentView;
        wxStaticText* mTest1;
        wxStaticText* mTest2;

        wxPanel* mPercentFg;
        wxPanel* mPercentBg;

        int mKnob1Percent{0};
        int mKnob2Percent{0};
    };
}