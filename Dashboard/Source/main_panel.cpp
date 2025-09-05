#include "main_panel.h"

#include <sstream>
#include <iomanip>

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
    std::unordered_map<std::string, wxColor> MainPanel::sValidVcuStateColors =
    {
        { "LV", gLawnGreen },
        { "PRECHARGE", gLawnGreen },
        { "HV_ENABLED", gLawnGreen },
        { "DRIVE", gLawnGreen },
        { "STARTUP", gLawnGreen },
        { "BSPD_TRIPD", gYellow },
        { "UNCALIBRTD", gYellow },
    };

    MainPanel::MainPanel(MainWindow* mainWnd, Telem& telem)
        : wxPanel(mainWnd, wxID_ANY)
        , mMainSizer(new wxBoxSizer(wxVERTICAL))
        , mMainWindow(mainWnd)
    {
        const int margin = FromDIP(20);
        const int marginHz = FromDIP(40);

        const wxColor blackColor = wxColor(10, 10, 10);
        const wxColor labelBgrColor = blackColor; //wxColor(100, 100, 100);
        const wxColor labelColor = wxColor(255, 255, 100);
        
        SetBackgroundColour(blackColor);

        auto sizer = new wxGridBagSizer(margin, marginHz);
                
        std::vector<std::pair<wxGBPosition, wxGBSpan>> items =
        {
            {{0, 0}, {1, 1}},
            {{0, 1}, {1, 1}},
            {{1, 0}, {2, 1}},
            {{1, 1}, {1, 1}},
            {{2, 1}, {1, 1}},

            {{3, 0}, {1, 1}},
            {{3, 1}, {1, 1}},
            {{4, 0}, {2, 1}},
            {{4, 1}, {2, 1}},
        };

        // MPH
        mMphText = CreateTextHeader(this, "MPH", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mMphText, items[0].first, items[0].second, wxEXPAND);

        mMphView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 7.0f);
        sizer->Add(mMphView, items[2].first, items[2].second, wxEXPAND);

        // PACK SOCIT
        mPackSocitText = CreateTextHeader(this, "PACK SOCIT", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mPackSocitText, items[1].first, items[1].second, wxEXPAND);

        mSocView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 4.0f);
        sizer->Add(mSocView, items[3].first, items[3].second, wxEXPAND);

        mTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 4.0f);
        sizer->Add(mTempView, items[4].first, items[4].second, wxEXPAND);

        // STATE
        mStateText = CreateTextHeader(this, "STATE", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mStateText, items[5].first, items[5].second, wxEXPAND);

        mStateView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 4.0f);
        sizer->Add(mStateView, items[7].first, items[7].second, wxEXPAND);

        // GLV VOLTAGE
        mGlvVoltageText = CreateTextHeader(this, "GLV V", sizer->GetEmptyCellSize(), labelColor, labelBgrColor, mainWnd, 2.0f);
        sizer->Add(mGlvVoltageText, items[6].first, items[6].second, wxEXPAND);

        mGlvVoltageView = CreateTextView(this, "", sizer->GetEmptyCellSize(), blackColor, gDodgerBlue, mainWnd, 4.0f);
        sizer->Add(mGlvVoltageView, items[8].first, items[8].second, wxEXPAND);

        sizer->AddGrowableRow(0, 1);
        sizer->AddGrowableRow(1, 3);
        sizer->AddGrowableRow(2, 3);
        sizer->AddGrowableRow(3, 1);
        sizer->AddGrowableRow(4, 3);
        sizer->AddGrowableRow(5, 3);

        sizer->AddGrowableCol(0);
        sizer->AddGrowableCol(1);

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

    void MainPanel::UpdateState(std::string vcuState, std::string bmsState)
    {
        // BMS faults over VCU
        std::string resState;
        wxColor resColor = gRed;

        if (vcuState == mVcuState && bmsState == mBmsState)
        {
            if (mBmsError || mVcuError)
            {
                const auto now = std::chrono::system_clock::now();
                std::chrono::duration<double> dur = now - mErrorTimestamp;
                if (dur.count() >= 3.0)
                {
                    // Hide error window
                }
            }
            return;
        }

        mVcuState = vcuState;
        mBmsState = bmsState;
        if (bmsState != "NO_ERROR" && !bmsState.empty())
        {
            resState = (std::atoi(bmsState.c_str()) != 0 ? "BMSINT?" : bmsState);
            mErrorTimestamp = std::chrono::system_clock::now();
            mBmsError = true;
        }
        else
        {
            mBmsError = false;
            resState = vcuState;
            if (std::atoi(vcuState.c_str()) != 0)
            {
                resState = "VCUINT?";
                mVcuError = true;
            }
            else if (sValidVcuStateColors.find(vcuState) == sValidVcuStateColors.end())
            {
                mErrorTimestamp = std::chrono::system_clock::now();
                mVcuError = true;
            }
            else
            {
                resColor = sValidVcuStateColors[vcuState];
            }
        }

        mStateView->SetLabel(resState);
        mStateView->SetBackgroundColour(resColor);
    }

    void MainPanel::UpdateTemp(double motorTemp, double mcTemp, double packTemp, double soc)
    {
        mMotorTemp = motorTemp;
        mMcTemp = mcTemp;
        mPackTemp = packTemp;
        mSoc = soc;

        mSocView->SetLabel(std::to_string((int32_t)std::round(mSoc)));

        double maxTemp = mMotorTemp;
        wxColor resColor = mMotorTemp < 45 ? gLawnGreen : (mMotorTemp < 50 ? gYellow : gOrangeRed);

        if (mMcTemp > maxTemp)
        {
            maxTemp = mMcTemp;
            resColor = mMcTemp < 45 ? gLawnGreen : (mMcTemp < 50 ? gYellow : gOrangeRed);
        }

        if (mPackTemp > maxTemp)
        {
            maxTemp = mPackTemp;
            resColor = mPackTemp <= 30 ? gLawnGreen :
                (mMcTemp <= 40 ? gYellow : 
                (mMcTemp <= 50 ? gOrange : gOrangeRed));
        }

        std::ostringstream str;
        str << ((int32_t)std::round(maxTemp)) << 'C';

        mTempView->SetLabel(str.str());
        mTempView->SetBackgroundColour(resColor);
    }

    void MainPanel::UpdateSpeed(double speedRpm)
    {
        mSpeedRpm = speedRpm;

        constexpr double circumference = 50.2655; // Radius = 8in
        double speedMph = mSpeedRpm * circumference * 60.0 / 63360.0;

        mMphView->SetLabel(std::to_string((int32_t)std::round(speedMph)));
    }

    void MainPanel::UpdateGlv(double glvVoltage)
    {
        mGlvVoltage = glvVoltage;

        wxColor resColor;
        if (mGlvVoltage > 10.0)
            resColor = gLawnGreen;
        else if (mGlvVoltage > 9.0)
            resColor = gYellow;
        else
            resColor = gOrangeRed;

        std::ostringstream str;
        str << std::fixed << std::setprecision(2) << mGlvVoltage;
        mGlvVoltageView->SetLabel(str.str());
        mGlvVoltageView->SetBackgroundColour(resColor);
    }

    void MainPanel::OnFeCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
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
            auto [sig, stateNum] = sigMap["State"];
            if (auto state = GetStringEncoding(*sig, static_cast<int64_t>(stateNum));
                state.has_value())
            {
                UpdateState(state.value(), mBmsState);
            }

            // Throttle2
            mThrottle2 = sigMap["Throttle2_Level"].second;
        }
        else if (msg.Name() == "PEI_BMS_Status")
        {
            auto [sig, stateNum] = sigMap["PEI_BMS_Status"];
            if (auto state = GetStringEncoding(*sig, static_cast<int64_t>(stateNum));
                state.has_value())
            {
                UpdateState(mVcuState, state.value());
            }
        }
        else if (msg.Name() == "PEI_Diagnostic_BMS_Data")
        {
            UpdateTemp(mMotorTemp, mMcTemp, sigMap["HI_Temp"].second, sigMap["SOC"].second);
        }
        else if (msg.Name() == "Dashboard_Random_Shit")
        {
            UpdateSpeed(sigMap["Front_Wheel_Speed"].second);
        }
        else if (msg.Name() == "Dashboard_Knobs")
        {
            // TODO: Maybe make MainWindow an observer?
            mMainWindow->SetMode(sigMap["Button"].second);
        }
        else if (msg.Name() == "PEI_Status")
        {
            auto isState = [&sigMap](const std::string& state) { return sigMap.find(state) != sigMap.end() && sigMap[state].second == 0.0; };
            if (isState("PRECHARGE")) mShutdown = "PRECHARGE";
            else if (isState("AIR_NEG")) mShutdown = "AIR_NEG";
            else if (isState("AIR_POS")) mShutdown = "AIR_POS";
            else if (isState("BMS_OK")) mShutdown = "BMS_OK";
            else if (isState("IMD_OK")) mShutdown = "IMD_OK";
            else if (isState("SHUTDOWN_FINAL")) mShutdown = "SHUTDOWN_FINAL";
            else mShutdown = "NO_SHUTDOWN";
        }
#endif
    }
    
    void MainPanel::OnMcCan(const dbcppp::IMessage& msg, const dbcppp::INetwork& net, const can_frame& frame)
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
            UpdateTemp(mMotorTemp, mcTemp, mPackTemp, mSoc);
        }
        else if (msg.Name() == "M162_Temperature_Set_3")
        {
            UpdateTemp(sigMap["INV_Motor_Temp"].second, mMcTemp, mPackTemp, mSoc);
        }
        else if (msg.Name() == "M169_Internal_Voltages")
        {
            UpdateGlv(sigMap["INV_Ref_Voltage_12_0"].second);
        }
        else if (msg.Name() == "M169_Internal_Voltages")
        {
            UpdateGlv(sigMap["INV_Ref_Voltage_12_0"].second);
        }
        else if (msg.Name() == "M171_Fault_Codes")
        {
            if ((sigMap["INV_Post_Fault_Lo"].second != 0.0) && (sigMap["INV_Post_Fault_Hi"].second != 0.0))
            {
                // TODO: test if you need uint32 cast first
            }
        }
        else if (msg.Name() == "M165_Motor_Position_Info")
        {
            mMotorSpeed = sigMap["INV_Motor_Speed"].second;
        }
        else if (msg.Name() == "M172_Torque_And_Timer_Info")
        {
            mTorqueFeedback = sigMap["INV_Torque_Feedback"].second;
        }
#endif
    }
}