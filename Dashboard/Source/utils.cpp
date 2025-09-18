#include "utils.h"

#include "main_window.h"

namespace frucd
{
    wxStaticText* CreateTextHeader
    (
        wxWindow* parent,
        std::string_view title,
        wxSize size,
        MainWindow* wnd,
        float fontScale
    )
    {
        auto panel = new wxPanel(parent);
        panel->SetMaxSize(size);

        auto sizer = new wxBoxSizer(wxVERTICAL);

        auto text = new wxStaticText(
            panel,
            wxID_ANY,
            title.data(),
            wxDefaultPosition,
            wxDefaultSize,
            wxALIGN_CENTER_HORIZONTAL | wxST_NO_AUTORESIZE
        );

        wxFont font(wxFontInfo(int(10 * fontScale))
                        .Family(wxFONTFAMILY_DEFAULT)
                        .Weight(wxFONTWEIGHT_BOLD));
        text->SetFont(font);
        text->SetForegroundColour(wxColour(255, 255, 100));

        sizer->AddStretchSpacer(1);
        sizer->Add(text, 0, wxALIGN_CENTER);
        sizer->AddStretchSpacer(1);

        panel->SetSizer(sizer);

        return text;
    }

    wxStaticText* CreateTextView
    (
        wxWindow* parent,
        std::string_view defaultText,
        wxSize size,
        MainWindow* wnd,
        float fontScale
    )
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

        wxFont font(wxFontInfo(int(10 * fontScale))
                        .Family(wxFONTFAMILY_DEFAULT)
                        .Weight(wxFONTWEIGHT_BOLD));
        text->SetFont(font);
        text->SetForegroundColour(wxColor(0, 0, 0));

        sizer->AddStretchSpacer(1);
        sizer->Add(text, 0, wxALIGN_CENTER);
        sizer->AddStretchSpacer(1);

        panel->SetSizer(sizer);
        panel->SetMaxSize(size);

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