import tkinter as tk

class Dashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('FE12 Dashboard')
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        # Driver mode values
        self.bms_state = None
        self.vcu_state = None
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_RPM = None
        self.glv_voltage = None
        self.soc = None

        # Main frame
        self.main_frame = tk.Frame(self.root, bg='black')

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
        header_speed = tk.Label(self.main_frame, text=f'MPH', font=('Trebuchet MS', header_font_size, 'bold'), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_speed.grid(row=0, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_speed = tk.Label(self.main_frame, font=('Trebuchet MS', 75, 'bold'), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_speed.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(padx_out, 0))

        # Vehicle state
        header_state = tk.Label(self.main_frame, text=f'STATE:', font=('Trebuchet MS', header_font_size, 'bold'), bg='black', fg='yellow', anchor='w', pady=5)
        header_state.grid(row=3, column=0, sticky='nsew', padx=(padx_out, 0))
        self.lbl_state = tk.Label(self.main_frame, text='STARTUP', font=('Trebuchet MS', 30, 'bold'), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_state.grid(row=4, column=0, sticky='nsew', padx=(padx_out, 0))

        # Column Divider
        col_div = tk.Frame(self.main_frame, bg ='black')
        col_div.grid(column= 1, sticky='nsew', rowspan=2)

        # GLV Voltage
        header_voltage = tk.Label(self.main_frame, text=f'GLV V', font=('Trebuchet MS', header_font_size, 'bold'), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_voltage.grid(row=3, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_voltage = tk.Label(self.main_frame, font=('Trebuchet MS', 50, 'bold'), fg='black', anchor='center', padx=5, pady=5)
        self.lbl_voltage.grid(row=4, column=2, sticky='nsew', padx=(0, padx_out))

        # State of Charge
        header_soc = tk.Label(self.main_frame, text=f'PACK SOCIT', font=('Trebuchet MS', header_font_size, 'bold'), bg='black', fg='yellow', anchor='s', padx=5, pady=5)
        header_soc.grid(row=0, column=2, sticky='nsew', padx=(0, padx_out))
        self.lbl_soc = tk.Label(self.main_frame, font=('Trebuchet MS', 50, 'bold'), anchor='center', padx=5, pady=5)
        # Temperature
        self.lbl_soc.grid(row=1, column=2, sticky='nsew', padx=(0, padx_out), pady=(0,5))
        self.lbl_temp = tk.Label(self.main_frame, font=('Trebuchet MS', 50, 'bold'), anchor='center', padx=5, pady=5)
        self.lbl_temp.grid(row=2, column=2, sticky='nsew', padx=(0, padx_out))

        # Initial state
        self.mode = 'drive'
        self.current_frame = self.main_frame
        self.previous_frame = None
        self.current_frame.pack(fill='both', expand=True)
        self.root.update_idletasks()

    def update_state(self, vcu_state, bms_state):
        if vcu_state == self.vcu_state and bms_state == self.bms_state:
            return
        self.vcu_state = vcu_state
        self.bms_state = bms_state

        # Prioritize BMS faults over VCU faults
        if self.bms_state != 'NO ERROR' and self.bms_state != None:
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
            self.lbl_state.config(text=state, bg='red')
        else:
            self.lbl_state.config(text=state, bg=color)

    def update_temp(self, motor_temp, mc_temp, pack_temp, soc):
        if (motor_temp == self.motor_temp and 
            mc_temp == self.mc_temp and 
            pack_temp == self.pack_temp and 
            soc == self.soc):
            return
        self.motor_temp = motor_temp
        self.mc_temp = mc_temp
        self.pack_temp = pack_temp

        self.soc = soc
        if soc != None:
            self.lbl_soc.config(text=f'{round(self.soc)}%', bg='orange red')

        # Display highest temperature of motor, motor controller, BMS
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

    def update_speed(self, speed_RPM):
        if speed_RPM == self.speed_RPM:
            return
        self.speed_RPM = speed_RPM

        circum = 50.2655 # Radius = 8 in
        speed_MPH = self.speed_RPM * circum * 60 / 63360

        self.lbl_speed.config(text=str(round(speed_MPH)), bg='dodger blue')

    def update_glv(self, glv_voltage):
        if glv_voltage == self.glv_voltage:
            return
        self.glv_voltage = glv_voltage

        if self.glv_voltage > 10:
            color = 'lawn green'
        elif self.glv_voltage > 9:
            color = 'yellow'
        else:
            color = 'orange red'
        
        self.lbl_voltage.config(text=f'{(self.glv_voltage):.2f}', bg=color)