#pragma once

#include <wx/wx.h>
#include <wx/simplebook.h>

#include "telem.h"

namespace frucd
{
    class MainPanel;
    class DebugPanel;
    class GaugePanel;

    class MainWindow : public wxFrame
    {
    public:
        MainWindow();

    public:
        void OnUpdateUI(wxUpdateUIEvent& e);
        void OnKeyDown(wxKeyEvent& e);
        void OnKeyUp(wxKeyEvent& e);
        void OnUpdate(wxIdleEvent& e);

        void SetMode(double mode); // TODO: use a cleaner way - this was just the original

    private:
        void ShowMainPanel();
        void ShowDebugPanel();
        void ShowGaugePanel();

    private:
        Telem mTelem;
        MainPanel* mMainPanel;
        DebugPanel* mDebugPanel;
        GaugePanel* mGaugePanel;
        wxSimplebook* mPanelCollection;
        wxSizer* mMainSizer;
    };
}