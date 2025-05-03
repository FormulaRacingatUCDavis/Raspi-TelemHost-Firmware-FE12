#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

# FE12 Dashboard
# Display data received through Raspberry Pi telemetry host

import tkinter as tk

class FE12Dashboard:
    def __init__(self):

        self.master = tk.Tk()

        # Dashboard metrics
        self.bms_state = None
        self.vcu_state = 'STARTUP'
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_RPM = None
        self.glv_voltage = None
        self.soc = None

        # Widget placeholders
        self.lbl_speed = None
        self.header_speed = None
        self.lbl_state = None
        self.header_state = None
        self.lbl_voltage = None
        self.header_voltage = None
        self.lbl_soc = None
        self.header_soc = None
        self.lbl_temp = None
        self.col_div = None

    def create_widgets(self):

        self.master.title('FE12 Dashboard')
        self.master.configure(bg='black')

        dashboard = tk.Frame(self.master, bg='black')
        dashboard.pack(fill='both', expand=True, pady=20)

        dashboard.grid_rowconfigure(0, weight=5, uniform='equal')  # Header

        dashboard.grid_rowconfigure(1, weight=10, uniform='equal') 
        dashboard.grid_rowconfigure(2, weight=10, uniform='equal')

        dashboard.grid_rowconfigure(3, weight=6, uniform='equal')  # Header
        dashboard.grid_rowconfigure(4, weight=20, uniform='equal')
        
        dashboard.grid_columnconfigure(0, weight=15, uniform='equal')
        dashboard.grid_columnconfigure(1, weight=1, uniform='equal') # Column divider
        dashboard.grid_columnconfigure(2, weight=15, uniform='equal')

        padx_out = 10

        header_font_size = 20

        # Speed
        self.header_speed = tk.Label(dashboard, text=f'MPH', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        self.header_speed.grid(row=0, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_speed = tk.Label(dashboard, font=('Trebuchet MS', 75), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_speed.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(padx_out, 0))

        # Vehicle state
        self.header_state = tk.Label(dashboard, text=f'STATE:', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='w', pady=5)
        self.header_state.grid(row=3, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_state = tk.Label(dashboard, text=self.vcu_state, font=('Trebuchet MS', 35), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_state.grid(row=4, column=0, sticky='nsew', padx=(padx_out, 0))

        # Column Divider
        self.col_div = tk.Frame(dashboard, bg ='black')
        self.col_div.grid(column= 1, sticky='nsew', rowspan=2)

        # GLV Voltage
        self.header_voltage = tk.Label(dashboard, text=f'GLV V', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        self.header_voltage.grid(row=3, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_voltage = tk.Label(dashboard, font=('Trebuchet MS', 50), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_voltage.grid(row=4, column=2, sticky='nsew', padx=(0, padx_out))

        # State of Charge
        self.header_soc = tk.Label(dashboard, text=f'PACK SOCIT', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        self.header_soc.grid(row=0, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_soc = tk.Label(dashboard, font=('Trebuchet MS', 50), anchor='center', padx=5, pady=5)
        # Temperature
        self.lbl_soc.grid(row=1, column=2, sticky='nsew', padx=(0, padx_out), pady=(0,5))
        self.lbl_temp = tk.Label(dashboard, font=('Trebuchet MS', 50), anchor='center', padx=5, pady=5)
        self.lbl_temp.grid(row=2, column=2, sticky='nsew', padx=(0, padx_out))

    def update_state(self, message_name, data):
        # Prioritize BMS faults over VCU faults

        if message_name == 'Dashboard_Vehicle_State':
            self.vcu_state = data['State']
        else:
            self.bms_state = data['State']

        if self.bms_state != 'NO_ERROR' and self.bms_state != None:
            if isinstance(self.bms_state, int):
                state = 'YO WTF?'
                color = 'red'
            else:
                state = str(self.bms_state).replace('_', ' ')
                color = 'red'
        else:
            if isinstance(self.vcu_state, int):
                state = 'YO WTF?'
                color = 'red'
            else:
                state = str(self.vcu_state).replace('_', ' ')
                match state:
                    case 'LV':
                        color = 'lawn green'
                    case 'PRECHARGE':
                        color = 'lawn green'
                    case 'HV ENABLED':
                        color = 'lawn green'
                    case 'DRIVE':
                        color = 'lawn green'
                    case 'STARTUP':
                        color = 'lawn green'
                # Fault states
                    case 'BSPD TRIPD':
                        color = 'yellow'
                    case 'UNCALIBRTD':
                        color = 'yellow'
                    case _:
                        color = 'red'

        self.lbl_state.config(text=state, bg=color)

    def update_temp(self, message_name, data):
        # Display highest temperature of motor, motor controller, BMS
        
        if message_name == 'M162_Temperature_Set_3':
            self.motor_temp = data['INV_Motor_Temp']
        elif message_name == 'M160_Temperature_Set_1':
            self.mc_temp = (data['INV_Module_A_Temp'] + data['INV_Module_B_Temp'] + data['INV_Module_C_Temp']) / 3
        else:
            self.pack_temp = data['HI_Temp']
            self.soc = data['SOC']
            self.lbl_soc.config(text=f'{round(self.soc)}%', bg='red')

        max_temp = -4000
        color = 'gray'

        if self.motor_temp > max_temp:
            max_temp = self.motor_temp
            if self.motor_temp < 45:
                color = 'lawn green'
            elif self.motor_temp < 50:
                color = 'yellow'
            else:
                color = 'red'

        if self.mc_temp > max_temp:
            max_temp = self.mc_temp
            if self.mc_temp < 45:
                color = 'lawn green'
            elif self.mc_temp < 50:
                color = 'yellow'
            else:
                color = 'red'

        if self.pack_temp > max_temp:
            max_temp = self.pack_temp
            if self.pack_temp <= 30:
                color = 'lawn green'
            elif self.pack_temp <= 40:
                color = 'yellow'
            elif self.pack_temp <= 50:
                color = 'orange'
            else:
                color = 'red'

        self.lbl_temp.config(text=f'{round(max_temp)}C', bg=color)

    def update_speed(self, data):
        # Slow down speed updates for readability

        self.speed_RPM = data['Front_Wheel_Speed']

        circum = 50.2655 # Radius = 8 in
        speed_MPH = self.speed_RPM * circum * 60 / 63360

        self.lbl_speed.config(text=str(round(speed_MPH)), bg='dodger blue')

    def update_glv(self, data):

        self.glv_voltage = data['INV_Ref_Voltage_12_0']

        if self.glv_voltage > 10:
            color = 'lawn green'
        elif self.glv_voltage > 9:
            color = 'yellow'
        else:
            color = 'red'
        
        self.lbl_voltage.config(text=f'{(self.glv_voltage):.2f}', bg=color)