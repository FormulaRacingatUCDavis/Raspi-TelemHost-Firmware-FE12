#pragma once

#include <wx/wx.h>

namespace frucd
{
    class Display : public wxApp
    {
    public:
        bool OnInit() override;
    };
}