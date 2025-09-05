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
    static const wxColor blackColor = wxColor(10, 10, 10);

    GaugePanel::GaugePanel(MainWindow* mainWnd, Telem& telem)
        : wxPanel(mainWnd, wxID_ANY)
        , mMainWindow(mainWnd)
        , mMainSizer(new wxBoxSizer(wxVERTICAL))
    {
        const int margin = FromDIP(20);
        const int marginHz = FromDIP(40);

        const wxColor labelBgrColor = blackColor; //wxColor(100, 100, 100);
        const wxColor labelColor = wxColor(255, 255, 100);
        
        SetBackgroundColour(gOrange);

        auto sizer = new wxGridBagSizer(margin, marginHz);
        std::vector<std::pair<wxGBPosition, wxGBSpan>> items =
        {
            {{0, 0}, {1, 1}},
            {{0, 1}, {1, 1}}
        };

        mPercentView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 4.0f);
        sizer->Add(mPercentView, items[0].first, items[0].second, wxEXPAND);

        mPercentBg = new wxPanel(this, wxID_ANY);
        mPercentBg->SetBackgroundColour(gOrange);
        sizer->Add(mPercentBg, items[1].first, items[1].second, wxEXPAND);

        mPercentFg = new wxPanel(
            mPercentBg,
            wxID_ANY
        );
        mPercentFg->SetBackgroundColour(blackColor);

        sizer->AddGrowableRow(0, 1);

        sizer->AddGrowableCol(0, 1);
        sizer->AddGrowableCol(1, 2);

        sizer->SetMinSize(FromDIP(wxSize(600, 400)));

        SetSizer(sizer);

        const int overallMarginHz = FromDIP(200);
        mMainSizer->Add(this, 1, wxEXPAND | wxALL, margin);

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
        static bool isOn = false;
        static auto lastTime = std::chrono::high_resolution_clock::now();
        
        constexpr double adcMax = 4095.0;
        constexpr float gaugePopupDuration = 2.0;

        int knob1Percent = (knob1 / adcMax) * 100.0;
        int knob2Percent = (knob2 / adcMax) * 100.0;
        if (knob1Percent != mKnob1Percent)
        {
            mKnob1Percent = knob1Percent;
            mPercentView->SetLabel(std::to_string(mKnob1Percent) + "%");
            mMainWindow->SetMode(2); // TODO: use cleaner method
            // Set up gauge window, color
            isOn = true;
            lastTime = std::chrono::high_resolution_clock::now();
        }
        else if (knob2Percent != mKnob2Percent)
        {
            mKnob2Percent = knob2Percent;
            mPercentView->SetLabel(std::to_string(mKnob2Percent) + "%");
            mMainWindow->SetMode(2); // TODO: use cleaner method
            // Set up gauge window, color
            isOn = true;
            lastTime = std::chrono::high_resolution_clock::now();
        }
        else
        {
            if (isOn)
            {
                auto currentTime = std::chrono::high_resolution_clock::now();
                if (float time = std::chrono::duration<float, std::chrono::seconds::period>(currentTime - lastTime).count();
                    time >= gaugePopupDuration)
                {
                    mMainWindow->SetMode(0); // TODO: could pop the window, but this should work fine
                    isOn = false;
                }
            }
        }
    }

    void GaugePanel::OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
    {
#ifdef FRUCD_USE_RASPI
        // TODO: slowish decoding, made for ease of use and compatibility w python variant - could be optimized
        std::unordered_map<std::string, std::pair<const dbcppp::ISignal*, double>> sigMap;
        for (const dbcppp::ISignal& sig : msg.Signals())
        {
            const auto* muxSignal = msg.MuxSignal();
            if (sig.MultiplexerIndicator() != dbcppp::ISignal::EMultiplexer::MuxValue ||
                (muxSignal && muxSignal->Decode(frame.data) == sig.MultiplexerSwitchValue()))
            {
                //for (const auto& e : sig.ValueEncodingDescriptions()) std::cerr << e.Description() << std::endl;
                sigMap[sig.Name()] = std::make_pair(&sig, sig.RawToPhys(sig.Decode(frame.data)));
            }
        }

        if (msg.Name() == "Dashboard_Knobs")
        {
            UpdateKnobs(sigMap["Knob1"].second, sigMap["Knob2"].second);
        }
#endif
    }
}