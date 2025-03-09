#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

# FE12 Dashboard
# Display data received from Raspberry Pi telemetry host
# Note: GUI currently does NOT display until it receives CAN data

import tkinter as tk
from canManager import FE12CANBus

class FE12Dashboard:
    def __init__(self, master, channel, interface):
        self.canbus = FE12CANBus(channel, interface)
        
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

        print("Creating widgets...")

        self.createWidgets()

        print("Waiting for CAN messages...")

        self.updateDashboard()

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

    def updateDashboard(self): # Doesn't update until it receives CAN data

        self.canbus.readMsg()

        outputSpeed = str(round(self.canbus.speed))
        outputState = self.canbus.state
        outputVoltage = f"{(self.canbus.glvVoltage):.2f}"
        outputSoC = f"{round(self.canbus.soc)}%"
        outputTemp = f"{round(max(self.canbus.motorTemp, self.canbus.mcTemp, self.canbus.packTemp))}C" # Display highest temperature of motor, motor controller, battery

        self.lblSpeed.config(text=outputSpeed)
        self.lblState.config(text=outputState)
        self.lblVoltage.config(text=outputVoltage)
        self.lblSoC.config(text=outputSoC)
        self.lblTemp.config(text=outputTemp)

        self.master.after(10, self.updateDashboard)

root = tk.Tk()
raspiDashboard = FE12Dashboard(root, 'vcan0', 'socketcan') # Testing using virtual can node

root.mainloop()