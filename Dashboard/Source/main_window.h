#pragma once

#include <wx/wx.h>

#include "telem.h"

namespace frucd
{
    class MainWindow : public wxFrame
    {
    public:
        MainWindow();

    private:
        void OnUpdateUI(wxUpdateUIEvent& e);
        void OnKeyUp(wxKeyEvent& e);
        void OnUpdate(wxIdleEvent& e);

    private:
        wxPanel* mMainPanel;
        Telem mTelem;
    };
}