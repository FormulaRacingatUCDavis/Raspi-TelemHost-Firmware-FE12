import tkinter as tk
import time

class Dashboard:
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg='black')

        # Driver mode values
        self.bms_state = None
        self.vcu_state = None
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_RPM = None
        self.glv_voltage = None
        self.soc = None
        self.knob1_adc = 0
        self.knob2_adc = 0

        # Debug mode values
        self.d_soc = None
        self.d_pack_temp = None
        self.d_mc_temp = None
        self.d_motor_temp = None
        self.d_vcu_state = None
        self.d_glv_voltage = None
        self.d_shutdown = None
        self.d_mc_state = None
        self.d_free_slot = None
        self.d_free_slot_header = None
        self.d_free_slot_unit = None

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
        self.lbl_state = tk.Label(self.main_frame, text='STARTUP', font=('Trebuchet MS', 35, 'bold'), fg='black', anchor='center', padx=5, pady=5)
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

        # Error frame
        self.error_frame = tk.Label(self.root, bg='orange red', font=('Trebuchet MS', 50, 'bold'))
        self.bms_error = False
        self.vcu_error = False

        self.error_timestamp = 0

        # Bar gauge frame
        self.gauge_frame = tk.Frame(self.root, bg='black')
        self.gauge_frame.columnconfigure(0, weight=1)
        self.gauge_frame.columnconfigure(1, weight=2)

        top_bar = tk.Frame(self.gauge_frame, bg='black')
        top_bar.grid(row=0, column=1, sticky='nsew')

        self.bottom_bar = tk.Frame(self.gauge_frame, bg='yellow')
        self.bottom_bar.grid(row=1, column=1, sticky='nsew')
        self.bottom_bar.grid_rowconfigure(0, weight=1)
        self.bottom_bar.grid_columnconfigure(0, weight=1)

        self.lbl_gauge = tk.Label(self.gauge_frame, font=('Trebuchet MS', 125, 'bold'), fg='black', width=2)
        self.lbl_gauge.grid(row=0, rowspan=2, column=0, sticky='nsew')

        self.knob_timestamp = 0

        # Debug frame
        self.debug_frame = tk.Frame(self.root, bg='black')
        for i in range(7):
            if i % 2 == 0:
                self.debug_frame.rowconfigure(i, weight=3, uniform='equal')  # Headers and bottom spacer
            else:
                self.debug_frame.rowconfigure(i, weight=10, uniform='equal')  # Value
        for j in range(7):
            if j % 2 == 0:
                self.debug_frame.columnconfigure(j, weight=1, uniform='equal')  # Column divider
            else:
                self.debug_frame.columnconfigure(j, weight=15, uniform='equal')

        self.debug_soc_h = tk.Label(self.debug_frame, text='SOC', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_pack_temp_h = tk.Label(self.debug_frame, text='PACK TEMP', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_shutdown_h = tk.Label(self.debug_frame, text='SHUTDOWN', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_mc_temp_h= tk.Label(self.debug_frame, text='MC TEMP', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_motor_temp_h = tk.Label(self.debug_frame, text='MOTOR TEMP', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_mc_state_h = tk.Label(self.debug_frame, text='MC STATE', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_vcu_state_h = tk.Label(self.debug_frame, text='STATE', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_glv_voltage_h = tk.Label(self.debug_frame, text='GLV V', font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')
        self.debug_free_slot_h = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='yellow', bg='black', anchor='w')

        debug_headers = [
            self.debug_soc_h, self.debug_pack_temp_h, self.debug_shutdown_h,
            self.debug_mc_temp_h, self.debug_motor_temp_h, self.debug_mc_state_h,
            self.debug_vcu_state_h, self.debug_glv_voltage_h, self.debug_free_slot_h
        ]

        self.debug_soc = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_pack_temp = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_shutdown = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_mc_temp = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_motor_temp = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_mc_state = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_vcu_state = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_glv_voltage = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')
        self.debug_free_slot = tk.Label(self.debug_frame, font=('Trebuchet MS', 15, 'bold'), fg='black', bg='white')

        debug_values = [
            self.debug_soc, self.debug_pack_temp, self.debug_shutdown,
            self.debug_mc_temp, self.debug_motor_temp, self.debug_mc_state,
            self.debug_vcu_state, self.debug_glv_voltage, self.debug_free_slot
        ]

        debug_header = 0
        debug_val = 0
        for i in range(6):
            for j in range(7):
                if i % 2 == 0 and j % 2 == 1:
                    row = i // 2
                    col = j // 2
                    header = debug_headers[debug_header]
                    header.grid(row=i, column=j, sticky='nsew')
                    debug_header += 1
                elif i % 2 == 1 and j % 2 == 1:
                    row = i // 2
                    col = j // 2
                    value = debug_values[debug_val]
                    value.grid(row=i, column=j, sticky='nsew')
                    debug_val += 1

        # Initial state
        self.mode = 'debug'
        self.current_frame = self.main_frame
        self.current_frame.pack(fill='both', expand=True)
        self.root.update_idletasks()

    def switch_frame(self, frame):
        if self.current_frame != frame and self.current_frame != self.gauge_frame:
            self.current_frame.pack_forget()
            frame.pack(fill='both', expand=True)
            self.root.update_idletasks()
            self.current_frame = frame

    def debug(self, soc, pack_temp, shutdown, mc_temp, motor_temp, mc_state, vcu_state, glv_voltage, free_slot, free_slot_header, free_slot_unit):
        if self.current_frame != self.debug_frame:
            self.switch_frame(self.debug_frame)

        if soc != self.d_soc:
            self.d_soc = soc
            self.debug_soc.config(text=f'{round(self.d_soc)}%')
        if pack_temp != self.d_pack_temp:
            self.d_pack_temp = pack_temp
            self.debug_pack_temp.config(text=f'{round(self.d_pack_temp)}C')
        if shutdown != self.d_shutdown:
            self.d_shutdown = shutdown
            self.debug_shutdown.config(text=self.d_shutdown)

        if mc_temp != self.d_mc_temp:
            self.d_mc_temp = mc_temp
            self.debug_mc_temp.config(text=f'{round(self.d_mc_temp)}C')
        if motor_temp != self.d_motor_temp:
            self.d_motor_temp = motor_temp
            self.debug_motor_temp.config(text=f'{round(self.d_motor_temp)}C')
        if mc_state != self.d_mc_state:
            self.d_mc_state = mc_state
            self.debug_mc_state.config(text=self.d_mc_state)

        if vcu_state != self.d_vcu_state:
            self.d_vcu_state = vcu_state
            self.debug_vcu_state.config(text=self.d_vcu_state)
        if glv_voltage != self.d_glv_voltage:
            self.d_glv_voltage = glv_voltage
            self.debug_glv_voltage.config(text=f'{(self.d_glv_voltage):.2f}')
            
        if free_slot != self.d_free_slot:
            if free_slot_header != self.d_free_slot_header:
                self.d_free_slot_header = free_slot_header
                self.d_free_slot_unit = free_slot_unit
                self.debug_free_slot_h.config(text=f'DEBUG ({free_slot_header})')
            self.d_free_slot = free_slot
            self.debug_free_slot.config(text=f'{self.d_free_slot}{self.d_free_slot_unit}')

    def update_state(self, vcu_state, bms_state):
        if vcu_state == self.vcu_state and bms_state == self.bms_state:
            # Exit error flash screen if 3 seconds has passed since change
            if self.current_frame == self.error_frame:
                if time.time() - self.error_timestamp > 3:
                    self.current_frame.forget()
                    self.main_frame.pack(fill='both', expand=True)
                    self.root.update_idletasks()
                    self.current_frame = self.main_frame
            return
        self.vcu_state = vcu_state
        self.bms_state = bms_state

        # Prioritize BMS faults over VCU faults
        if self.bms_state != 'NO_ERROR' and self.bms_state != None:
            self.error_timestamp = time.time()
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
                    self.error_timestamp = time.time()
                    self.vcu_error = True

        if self.bms_error or self.vcu_error:
            self.lbl_state.config(text=state, bg='red')
            self.error_frame.config(text=state)
            self.switch_frame(self.error_frame)
        else:
            self.lbl_state.config(text=state, bg=color)
            self.switch_frame(self.main_frame)

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

    def update_knob(self, knob1_adc, knob2_adc):
        if knob1_adc != self.knob1_adc and self.knob1_adc != None:
            self.knob1_adc = knob1_adc
            percentage = (knob1_adc / 4095) * 100
            color = 'dodger blue'
        elif knob2_adc != self.knob2_adc and self.knob2_adc != None:
            self.knob2_adc = knob2_adc
            percentage = (knob2_adc / 4095) * 100
            color = 'orange red'
        else:
            # Exit knob flash screen if 1 second has passed since change
            if self.current_frame == self.gauge_frame:
                if time.time() - self.knob_timestamp > 3:
                    if self.bms_error == True or self.vcu_error == True:
                        self.current_frame.forget()
                        self.error_frame.pack(fill='both', expand=True)
                        self.root.update_idletasks()
                        self.current_frame = self.error_frame
                    else:
                        self.current_frame.forget()
                        self.main_frame.pack(fill='both', expand=True)
                        self.root.update_idletasks()
                        self.current_frame = self.main_frame
            return

        self.gauge_frame.rowconfigure(0, weight=int(100 - percentage))
        self.gauge_frame.rowconfigure(1, weight=int(percentage))

        self.lbl_gauge.config(text=str(round(percentage)), bg=color)
        self.knob_timestamp = time.time()

        self.switch_frame(self.gauge_frame)