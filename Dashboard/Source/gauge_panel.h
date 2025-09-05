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

        // TODO: optimize this
        void Update();

    public:
        inline wxSizer* GetSizer() { return mMainSizer; }

    private:
        void OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame);
    
    private:
        wxSizer* mMainSizer;
        wxStaticText* mPercentView;

        wxPanel* mPercentFg;
        wxPanel* mPercentBg;
    };
}