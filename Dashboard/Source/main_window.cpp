#include "main_window.h"

#include <wx/grid.h>
#include <wx/gbsizer.h>

#include "main_panel.h"
#include "debug_panel.h"
#include "gauge_panel.h"

#define FRUCD_CALC_FPS 0

namespace frucd
{
    MainWindow::MainWindow()
        : wxFrame(nullptr, wxID_ANY, "FE13 Dashboard")
        , mTelem()
        , mMainPanel(new MainPanel(this, mTelem))
        , mDebugPanel(new DebugPanel(this, mTelem))
        , mGaugePanel(new GaugePanel(this, mTelem))
        , mPanelCollection(new wxSimplebook(this))
        , mMainSizer(new wxBoxSizer(wxVERTICAL))
    {
        const int margin = 0;
        mPanelCollection->AddPage(mMainPanel, "Main");
        mPanelCollection->AddPage(mDebugPanel, "Debug");
        mPanelCollection->AddPage(mGaugePanel, "Gauge");

        mPanelCollection->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, this);
        mPanelCollection->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, this);
        mPanelCollection->Bind(wxEVT_UPDATE_UI, &MainWindow::OnUpdateUI, this);
        mPanelCollection->Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);

        mMainSizer->Add(mPanelCollection, 1, wxEXPAND | wxALL, margin);
        SetSizerAndFit(mMainSizer);

        ShowMainPanel();

        mMainPanel->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, this);
        mMainPanel->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, this);
        mMainPanel->Bind(wxEVT_UPDATE_UI, &MainWindow::OnUpdateUI, this);
        mMainPanel->Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);

        mDebugPanel->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, this);
        mDebugPanel->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, this);
        mDebugPanel->Bind(wxEVT_UPDATE_UI, &MainWindow::OnUpdateUI, this);
        mDebugPanel->Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);

        mGaugePanel->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, this);
        mGaugePanel->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, this);
        mGaugePanel->Bind(wxEVT_UPDATE_UI, &MainWindow::OnUpdateUI, this);
        mGaugePanel->Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);

        ShowFullScreen(true);
    }

    void MainWindow::OnUpdateUI(wxUpdateUIEvent& e)
    {
    }

    void MainWindow::OnKeyDown(wxKeyEvent& e)
    {
        if (e.GetKeyCode() == WXK_UP)
        {
            ShowDebugPanel();
        }
        else
        {
            e.Skip(false);
        }
    }

    void MainWindow::OnKeyUp(wxKeyEvent& e)
    {
        if (e.GetKeyCode() == WXK_ESCAPE)
        {
            Close(true);
        }
        else if (e.GetKeyCode() == WXK_UP)
        {
            ShowMainPanel();
        }
        else
        {
            e.Skip(false);
        }
    }

    
    void MainWindow::OnUpdate(wxIdleEvent& e)
    {
        // https://github.com/Overv/VulkanTutorial/blob/main/en/05_Uniform_buffers/00_Descriptor_set_layout_and_buffer.md
#if FRUCD_SHOW_FPS
        static int fps = 0;
        static auto startTime = std::chrono::high_resolution_clock::now();
        static auto lastTime = std::chrono::high_resolution_clock::now();
        static double osc = 0.01;
#endif

        mTelem.Log();
        mGaugePanel->Update();

#if FRUCD_SHOW_FPS
        fps++;
        
        auto currentTime = std::chrono::high_resolution_clock::now();
        if (float time = std::chrono::duration<float, std::chrono::seconds::period>(currentTime - startTime).count();
            time >= 1.0f)
        {
            std::cerr << "FPS: " << fps << std::endl;
            fps = 0;
            startTime = currentTime;
        }
#endif
        e.RequestMore(); // Used as an "update method"
    }

    void MainWindow::SetMode(double mode)
    {
        if (mode == 0.0)
            ShowMainPanel();
        else if (mode == 1.0)
            ShowDebugPanel();
        else if (mode == 2.0)
            ShowGaugePanel();
    }

    void MainWindow::ShowMainPanel()
    {
        mPanelCollection->ChangeSelection(0);
        SetBackgroundColour(mMainPanel->GetBackgroundColour());
        mMainPanel->SetClientSize(wxDefaultSize);
        mDebugPanel->SetClientSize(wxSize(0, 0));
        mGaugePanel->SetClientSize(wxSize(0, 0));
    }

    void MainWindow::ShowDebugPanel()
    {
        mPanelCollection->ChangeSelection(1);
        SetBackgroundColour(mDebugPanel->GetBackgroundColour());
        mMainPanel->SetClientSize(wxSize(0, 0));
        mDebugPanel->SetClientSize(wxDefaultSize);
        mGaugePanel->SetClientSize(wxSize(0, 0));
    }

    void MainWindow::ShowGaugePanel()
    {
        mPanelCollection->ChangeSelection(2);
        SetBackgroundColour(mGaugePanel->GetBackgroundColour());
        mMainPanel->SetClientSize(wxSize(0, 0));
        mDebugPanel->SetClientSize(wxSize(0, 0));
        mGaugePanel->SetClientSize(wxDefaultSize);
    }
}