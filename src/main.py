#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can
import cantools
import cantools.database
import threading
import csv
import time
from dashboard import FE12Dashboard

bus = can.interface.Bus(channel = 'vcan0', interface = 'socketcan')
db = cantools.database.load_file('src/FE12.dbc')
dashboard = FE12Dashboard()

# Open CSV file and write header
csv_file = open('logs/FE12_Log.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp'])

def process_can():
    print("Processing CAN messages...")

    while True:
        msg = bus.recv()
        try:
            # Write raw CAN data to CSV
            data_bytes = list(msg.data)
            # Pad data with zeros if less than 8 bytes
            data_bytes += [0] * (8 - len(data_bytes))
            # Format bytes as two-digit hex strings
            formatted_bytes = [f"{byte:02X}" for byte in data_bytes]
            # Write to CSV: ID, D0-D7, timestamp
            csv_writer.writerow([
                hex(msg.arbitration_id)[2:].upper(),  # Remove '0x' prefix
                *formatted_bytes,
                int(time.time() * 1000)  # Timestamp in milliseconds
            ])
            csv_file.flush()  # Ensure data is written immediately

            message = db.get_message_by_frame_id(msg.arbitration_id)
            data = message.decode(msg.data)

            match message.name:
                case 'Dashboard_Vehicle_State':
                    dashboard.master.after(0, dashboard.update_state, message.name, data)
                case 'M160_Temperature_Set_1':
                    dashboard.master.after(0, dashboard.update_temp, message.name, data)
                case 'M162_Temperature_Set_3':
                    dashboard.master.after(0, dashboard.update_temp, message.name, data)
                case 'PEI_Diagnostic_BMS_Data':
                    dashboard.master.after(0, dashboard.update_temp, message.name, data)
                case 'Dashboard_Random_Shit':
                    dashboard.master.after(0, dashboard.update_speed, data)
                case 'M169_Internal_Voltages':
                    dashboard.master.after(0, dashboard.update_glv, data)
            
        except KeyError:
            print(f"Unknown CAN ID: {hex(msg.arbitration_id)}")
        #catching errors for csv file
        except Exception as e:
            print(f"Error processing message: {e}")
threading.Thread(target=process_can, daemon=True).start()

dashboard.create_widgets()
dashboard.master.attributes('-zoomed', True)
dashboard.master.mainloop()

csv_file.close()
