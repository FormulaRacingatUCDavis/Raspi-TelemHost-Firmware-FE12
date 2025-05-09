#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can
import cantools
import cantools.database
import threading
import time
import csv
from dashboard import FE12Dashboard

bus = can.interface.Bus(channel = 'vcan0', interface = 'socketcan')
db = cantools.database.load_file('src/FE12.dbc')
dashboard = FE12Dashboard()

csv_file = open('logs/FE12_Log.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp'])

def process_can():
    print("Processing CAN messages...")

    while True:
        msg = bus.recv()

        # Log message to CSV
        data_bytes = list(msg.data)
        data_bytes += [0] * (8 - len(data_bytes))
        formatted_bytes = [f"{byte:02X}" for byte in data_bytes]
        csv_writer.writerow([
            hex(msg.arbitration_id)[2:].upper(),
            *formatted_bytes,
            int(time.time() * 1000)
        ])
        csv_file.flush()

        try:
            message = db.get_message_by_frame_id(msg.arbitration_id)
            data = message.decode(msg.data)

            match message.name:
                case 'Dashboard_Vehicle_State':
                    dashboard.root.after(0, dashboard.update_state, message.name, data)
                case 'PEI_BMS_Status':
                    dashboard.root.after(0, dashboard.update_state, message.name, data)
                case 'M160_Temperature_Set_1':
                    dashboard.root.after(0, dashboard.update_temp, message.name, data)
                case 'M162_Temperature_Set_3':
                    dashboard.root.after(0, dashboard.update_temp, message.name, data)
                case 'PEI_Diagnostic_BMS_Data':
                    dashboard.root.after(0, dashboard.update_temp, message.name, data)
                case 'Dashboard_Random_Shit':
                    dashboard.root.after(0, dashboard.update_speed, data)
                case 'M169_Internal_Voltages':
                    dashboard.root.after(0, dashboard.update_glv, data)
            
        except KeyError:
            print(f"Unknown CAN ID: {hex(msg.arbitration_id)}")

threading.Thread(target=process_can, daemon=True).start()

dashboard.init_main_frame()
dashboard.root.attributes('-zoomed', True)
dashboard.root.mainloop()