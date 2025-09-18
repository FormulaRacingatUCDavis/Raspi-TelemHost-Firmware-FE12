#include "display.h"

#include "main_window.h"

namespace frucd
{
    bool Display::OnInit()
    {
        MainWindow* wnd = new MainWindow(); // No leak, managed by wx
        //wnd->ShowFullScreen(true, wxFULLSCREEN_ALL);
        wnd->Show();
        return true;
    }
}