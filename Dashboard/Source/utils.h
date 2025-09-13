#pragma once

#include <wx/wx.h>
#include <dbcppp/Network.h>
#include <string>
#include <string_view>
#include <optional>

namespace frucd
{
    class MainWindow;

    wxStaticText* CreateTextHeader(
        wxWindow* parent,
        std::string_view title,
        wxSize size,
        wxColor fgColor,
        MainWindow* wnd,
        float fontScale
    );

    wxStaticText* CreateTextView(
        wxWindow* parent,
        std::string_view defaultText,
        wxSize size,
        wxColour fgColor,
        MainWindow* wnd,
        float fontScale);
    
    std::optional<std::string> GetStringEncoding(const dbcppp::ISignal& sig, int64_t value);
}