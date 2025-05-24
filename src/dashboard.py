import tkinter as tk

class FE12Dashboard:
    def __init__(self):

        self.root = tk.Tk()

        # Dashboard metrics
        self.bms_state = None
        self.vcu_state = 'STARTUP'
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_MPH = None
        self.glv_voltage = None
        self.soc = None
        self.knob1_percentage = 0
        self.knob2_percentage = 0

        # Main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.root.title('FE12 Dashboard')
        self.root.configure(bg='black')

        self.main_frame.grid_rowconfigure(0, weight=5, uniform='equal')  # Header

        self.main_frame.grid_rowconfigure(1, weight=10, uniform='equal') 
        self.main_frame.grid_rowconfigure(2, weight=10, uniform='equal')

        self.main_frame.grid_rowconfigure(3, weight=6, uniform='equal')  # Header
        self.main_frame.grid_rowconfigure(4, weight=20, uniform='equal')
        
        self.main_frame.grid_columnconfigure(0, weight=15, uniform='equal')
        self.main_frame.grid_columnconfigure(1, weight=1, uniform='equal') # Column divider
        self.main_frame.grid_columnconfigure(2, weight=15, uniform='equal')

        padx_out = 10

        header_font_size = 20

        # Speed
        header_speed = tk.Label(self.main_frame, text=f'MPH', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_speed.grid(row=0, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_speed = tk.Label(self.main_frame, text=self.speed_MPH, font=('Trebuchet MS', 75), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_speed.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(padx_out, 0))

        # Vehicle state
        header_state = tk.Label(self.main_frame, text=f'STATE:', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='w', pady=5)
        header_state.grid(row=3, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_state = tk.Label(self.main_frame, text=self.vcu_state, font=('Trebuchet MS', 35), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_state.grid(row=4, column=0, sticky='nsew', padx=(padx_out, 0))

        # Column Divider
        col_div = tk.Frame(self.main_frame, bg ='black')
        col_div.grid(column= 1, sticky='nsew', rowspan=2)

        # GLV Voltage
        header_voltage = tk.Label(self.main_frame, text=f'GLV V', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_voltage.grid(row=3, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_voltage = tk.Label(self.main_frame, text=self.glv_voltage, font=('Trebuchet MS', 50), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_voltage.grid(row=4, column=2, sticky='nsew', padx=(0, padx_out))

        # State of Charge
        header_soc = tk.Label(self.main_frame, text=f'PACK SOCIT', font=('Trebuchet MS', header_font_size), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_soc.grid(row=0, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_soc = tk.Label(self.main_frame, text=self.soc, font=('Trebuchet MS', 50), anchor='center', padx=5, pady=5)
        # Temperature
        self.lbl_soc.grid(row=1, column=2, sticky='nsew', padx=(0, padx_out), pady=(0,5))
        self.lbl_temp = tk.Label(self.main_frame, font=('Trebuchet MS', 50), anchor='center', padx=5, pady=5)
        self.lbl_temp.grid(row=2, column=2, sticky='nsew', padx=(0, padx_out))

        # Error frame
        self.error_frame = tk.Label(self.root, bg='orange red', font=('Trebuchet MS', 125))
        self.bms_error = False
        self.vcu_error = False

        # Bar gauge frame
        self.gauge_frame = tk.Frame(self.root, bg='black')
        self.gauge_frame.columnconfigure(0, weight=1)

        top_bar = tk.Frame(self.gauge_frame, bg='black')
        top_bar.grid(row=0, column=0, sticky='nsew')

        bottom_bar = tk.Frame(self.gauge_frame, bg='blue')
        bottom_bar.grid(row=1, column=0, sticky='nsew')
        bottom_bar.grid_rowconfigure(0, weight=1)
        bottom_bar.grid_columnconfigure(0, weight=1)

        self.lbl_gauge = tk.Label(bottom_bar, font=('Trebuchet MS', 125), fg='black', bg='blue')
        self.lbl_gauge.grid(row=0, column=0, sticky='nsew')

        # Current frame
        self.current_frame = self.main_frame
        self.current_frame.pack(fill='both', expand=True)
        self.root.update_idletasks()

    def want_frame(self, frame):
        if self.current_frame != frame and self.current_frame != self.gauge_frame:
            self.current_frame.pack_forget()
            frame.pack(fill='both', expand=True)
            self.root.update_idletasks()
            self.current_frame = frame

    def update_state(self, message_name, data):

        if message_name == 'Dashboard_Vehicle_State':
            self.vcu_state = data['State']
        else:
            self.bms_state = data['BMS_Status']

        # Prioritize BMS faults over VCU faults
        if self.bms_state != 'NO_ERROR' and self.bms_state != None:
            self.want_frame(self.error_frame)
            if isinstance(self.bms_state, int):
                state = 'YO WTF?'
                self.bms_error = True
            else:
                state = str(self.bms_state).replace('_', ' ')
                self.bms_error = True
        else:
            self.bms_error = False
            if isinstance(self.vcu_state, int):
                state = 'YO WTF?'
                self.vcu_error = True
            else:
                state = str(self.vcu_state).replace('_', ' ')

                green = {'LV', 'PRECHARGE', 'HV ENABLED', 'DRIVE', 'STARTUP'}
                yellow = {'BSPD TRIPD', 'UNCALIBRTD'}

                if state in green:
                    color = 'lawn green'
                    self.vcu_error = False
                elif state in yellow:
                    color = 'yellow'
                    self.vcu_error = False
                else:
                    self.vcu_error = True

        if self.bms_error or self.vcu_error:
            self.error_frame.config(text=state)
            self.want_frame(self.error_frame)
        else:
            self.lbl_state.config(text=state, bg=color)
            self.want_frame(self.main_frame)

    def update_temp(self, message_name, data):
        # Display highest temperature of motor, motor controller, BMS
        
        if message_name == 'M162_Temperature_Set_3':
            self.motor_temp = data['INV_Motor_Temp']
        elif message_name == 'M160_Temperature_Set_1':
            self.mc_temp = (data['INV_Module_A_Temp'] + data['INV_Module_B_Temp'] + data['INV_Module_C_Temp']) / 3
        else:
            self.pack_temp = data['HI_Temp']
            self.soc = data['SOC']
            self.lbl_soc.config(text=f'{round(self.soc)}%', bg='orange red')

        max_temp = -4000
        color = 'gray'

        if self.motor_temp > max_temp:
            max_temp = self.motor_temp
            if self.motor_temp < 45:
                color = 'lawn green'
            elif self.motor_temp < 50:
                color = 'yellow'
            else:
                color = 'orange red'

        if self.mc_temp > max_temp:
            max_temp = self.mc_temp
            if self.mc_temp < 45:
                color = 'lawn green'
            elif self.mc_temp < 50:
                color = 'yellow'
            else:
                color = 'orange red'

        if self.pack_temp > max_temp:
            max_temp = self.pack_temp
            if self.pack_temp <= 30:
                color = 'lawn green'
            elif self.pack_temp <= 40:
                color = 'yellow'
            elif self.pack_temp <= 50:
                color = 'orange'
            else:
                color = 'orange red'

        self.lbl_temp.config(text=f'{round(max_temp)}C', bg=color)

    def update_speed(self, data):
        # Slow down speed updates for readability

        speed_RPM = data['Front_Wheel_Speed']

        circum = 50.2655 # Radius = 8 in
        self.speed_MPH = speed_RPM * circum * 60 / 63360

        self.lbl_speed.config(text=str(round(self.speed_MPH)), bg='dodger blue')

    def update_glv(self, data):

        self.glv_voltage = data['INV_Ref_Voltage_12_0']

        if self.glv_voltage > 10:
            color = 'lawn green'
        elif self.glv_voltage > 9:
            color = 'yellow'
        else:
            color = 'orange red'
        
        self.lbl_voltage.config(text=f'{(self.glv_voltage):.2f}', bg=color)

    def update_knob(self, data):

        if self.knob1_percentage != (data['Knob1'] / 4095) * 100 and self.knob1_percentage != None:
            active = 1
            self.knob1_percentage = (data['Knob1'] / 4095) * 100
        elif self.knob2_percentage != (data['Knob2'] / 4095) * 100 and self.knob2_percentage != None:
            active = 2
            self.knob2_percentage = (data['Knob2'] / 4095) * 100

        if active == 1:
            percentage = self.knob1_percentage
            knob_color = 'blue'
        elif active == 2:
            percentage = self.knob2_percentage
            knob_color = 'orange red'

        self.gauge_frame.rowconfigure(0, weight=int(100 - percentage))
        self.gauge_frame.rowconfigure(1, weight=int(percentage))

        knob_label = f"KNOB {active}"
        self.lbl_gauge.config(text=f'{knob_label}: {round(percentage)}%', bg=knob_color)

        self.want_frame(self.gauge_frame)