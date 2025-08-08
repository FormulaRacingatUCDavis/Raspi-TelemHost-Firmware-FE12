#include "display.h"

#include "main_window.h"

namespace frucd
{
    bool Display::OnInit()
    {
        MainWindow* wnd = new MainWindow(); // No leak, managed by wx
        wnd->Show();
        //wnd->ShowFullScreen(true, wxFULLSCREEN_ALL);
        return true;
    }
}