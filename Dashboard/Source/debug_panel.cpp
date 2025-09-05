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
        const int margin = FromDIP(20);
        const int marginHz = FromDIP(40);

        const wxColor blackColor = wxColor(10, 10, 10);
        const wxColor whiteColor = wxColor(255, 255, 255);
        const wxColor labelBgrColor = blackColor; //wxColor(100, 100, 100);
        const wxColor labelColor = wxColor(255, 255, 100);
        
        SetBackgroundColour(blackColor);

        auto sizer = new wxGridBagSizer(margin, marginHz);
                
        std::vector<std::pair<wxGBPosition, wxGBSpan>> items =
        {
            {{0, 0}, {1, 1}},
            {{0, 1}, {1, 1}},
            {{0, 2}, {1, 1}},

            {{1, 0}, {2, 1}},
            {{1, 1}, {2, 1}},
            {{1, 2}, {2, 1}},

            {{3, 0}, {1, 1}},
            {{3, 1}, {1, 1}},
            {{3, 2}, {1, 1}},

            {{4, 0}, {2, 1}},
            {{4, 1}, {2, 1}},
            {{4, 2}, {2, 1}},

            {{6, 0}, {1, 1}},
            {{6, 1}, {1, 1}},
            {{6, 2}, {1, 1}},

            {{7, 0}, {2, 1}},
            {{7, 1}, {2, 1}},
            {{7, 2}, {2, 1}},
        };

        // Soc
        mSocText = CreateTextHeader(this, "SOC", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mSocText, items[0].first, items[0].second, wxEXPAND);

        mSocView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mSocView, items[3].first, items[3].second, wxEXPAND);

        // PACK SOCIT
        mPackTempText = CreateTextHeader(this, "PACK TEMP", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mPackTempText, items[1].first, items[1].second, wxEXPAND);
        
        mPackTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mPackTempView, items[4].first, items[4].second, wxEXPAND);

        // SHUTDOWN
        mShutdownText = CreateTextHeader(this, "SHUTDOWN", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mShutdownText, items[2].first, items[2].second, wxEXPAND);

        mShutdownView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mShutdownView, items[5].first, items[5].second, wxEXPAND);

        // MC TEMP
        mMcTempText = CreateTextHeader(this, "MC TEMP", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mMcTempText, items[6].first, items[6].second, wxEXPAND);

        mMcTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mMcTempView, items[9].first, items[9].second, wxEXPAND);

        // MOTOR TEMP
        mMotorTempText = CreateTextHeader(this, "MOTOR TEMP", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mMotorTempText, items[7].first, items[7].second, wxEXPAND);

        mMotorTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mMotorTempView, items[10].first, items[10].second, wxEXPAND);

        // MC STATE
        mMcStateText = CreateTextHeader(this, "MC STATE", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mMcStateText, items[8].first, items[8].second, wxEXPAND);

        mMcStateView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mMcStateView, items[11].first, items[11].second, wxEXPAND);

        // VCU STATE
        mVcuStateText = CreateTextHeader(this, "STATE", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mVcuStateText, items[12].first, items[12].second, wxEXPAND);

        mVcuStateView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mVcuStateView, items[15].first, items[9].second, wxEXPAND);

        // GLV V
        mGlvVoltText = CreateTextHeader(this, "GLV V", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mGlvVoltText, items[13].first, items[13].second, wxEXPAND);

        mGlvVoltView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mGlvVoltView, items[16].first, items[16].second, wxEXPAND);

        // DEBUG
        // NOTE: you don't currently use the free slot for anything.
        // If you'd like to add something, then just update the code in the handler callbacks.
        mDebugText = CreateTextHeader(this, "DEBUG (TEST)", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mDebugText, items[14].first, items[14].second, wxEXPAND);

        mDebugView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, whiteColor, mainWnd, 4.0f);
        sizer->Add(mDebugView, items[17].first, items[17].second, wxEXPAND);

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

        const int overallMarginHz = FromDIP(200);
        mMainSizer->Add(this, 1, wxEXPAND | wxALL, margin);
        //mMainSizer->Add(this, 1, wxEXPAND | wxLEFT | wxRIGHT, overallMarginHz);

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
            }
        }
        else if (msg.Name() == "PEI_Diagnostic_BMS_Data")
        {
            mPackTempView->SetLabel(std::to_string(sigMap["HI_Temp"].second) + "C");
            mSocView->SetLabel(std::to_string(sigMap["SOC"].second) + "%");
        }
        else if (msg.Name() == "PEI_Status")
        {
            std::string shutdown = "NO_SHUTDOWN";
            auto isState = [&sigMap](const std::string& state) { return sigMap.find(state) != sigMap.end() && sigMap[state].second == 0.0; };
            if (isState("PRECHARGE")) shutdown = "PRECHARGE";
            else if (isState("AIR_NEG")) shutdown = "AIR_NEG";
            else if (isState("AIR_POS")) shutdown = "AIR_POS";
            else if (isState("BMS_OK")) shutdown = "BMS_OK";
            else if (isState("IMD_OK")) shutdown = "IMD_OK";
            else if (isState("SHUTDOWN_FINAL")) shutdown = "SHUTDOWN_FINAL";
            mShutdownView->SetLabel(shutdown);
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
            mMcTempView->SetLabel(std::to_string(mcTemp) + "C");
        }
        else if (msg.Name() == "M162_Temperature_Set_3")
        {
            mMotorTempView->SetLabel(std::to_string(sigMap["INV_Motor_Temp"].second) + "C");
        }
        else if (msg.Name() == "M169_Internal_Voltages") // Duplicated in original code???
        {
            std::ostringstream str;
            str << std::fixed << std::setprecision(2) << sigMap["INV_Ref_Voltage_12_0"].second;
            mGlvVoltView->SetLabel(str.str());
        }
        else if (msg.Name() == "M169_Internal_Voltages")
        {
            std::ostringstream str;
            str << std::fixed << std::setprecision(2) << sigMap["INV_Ref_Voltage_12_0"].second;
            mGlvVoltView->SetLabel(str.str());
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
