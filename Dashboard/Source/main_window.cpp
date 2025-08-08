#include "main_window.h"

namespace frucd
{
    MainWindow::MainWindow()
        : wxFrame(nullptr, wxID_ANY, "FE13 Dashboard")
        , mMainPanel(new wxPanel(this))
        , mTelem()
    {
        mMainPanel->SetBackgroundColour(wxColor(18, 18, 18));
        
        mMainPanel->Bind(wxEVT_KEY_UP, &MainWindow::OnKeyUp, this);
        mMainPanel->Bind(wxEVT_UPDATE_UI, &MainWindow::OnUpdateUI, this);
        mMainPanel->Bind(wxEVT_IDLE, &MainWindow::OnUpdate, this);
    }

    void MainWindow::OnUpdateUI(wxUpdateUIEvent& e)
    {
    }

    void MainWindow::OnKeyUp(wxKeyEvent& e)
    {
        std::cerr << e.GetKeyCode() << std::endl;

        if (e.GetKeyCode() == WXK_ESCAPE)
        {
            Close(true);
        }
        else
        {
            e.Skip(false);
        }
    }

    static int fps = 0;

    void MainWindow::OnUpdate(wxIdleEvent& e)
    {
        // https://github.com/Overv/VulkanTutorial/blob/main/en/05_Uniform_buffers/00_Descriptor_set_layout_and_buffer.md
        static auto startTime = std::chrono::high_resolution_clock::now();
        static auto lastTime = std::chrono::high_resolution_clock::now();
        fps++;
        
        auto currentTime = std::chrono::high_resolution_clock::now();
        if (float time = std::chrono::duration<float, std::chrono::seconds::period>(currentTime - startTime).count();
            time >= 1.0f)
        {
            std::cerr << "FPS: " << fps << std::endl;
            fps = 0;
            startTime = currentTime;
        }
        e.RequestMore(); // Used as an "update method"
    }
}