#include "debug_panel.h"

#include <sstream>
#include <wx/grid.h>
#include <wx/gbsizer.h>

#include "main_window.h"
#include "telem.h"
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
    DebugPanel::DebugPanel(MainWindow* mainWnd, Telem& telem)
        : wxPanel(mainWnd, wxID_ANY)
        , mMainSizer(new wxBoxSizer(wxVERTICAL))
    {

        const wxColor blackColor = wxColor(0, 0, 0);
        const wxColor whiteColor = wxColor(255, 255, 255);
        const wxColor labelColor = wxColor(255, 255, 100);

        const float tFontScale = 5.0f;
        const float vFontScale = 10.0f;
        
        SetBackgroundColour(blackColor);

        auto sizer = new wxGridBagSizer(FromDIP(20), FromDIP(40));
                
        // SOC
        mSocText = CreateTextHeader(this, "SOC", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mSocText, wxGBPosition(0, 0), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mSocView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mSocView->GetParent(), wxGBPosition(1, 0), wxGBSpan(2, 1), wxEXPAND);

        // PACK TEMP
        mPackTempText = CreateTextHeader(this, "PACK TEMP", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mPackTempText, wxGBPosition(0, 1), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mPackTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mPackTempView->GetParent(), wxGBPosition(1, 1), wxGBSpan(2, 1), wxEXPAND);

        // SHUTDOWN
        mShutdownText = CreateTextHeader(this, "SHUTDOWN", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mShutdownText, wxGBPosition(0, 2), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mShutdownView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mShutdownView->GetParent(), wxGBPosition(1, 2), wxGBSpan(2, 1), wxEXPAND);

        // MC TEMP
        mMcTempText = CreateTextHeader(this, "MC TEMP", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mMcTempText, wxGBPosition(3, 0), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mMcTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mMcTempView->GetParent(), wxGBPosition(4, 0), wxGBSpan(2, 1), wxEXPAND);

        // MOTOR TEMP
        mMotorTempText = CreateTextHeader(this, "MOTOR TEMP", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mMotorTempText, wxGBPosition(3, 1), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mMotorTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mMotorTempView->GetParent(), wxGBPosition(4, 1), wxGBSpan(2, 1), wxEXPAND);

        // MC STATE
        mMcStateText = CreateTextHeader(this, "MC STATE", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mMcStateText, wxGBPosition(3, 2), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mMcStateView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mMcStateView->GetParent(), wxGBPosition(4, 2), wxGBSpan(2, 1), wxEXPAND);

        // VCU STATE
        mVcuStateText = CreateTextHeader(this, "STATE", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mVcuStateText, wxGBPosition(6, 0), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mVcuStateView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mVcuStateView->GetParent(), wxGBPosition(7, 0), wxGBSpan(2, 1), wxEXPAND);

        // GLV V
        mGlvVoltText = CreateTextHeader(this, "GLV V", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mGlvVoltText, wxGBPosition(6, 1), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mGlvVoltView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mGlvVoltView->GetParent(), wxGBPosition(7, 1), wxGBSpan(2, 1), wxEXPAND);

        // DEBUG
        // NOTE: you don't currently use the free slot for anything.
        // If you'd like to add something, then just update the code in the handler callbacks.
        mDebugText = CreateTextHeader(this, "DEBUG (TEST)", sizer->GetEmptyCellSize(), labelColor, mainWnd, tFontScale);
        sizer->Add(mDebugText, wxGBPosition(6, 2), wxGBSpan(1, 1), wxALIGN_CENTER, 0);

        mDebugView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, mainWnd, tFontScale);
        sizer->Add(mDebugView->GetParent(), wxGBPosition(7, 2), wxGBSpan(2, 1), wxEXPAND);

        sizer->AddGrowableRow(0, 1);
        sizer->AddGrowableRow(1, 3);
        sizer->AddGrowableRow(2, 3);
        sizer->AddGrowableRow(3, 1);
        sizer->AddGrowableRow(4, 3);
        sizer->AddGrowableRow(5, 3);
        sizer->AddGrowableRow(6, 1);
        sizer->AddGrowableRow(7, 3);
        sizer->AddGrowableRow(8, 3);

        sizer->AddGrowableCol(0);
        sizer->AddGrowableCol(1);
        sizer->AddGrowableCol(2);

        sizer->SetMinSize(FromDIP(wxSize(600, 400)));

        SetSizer(sizer);

        mMainSizer->Add(this, 1, wxEXPAND | wxALL, FromDIP(20));

        telem.RegisterCanObserver(
            [this](const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
            {
                OnFeCan(msg, net, frame);
            },
            [this](const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
            {
                OnMcCan(msg, net, frame);
            }
        );
    }

    void DebugPanel::OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
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

        if (msg.Name() == "Dashboard_Vehicle_State")
        {
            // VCU
            auto [sig, stateNum] = sigMap["State"];
            if (auto state = GetStringEncoding(*sig, static_cast<int64_t>(stateNum));
                state.has_value())
            {
                mVcuStateView->SetLabel(state.value());
                mVcuStateView->GetParent()->Layout();
            }
        }
        else if (msg.Name() == "PEI_Diagnostic_BMS_Data")
        {
            mPackTempView->SetLabel(std::to_string((int32_t)sigMap["HI_Temp"].second) + "C");
            mPackTempView->GetParent()->Layout();
            mSocView->SetLabel(std::to_string((int32_t)sigMap["SOC"].second) + "%");
            mSocView->GetParent()->Layout();
        }
        else if (msg.Name() == "PEI_Status")
        {
            std::string shutdown = "NO_SHUTDOWN";
            auto isState = [&sigMap](const std::string& state) { return sigMap.find(state) != sigMap.end() && sigMap[state].second == 0.0; };
            if (isState("PRECHARGE")) shutdown = "PRECHARGE";
            else if (isState("AIR_NEG")) shutdown = "AIR NEG";
            else if (isState("AIR_POS")) shutdown = "AIR POS";
            else if (isState("BMS_OK")) shutdown = "BMS OK";
            else if (isState("IMD_OK")) shutdown = "IMD OK";
            else if (isState("SHUTDOWN_FINAL")) shutdown = "SHUTDOWN FINAL";
            mShutdownView->SetLabel(shutdown);
            mShutdownView->GetParent()->Layout();
        }
#endif
    }
    
    void DebugPanel::OnMcCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
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

        if (msg.Name() == "M160_Temperature_Set_1")
        {
            double mcTemp = sigMap["INV_Module_A_Temp"].second +
                            sigMap["INV_Module_B_Temp"].second +
                            sigMap["INV_Module_C_Temp"].second / 3.0;
            std::ostringstream str;
            str << std::fixed << std::setprecision(2) << mcTemp;
            mMcTempView->SetLabel(str.str() + "C");
            mMcTempView->GetParent()->Layout();
        }
        else if (msg.Name() == "M162_Temperature_Set_3")
        {
            std::ostringstream str;
            str << std::fixed << std::setprecision(2) << sigMap["INV_Motor_Temp"].second;
            mMotorTempView->SetLabel(str.str() + "C");
            mMotorTempView->GetParent()->Layout();
        }
        else if (msg.Name() == "M169_Internal_Voltages")
        {
            std::ostringstream str;
            str << std::fixed << std::setprecision(2) << sigMap["INV_Ref_Voltage_12_0"].second;
            mGlvVoltView->SetLabel(str.str());
            mGlvVoltView->GetParent()->Layout();
        }
        else if (msg.Name() == "M171_Fault_Codes")
        {
            // TODO: test if you need uint32 cast first
            if ((sigMap["INV_Post_Fault_Lo"].second != 0.0) && (sigMap["INV_Post_Fault_Hi"].second != 0.0))
            {
                // TODO: MC State
            }
        }
#endif
    }
}
