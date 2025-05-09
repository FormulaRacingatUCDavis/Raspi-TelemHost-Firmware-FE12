#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can
import cantools
import cantools.database
import threading
import csv
from dashboard import FE12Dashboard

bus = can.interface.Bus(channel = 'vcan0', interface = 'socketcan')
db = cantools.database.load_file('FE12.dbc')
dashboard = FE12Dashboard()

def process_can():
    print("Processing CAN messages...")

    while True:
        msg = bus.recv()
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
                case 'Dashboard_Knobs':
                    dashboard.root.after(0, dashboard.update_screen_knob, data)
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