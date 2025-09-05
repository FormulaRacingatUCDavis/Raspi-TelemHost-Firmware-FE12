#include "utils.h"

#include "main_window.h"

namespace frucd
{
    wxTextCtrl* CreateTextHeader(
        wxWindow* parent,
        std::string_view title,
        wxSize size,
        wxColor fgColor,
        wxColor bgColor,
        MainWindow* wnd,
        float fontScale)
    {
        auto res = new wxTextCtrl(parent, wxID_ANY, title.data(), wxDefaultPosition, size, wxTE_READONLY | wxTE_CENTRE);
        res->SetForegroundColour(fgColor);
        res->SetBackgroundColour(bgColor);
        res->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, wnd);
        res->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, wnd);
        res->SetFont(res->GetFont().Scale(fontScale));
        return res;
    }

    wxStaticText* CreateTextView(
        wxWindow* parent,
        std::string_view defaultText,
        wxSize size,
        wxColor fgColor,
        wxColor bgColor,
        MainWindow* wnd,
        float fontScale)
    {
        auto res = new wxStaticText(parent, wxID_ANY, defaultText.data(), wxDefaultPosition, size, wxALIGN_CENTER_HORIZONTAL | wxST_NO_AUTORESIZE);
        res->SetForegroundColour(fgColor);
        res->SetBackgroundColour(bgColor);
        res->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, wnd);
        res->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, wnd);
        res->SetFont(res->GetFont().Scale(fontScale));
        return res;
    }

    std::optional<std::string> GetStringEncoding(const dbcppp::ISignal& sig, int64_t value)
    {
        auto res = std::find_if(
            sig.ValueEncodingDescriptions().begin(),
            sig.ValueEncodingDescriptions().end(),
            [value](const dbcppp::IValueEncodingDescription& ved) { return ved.Value() == value; });
        return (res != sig.ValueEncodingDescriptions().end()) ? std::optional(res->Description()) : std::nullopt;
    }
}