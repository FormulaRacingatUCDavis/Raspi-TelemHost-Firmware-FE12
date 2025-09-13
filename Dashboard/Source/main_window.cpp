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
        mPanelCollection->AddPage(mMainPanel, "Main");
        mPanelCollection->AddPage(mDebugPanel, "Debug");
        mPanelCollection->AddPage(mGaugePanel, "Gauge");

        Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);

        Bind(wxEVT_CHAR_HOOK, &MainWindow::OnKeyCharHook, this);

        mMainSizer->Add(mPanelCollection, 1, wxEXPAND | wxALL, 0);
        SetSizerAndFit(mMainSizer);

        ShowMainPanel();
        // ShowDebugPanel();
        ShowFullScreen(true);
    }

    void MainWindow::OnUpdateUI(wxUpdateUIEvent& e)
    {
    }

    void MainWindow::OnUpdate(wxIdleEvent& e)
    {
#if FRUCD_SHOW_FPS
        static int fps = 0;
        static auto startTime = std::chrono::high_resolution_clock::now();
#endif

        mTelem.Log();

        switch (mPanelCollection->GetSelection())
        {
            case 0: mMainPanel->Update(); break;
            case 1: mDebugPanel->Update(); break;
            case 2: mGaugePanel->Update(); break;
        }

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

    void MainWindow::OnKeyCharHook(wxKeyEvent& e)
    {
        switch (e.GetKeyCode())
        {
            case WXK_ESCAPE:
                Close(true);
                break;

            case WXK_UP:
                if (mPanelCollection->GetSelection() == 1)
                    ShowMainPanel();
                else
                    ShowDebugPanel();
                break;

            case WXK_DOWN:
                ShowGaugePanel();
                break;

            case WXK_LEFT:
                ShowMainPanel();
                break;

            default:
                e.Skip();
                break;
        }
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
    }

    void MainWindow::ShowDebugPanel()
    {
        mPanelCollection->ChangeSelection(1);
        SetBackgroundColour(mDebugPanel->GetBackgroundColour());
    }

    void MainWindow::ShowGaugePanel()
    {
        mPanelCollection->ChangeSelection(2);
        SetBackgroundColour(mGaugePanel->GetBackgroundColour());
    }
}