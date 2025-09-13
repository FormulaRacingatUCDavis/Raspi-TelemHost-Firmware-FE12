#include "utils.h"

#include "main_window.h"

namespace frucd
{
    wxStaticText* CreateTextHeader(
        wxWindow* parent,
        std::string_view title,
        wxSize size,
        wxColor fgColor,
        MainWindow* wnd,
        float fontScale)
    {
        auto res = new wxStaticText(
            parent,
            wxID_ANY,
            title.data(),
            wxDefaultPosition,
            wxDefaultSize,
            wxALIGN_CENTER_HORIZONTAL
        );

        res->SetForegroundColour(fgColor);
        res->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, wnd);
        res->Bind(wxEVT_KEY_DOWN, &MainWindow::OnKeyDown, wnd);

        wxFont font(wxFontInfo(int(10 * fontScale))
                        .Family(wxFONTFAMILY_DEFAULT)
                        .Weight(wxFONTWEIGHT_BOLD));
        res->SetFont(font);

        return res;
    }

    wxStaticText* CreateTextView(
        wxWindow* parent,
        std::string_view defaultText,
        wxSize size,
        wxColour fgColor,
        MainWindow* wnd,
        float fontScale)
    {
        auto panel = new wxPanel(parent);
        panel->SetBackgroundColour(wxColor(255, 255, 255));

        auto sizer = new wxBoxSizer(wxVERTICAL);

        auto text = new wxStaticText(
            panel,
            wxID_ANY,
            defaultText.data(),
            wxDefaultPosition,
            wxDefaultSize,
            wxALIGN_CENTER_HORIZONTAL
        );
        text->SetForegroundColour(fgColor);

        wxFont font(wxFontInfo(int(10 * fontScale))
                        .Family(wxFONTFAMILY_DEFAULT)
                        .Weight(wxFONTWEIGHT_BOLD));
        text->SetFont(font);

        sizer->AddStretchSpacer(1);
        sizer->Add(text, 0, wxALIGN_CENTER);
        sizer->AddStretchSpacer(1);

        panel->SetSizer(sizer);

        return text;
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