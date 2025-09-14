#include "gauge_panel.h"

#include <sstream>

#include <wx/gbsizer.h>

#include "main_window.h"
#include "palette.h"
#include "utils.h"

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
    GaugePanel::GaugePanel(MainWindow* mainWnd, Telem& telem)
        : wxPanel(mainWnd, wxID_ANY)
        , mMainWindow(mainWnd)
        , mMainSizer(new wxBoxSizer(wxVERTICAL))
    {   
        SetBackgroundColour(wxColor(0, 0, 0));

        auto sizer = new wxGridBagSizer(0, 0);

        mTest1 = CreateTextView(this, "TEST1", sizer->GetEmptyCellSize(), mainWnd, 9.0f);
        sizer->Add(mTest1->GetParent(), wxGBPosition(0, 0), wxGBSpan(2, 1), wxEXPAND);
        mTest1->GetParent()->SetBackgroundColour(gDodgerBlue);

        mTest2 = CreateTextView(this, "TEST2", sizer->GetEmptyCellSize(), mainWnd, 9.0f);
        sizer->Add(mTest2->GetParent(), wxGBPosition(0, 1), wxGBSpan(2, 1), wxEXPAND);
        mTest2->GetParent()->SetBackgroundColour(gRed);

        sizer->AddGrowableRow(0);
        sizer->AddGrowableRow(1);
        sizer->AddGrowableCol(0);
        sizer->AddGrowableCol(1);

        sizer->SetMinSize(FromDIP(wxSize(600, 400)));

        SetSizer(sizer);

        mMainSizer->Add(this, 1, wxEXPAND, 0);

        telem.RegisterCanObserver(
            [this](const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
            {
                OnFeCan(msg, net, frame);
            },
            [this](const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
            {
            }
        );
    }

    void GaugePanel::UpdateKnobs(double knob1, double knob2)
    {
        
    }

    void GaugePanel::OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
    {
#ifdef FRUCD_USE_RASPI

#endif
    }
}