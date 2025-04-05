#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

# FE12 Dashboard
# Display data received from Raspberry Pi telemetry host

import tkinter as tk
from canManager import FE12CANBus

class FE12Dashboard:
    def __init__(self, master, channel, interface):

        print("Opening up dashboard...")

        self.canbus = FE12CANBus(channel, interface)
        
        self.master = master
        self.master.title("FE12 Dashboard")
        self.master.configure(bg="black")

        self.dashboard = tk.Frame(self.master, bg="black")
        self.dashboard.pack(fill="both", expand=True, pady=20)

        self.dashboard.grid_rowconfigure(0, weight=5, uniform="equal")  # Header

        self.dashboard.grid_rowconfigure(1, weight=10, uniform="equal") 
        self.dashboard.grid_rowconfigure(2, weight=10, uniform="equal")

        self.dashboard.grid_rowconfigure(3, weight=6, uniform="equal")  # Header
        self.dashboard.grid_rowconfigure(4, weight=20, uniform="equal")
        
        self.dashboard.grid_columnconfigure(0, weight=15, uniform="equal")
        self.dashboard.grid_columnconfigure(1, weight=1, uniform="equal") # Column divider
        self.dashboard.grid_columnconfigure(2, weight=15, uniform="equal")

        self.padxOut = 10

        self.headerFontSize = 20

        self.FE_green = "#20e848"

        self.createWidgets()

        # VCU states

        self.LV = 0x0
        self.PRECHARGE = 0x1
        self.HV = 0x2
        self.DRIVE = 0x3
        self.STARTUP = 0x5
        self.DRIVE_REQUEST_FROM_LV = 0x81
        self.PRECHARGE_TIMEOUT = 0x82
        self.BRAKE_NOT_PRESSED = 0x83
        self.HV_DISABLED_WHILE_DRIVING = 0x84
        self.SENSOR_DISCREPANCY = 0x85
        self.BRAKE_IMPLAUSIBLE = 0x86
        self.SHUTDOWN_CIRCUIT_OPEN = 0x87
        self.UNCALIBRATED = 0x88
        self.HARD_BSPD = 0x89
        self.MC_FAULT = 0x8a

    def createWidgets(self):

        # Speed
        self.headerSpeed = tk.Label(self.dashboard, text=f"MPH", font=("Trebuchet MS", self.headerFontSize), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerSpeed.grid(row=0, column=0, sticky="nsew", padx=(self.padxOut, 0))
        self.lblSpeed = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 75), bg="#ac75d9", fg="black", anchor="center", padx=5, pady=5)
        self.lblSpeed.grid(row=1, column=0, sticky="nsew", rowspan=2, padx=(self.padxOut, 0))

        # Vehicle state
        self.headerState = tk.Label(self.dashboard, text=f"STATE:", font=("Trebuchet MS", self.headerFontSize), bg="black", fg="yellow", anchor="w", pady=5)
        self.headerState.grid(row=3, column=0, sticky="nsew", padx=(self.padxOut, 0))
        self.lblState = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 35), bg="yellow", fg="black", anchor="center", padx=5, pady=5)
        self.lblState.grid(row=4, column=0, sticky="nsew", padx=(self.padxOut, 0))

        # Column Divider
        self.colDivider = tk.Frame(self.dashboard, bg ="black")
        self.colDivider.grid(column= 1, sticky="nsew", rowspan=2)

        # GLV Voltage
        self.headerVoltage = tk.Label(self.dashboard, text=f"GLV V", font=("Trebuchet MS", self.headerFontSize), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerVoltage.grid(row=3, column=2, sticky="nsew", padx=(0, self.padxOut))
        self.lblVoltage = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 50), bg=self.FE_green, fg="black", anchor="center", padx=5, pady=5)
        self.lblVoltage.grid(row=4, column=2, sticky="nsew", padx=(0, self.padxOut))

        # State of Charge
        self.headerSoC = tk.Label(self.dashboard, text=f"PACK SOCIT", font=("Trebuchet MS", self.headerFontSize), bg="black", fg="yellow", anchor="s", padx=5, pady=5)
        self.headerSoC.grid(row=0, column=2, sticky="nsew", padx=(0, self.padxOut))
        self.lblSoC = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 50), bg="red", fg="black", anchor="center", padx=5, pady=5)
        # Temperature
        self.lblSoC.grid(row=1, column=2, sticky="nsew", padx=(0, self.padxOut), pady=(0,5))
        self.lblTemp = tk.Label(self.dashboard, text=f"...", font=("Trebuchet MS", 50), bg=self.FE_green, fg="black", anchor="center", padx=5, pady=5)
        self.lblTemp.grid(row=2, column=2, sticky="nsew", padx=(0, self.padxOut))

    def updateDashboard(self):

        print("Updating dashboard...")

        self.canbus.readMsg()
        
        match self.canbus.canID:
            case '0x500':
                self.updateSpeed()
            case '0x766':
                self.updateState()
            case '0xa9':
                self.updateGLV()
            case '0xa2':
                self.updateTemp()
            case '0xa0':
                self.updateTemp()
            case '0x380':
                self.lblSoC.config(text=f"{round(self.canbus.soc)}%")
                self.updateTemp()

        self.master.after(10, self.updateDashboard)

    def updateState(self):
        bmsStates = {
            '0x4': 'BMS TEMP',
            '0x80': 'SPI FAULT',
            '0x8': 'OVERVOLT',
            '0x10': 'UNDERVOLT',
            '0x20': 'OPEN WIRE',
            '0x40': 'MISMATCH'
        }

        try:
            if hex(self.canbus.bmsState) in bmsStates: # Prioritize BMS faults over VCU faults
                state = bmsStates[hex(self.canbus.vcuState)]
                self.lblState.config(text=state, bg="red")
            else:
                if self.canbus.vcuState & 0x80:
                    match self.canbus.vcuState:
                        # case STARTUP:
                        #     state = 'STARTUP'
                        #     color = 'yellow'
                        case self.DRIVE_REQUEST_FROM_LV:
                            state = 'DRV FRM LV'
                            color = 'red'
                        case self.PRECHARGE_TIMEOUT:
                            state = 'PRE TM OUT'
                            color = 'red'
                        case self.BRAKE_NOT_PRESSED:
                            state = 'BR NOT PRS'
                            color = 'red'
                        case self.HV_DISABLED_WHILE_DRIVING:
                            state = 'HV OFF DRV'
                            color = 'red'


                self.lblState.config(text=state)
        except:
            print(f"Invalid state encoding: {hex(self.canbus.vcuState)}")

    def updateTemp(self):
        # Display highest temperature of motor, motor controller, BMS

        convMotorTemp = self.canbus.motorTemp / 10
        convMcTemp = self.canbus.motorTemp / 10

        maxTemp = max(convMotorTemp, convMcTemp, self.canbus.packTemp)

        # if maxTemp == convMotorTemp or maxTemp == convMcTemp

        self.lblTemp.config(text=f"{round(maxTemp)}C")

    def updateSpeed(self):
        # Slow down speed updates for readability

        wheelRadius = 1302 # double-check
        speedMPH = self.canbus.speed * 60 / wheelRadius # convert from RPM to mph

        self.lblSpeed.config(text=str(round(speedMPH)))

    def updateGLV(self):
        convVoltage = self.canbus.glvVoltage / 100

        if convVoltage > 10:
            color = self.FE_green
        elif convVoltage > 9:
            color = "yellow"
        else:
            color = "red"
        
        self.lblVoltage.config(text=f"{(convVoltage):.2f}", bg=color)


root = tk.Tk()
root.attributes('-zoomed', True)
raspiDashboard = FE12Dashboard(root, 'vcan0', 'socketcan')

root.after(500, raspiDashboard.updateDashboard) # Needs time to fully load the GUI
root.mainloop()