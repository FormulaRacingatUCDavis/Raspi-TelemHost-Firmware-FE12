#include "gauge_panel.h"

#include <sstream>
#include <wx/gbsizer.h>
#include <wx/dcbuffer.h>   // for wxAutoBufferedPaintDC
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

        // Knob value
        mPercentView = CreateTextView(this, "0", sizer->GetEmptyCellSize(), mainWnd, 13.0f);
        sizer->Add(mPercentView->GetParent(),
                   wxGBPosition(0, 0), wxGBSpan(1, 1), wxEXPAND);
        mPercentView->GetParent()->SetBackgroundColour(gDodgerBlue);

        // Bar gauge
        mBarGauge = new wxPanel(this);
        mBarGauge->SetBackgroundStyle(wxBG_STYLE_PAINT);
        sizer->Add(mBarGauge, wxGBPosition(0, 1), wxGBSpan(1, 1), wxEXPAND);
        mBarGauge->Bind(wxEVT_PAINT, &GaugePanel::OnBarPaint, this);

        sizer->AddGrowableRow(0);
        sizer->AddGrowableCol(0);
        sizer->AddGrowableCol(1);

        sizer->SetMinSize(FromDIP(wxSize(600, 400)));

        SetSizer(sizer);
        mMainSizer->Add(this, 1, wxEXPAND, 0);

        telem.RegisterCanObserver(
            [this](const dbcppp::IMessage& msg,
                   const dbcppp::INetwork& net,
                   const can_frame& frame)
            {
                OnFeCan(msg, net, frame);
            },
            [](const dbcppp::IMessage&,
               const dbcppp::INetwork&,
               const can_frame&)
            {
            }
        );
    }

    void GaugePanel::UpdateKnobs(double knob)
    {
        mKnob = std::clamp(static_cast<int>(knob), 0, 100);

        if (mPercentView)
        {
            mPercentView->SetLabel(std::to_string(mKnob));
            mPercentView->GetParent()->Layout();
        }

        if (mBarGauge)
            mBarGauge->Refresh();
    }

    void GaugePanel::OnBarPaint(wxPaintEvent& evt)
    {
        wxAutoBufferedPaintDC dc(mBarGauge);
        wxSize sz = mBarGauge->GetClientSize();

        // Empty background
        dc.SetBrush(wxBrush(*wxBLACK));
        dc.SetPen(*wxTRANSPARENT_PEN);
        dc.DrawRectangle(0, 0, sz.x, sz.y);

        // Yellow fill
        int filledHeight = (sz.y * mKnob) / 100;
        dc.SetBrush(wxBrush(gYellow));
        dc.DrawRectangle(0, sz.y - filledHeight, sz.x, filledHeight);
    }

    void GaugePanel::OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
    {
#ifdef FRUCD_USE_RASPI
        std::unordered_map<std::string, std::pair<const dbcppp::ISignal*, double>> sigMap;
        for (const dbcppp::ISignal& sig : msg.Signals())
        {
            const auto* muxSignal = msg.MuxSignal();
            if (sig.MultiplexerIndicator() != dbcppp::ISignal::EMultiplexer::MuxValue ||
                (muxSignal && muxSignal->Decode(frame.data) == sig.MultiplexerSwitchValue()))
            {
                sigMap[sig.Name()] = std::make_pair(&sig, sig.RawToPhys(sig.Decode(frame.data)));
            }
        }

        if (msg.Name() == "Dashboard_Knobs")
        {
            double knob1 = sigMap["Knob1"].second;
            double knob2 = sigMap["Knob2"].second;
            UpdateKnobs(knob1);
        }

#endif
    }
}