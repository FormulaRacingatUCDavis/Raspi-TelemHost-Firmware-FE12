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

        const float tFontScale = 2.5f;
        const float vFontScale = 3.0f;
        
        SetBackgroundColour(wxColor(0, 0, 0));

        auto sizer = new wxGridBagSizer(FromDIP(20), FromDIP(40));

        /*
        Grid:
            MPH         SOC
            MPH VIEW    SOC VIEW
            MPH VIEW    TEMP VIEW
            STATE       GLV
            STATE VIEW  GLV VIEW
        */

        // MPH
        mMphText = CreateTextHeader(this, "MPH", sizer->GetEmptyCellSize(), mainWnd, tFontScale);
        sizer->Add(mMphText->GetParent(), wxGBPosition(0, 0), wxGBSpan(1, 1), wxEXPAND);

        mMphView = CreateTextView(this, "", sizer->GetEmptyCellSize(), mainWnd, 7.0f);
        sizer->Add(mMphView->GetParent(), wxGBPosition(1, 0), wxGBSpan(2, 1), wxEXPAND);

        // SOC + TEMP
        mPackSocitText = CreateTextHeader(this, "PACK SOCIT", sizer->GetEmptyCellSize(), mainWnd, tFontScale);
        sizer->Add(mPackSocitText->GetParent(), wxGBPosition(0, 1), wxGBSpan(1, 1), wxEXPAND);

        mSocView = CreateTextView(this, "", sizer->GetEmptyCellSize(), mainWnd, vFontScale);
        sizer->Add(mSocView->GetParent(), wxGBPosition(1, 1), wxGBSpan(1, 1), wxEXPAND);

        mTempView = CreateTextView(this, "", sizer->GetEmptyCellSize(), mainWnd, vFontScale);
        sizer->Add(mTempView->GetParent(), wxGBPosition(2, 1), wxGBSpan(1, 1), wxEXPAND);

        // STATE
        mStateText = CreateTextHeader(this, "STATE", sizer->GetEmptyCellSize(), mainWnd, tFontScale);
        sizer->Add(mStateText->GetParent(), wxGBPosition(3, 0), wxGBSpan(1, 1), wxEXPAND);

        mStateView = CreateTextView(this, "STARTUP", sizer->GetEmptyCellSize(), mainWnd, vFontScale);
        sizer->Add(mStateView->GetParent(), wxGBPosition(4, 0), wxGBSpan(2, 1), wxEXPAND);

        // GLV VOLTAGE
        mGlvVoltageText = CreateTextHeader(this, "GLV V", sizer->GetEmptyCellSize(), mainWnd, tFontScale);
        sizer->Add(mGlvVoltageText->GetParent(), wxGBPosition(3, 1), wxGBSpan(1, 1), wxEXPAND);

        mGlvVoltageView = CreateTextView(this, "", sizer->GetEmptyCellSize(), mainWnd, vFontScale);
        sizer->Add(mGlvVoltageView->GetParent(), wxGBPosition(4, 1), wxGBSpan(2, 1), wxEXPAND);

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

        mMainSizer->Add(this, 1, wxEXPAND);

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
        wxColor resColor = gOrangeRed;

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
        mStateView->GetParent()->Layout();
        mStateView->GetParent()->SetBackgroundColour(resColor);
    }

    void MainPanel::UpdateTemp(double motorTemp, double mcTemp, double packTemp, double soc)
    {
        mMotorTemp = motorTemp;
        mMcTemp = mcTemp;
        mPackTemp = packTemp;
        mSoc = soc;

        mSocView->SetLabel(std::to_string((int32_t)std::round(mSoc)));
        mSocView->GetParent()->Layout();
        mSocView->GetParent()->SetBackgroundColour(gOrangeRed);

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
        mTempView->GetParent()->Layout();
        mTempView->GetParent()->SetBackgroundColour(resColor);
    }

    void MainPanel::UpdateSpeed(double speedRpm)
    {
        mSpeedRpm = speedRpm;

        constexpr double circumference = 50.2655; // Radius = 8in
        double speedMph = mSpeedRpm * circumference * 60.0 / 63360.0;

        mMphView->SetLabel(std::to_string((int32_t)std::round(speedMph)));
        mMphView->GetParent()->Layout();
        mMphView->GetParent()->SetBackgroundColour(gDodgerBlue);
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
        mGlvVoltageView->GetParent()->Layout();
        mGlvVoltageView->GetParent()->SetBackgroundColour(resColor);
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
        else if (msg.Name() == "Dashboard_Inputs")
        {
            if (sigMap["DISPLAY_MODE"].second == 0.0)
                mMainWindow->SetMode(0.0);
            else if (sigMap["DISPLAY_MODE"].second == 1.0)
                mMainWindow->SetMode(1.0);
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