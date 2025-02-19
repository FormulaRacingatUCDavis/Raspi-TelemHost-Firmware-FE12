# FE12 Dashboard
# Display data received from Raspberry Pi telemetry host

import tkinter as tk

class Dashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("FE12 Dashboard")
        self.master.configure(bg="black")
        self.master.geometry("1980x1080")

        self.dashboard = tk.Frame(self.master, bg="black")
        self.dashboard.pack(fill="both", expand=True, pady=20)

        self.dashboard.grid_rowconfigure(0, weight=4, uniform="equal")  # Header

        self.dashboard.grid_rowconfigure(1, weight=10, uniform="equal") 
        self.dashboard.grid_rowconfigure(2, weight=10, uniform="equal")

        self.dashboard.grid_rowconfigure(3, weight=4, uniform="equal")  # Header
        self.dashboard.grid_rowconfigure(4, weight=10, uniform="equal")

        self.dashboard.grid_columnconfigure(0, weight=10, uniform="equal")
        self.dashboard.grid_columnconfigure(1, weight=10, uniform="equal")

        self.padxOut = 100
        self.padxIn = 50

        self.createWidgets()

    def createWidgets(self):
        # Speed
        self.headerSpeed = tk.Label(self.dashboard, text=f"MPH", font=("Trebuchet MS", 40), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerSpeed.grid(row=0, column=0, sticky="nsew", padx=(self.padxOut,self.padxIn))
        self.lblSpeed = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 150), bg="#ac75d9", fg="black", anchor="center", padx=5, pady=5)
        self.lblSpeed.grid(row=1, column=0, sticky="nsew", rowspan=2, padx=(self.padxOut,self.padxIn))

        # Vehicle state
        self.headerState = tk.Label(self.dashboard, text=f"STATE:", font=("Trebuchet MS", 40), bg="black", fg="yellow", anchor="w", pady=5)
        self.headerState.grid(row=3, column=0, sticky="nsew", padx=(self.padxOut,self.padxIn))
        self.lblState = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 70), bg="yellow", fg="black", anchor="center", padx=5, pady=5)
        self.lblState.grid(row=4, column=0, sticky="nsew", padx=(self.padxOut,self.padxIn))

        FE_green = "#20e848"

        # GLV Voltage
        self.dashboard.grid_columnconfigure(0, weight=10, uniform="equal")
        self.dashboard.grid_rowconfigure(0, weight=3, uniform="equal")
        self.dashboard.grid_rowconfigure(1, weight=10, uniform="equal")

        self.headerVoltage = tk.Label(self.dashboard, text=f"GLV V", font=("Trebuchet MS", 40), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerVoltage.grid(row=3, column=1, sticky="nsew", padx=(self.padxIn, self.padxOut))
        self.lblVoltage = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 100), bg=FE_green, fg="black", anchor="center", padx=5, pady=5)
        self.lblVoltage.grid(row=4, column=1, sticky="nsew", padx=(self.padxIn, self.padxOut))

        self.dashboard.grid_columnconfigure(0, weight=10, uniform="equal")
        self.dashboard.grid_rowconfigure(0, weight=3, uniform="equal")
        self.dashboard.grid_rowconfigure(1, weight=10, uniform="equal")
        # State of Charge
        self.headerSoC = tk.Label(self.dashboard, text=f"PACK SOCIT", font=("Trebuchet MS", 40), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerSoC.grid(row=0, column=1, sticky="nsew", padx=(self.padxIn, self.padxOut))
        self.lblSoC = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 100), bg="red", fg="black", anchor="center", padx=5, pady=5)
        # Temperature
        self.lblSoC.grid(row=1, column=1, sticky="nsew", padx=(self.padxIn, self.padxOut), pady=(0, 20))
        self.lblTemp = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 100), bg=FE_green, fg="black", anchor="center", padx=5, pady=5)
        self.lblTemp.grid(row=2, column=1, sticky="nsew", padx=(self.padxIn, self.padxOut))

    def updateDashboard(self, speed, state, voltage, soc, motorTemp, motorCtrlTemp, batteryTemp):

        txtSpeed = str(round(speed))
        txtState = state                    # Ask how state is determined
        txtVoltage = f"{(voltage):.2f}"
        txtSoC = f"{round(soc)}%"
        txtTemp = f"{round(max(motorTemp, motorCtrlTemp, batteryTemp))}C" # Display highest temperature of motor, motor controller, battery

        self.lblSpeed.config(text=txtSpeed)
        self.lblState.config(text=txtState)
        self.lblVoltage.config(text=txtVoltage)
        self.lblSoC.config(text=txtSoC)
        self.lblTemp.config(text=txtTemp)

root = tk.Tk()
dashboard = Dashboard(root)

dashboard.updateDashboard(58.39, "CALIBRATED", 24.25132, 25.353, 54.35, 24.43, 100.39) # Test input

root.mainloop()
