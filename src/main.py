#!/home/frucd/projects/Raspi-TelemHost-Firmware-FE12/.venv/bin/python

import can
import os
import cantools.database
import threading
import time
import ADS1263
import RPi.GPIO as GPIO
from datetime import datetime
import csv
from dashboard import FE12Dashboard

project_root = os.path.dirname(os.path.dirname(__file__))

# Initialize CAN Bus and import DBC file
bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
dbc_path = os.path.join(os.path.dirname(__file__), 'FE12.dbc')
db = cantools.database.load_file(dbc_path)

# CSV for CAN message logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f'{timestamp}.csv')
csv_file = open(log_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp'])

dashboard = FE12Dashboard()
dashboard.root.bind('<x>', lambda event: dashboard.root.destroy()) # Exit

knob_timestamp = 0

# ADS1263 HAT
adc = ADS1263.ADS1263()
if (adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1):
    exit()
adc.ADS1263_SetMode(0)

def main():
    global knob_timestamp
    while True:

        # Receive ADS1263 input data
        adc_data = [adc.ADS1263_GetChannalValue(0),
                    adc.ADS1263_GetChannalValue(1),
                    adc.ADS1263_GetChannalValue(2),
                    adc.ADS1263_GetChannalValue(3),
                    adc.ADS1263_GetChannalValue(4),
                    adc.ADS1263_GetChannalValue(5),
                    0, 0]

        # Log ADS1263 inputs to CSV
        csv_file.flush()
        csv_writer.writerow([
            hex(898)[2:].upper(),
            *adc_data,
            int(time.time() * 1000)
        ])
        csv_file.flush()

        # Receive CAN message
        msg = bus.recv()

        # Log CAN message to CSV
        data_bytes = list(msg.data)
        data_bytes += [0] * (8 - len(data_bytes))
        formatted_bytes = [f"{byte:02X}" for byte in data_bytes]
        csv_writer.writerow([
            hex(msg.arbitration_id)[2:].upper(),
            *formatted_bytes,
            int(time.time() * 1000)
        ])

        try:
            message = db.get_message_by_frame_id(msg.arbitration_id)
            data = message.decode(msg.data)

            match message.name:
                case 'Dashboard_Vehicle_State' | 'PEI_BMS_Status':
                    dashboard.root.after(0, dashboard.update_state, message.name, data)
                case 'M160_Temperature_Set_1' | 'M162_Temperature_Set_3' | 'PEI_Diagnostic_BMS_Data':
                    dashboard.root.after(0, dashboard.update_temp, message.name, data)
                case 'Dashboard_Random_Shit':
                    dashboard.root.after(0, dashboard.update_speed, data)
                case 'Dashboard_Knobs':
                    dashboard.root.after(0, dashboard.update_knob, data)
                    knob_timestamp = time.time()
                case 'M169_Internal_Voltages':
                    dashboard.root.after(0, dashboard.update_glv, data)

            # Exit knob flash screen after 1 second has passed
            if time.time() - knob_timestamp > 1 and dashboard.current_frame == dashboard.gauge_frame:
                if dashboard.bms_error == True or dashboard.vcu_error == True:
                    dashboard.current_frame.forget()
                    dashboard.error_frame.pack(fill='both', expand=True)
                    dashboard.root.update_idletasks()
                    dashboard.current_frame = dashboard.error_frame
                else:
                    dashboard.current_frame.forget()
                    dashboard.main_frame.pack(fill='both', expand=True)
                    dashboard.root.update_idletasks()
                    dashboard.current_frame = dashboard.main_frame

        except KeyError:
            print(f"Unknown CAN ID: {hex(msg.arbitration_id)}")

if __name__ == '__main__':
    threading.Thread(target=main, daemon=True).start()

dashboard.root.attributes('-fullscreen', True)
dashboard.root.config(cursor="none")
dashboard.root.mainloop()