import sys
import os
import can
import cantools
import cantools.database
import threading
import time
from datetime import datetime
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dashboard import FE12Dashboard

bus = can.interface.Bus(channel = 'virtual', interface = 'virtual')

dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
db = cantools.database.load_file(dbc_path)
dashboard = FE12Dashboard()
dashboard.root.bind('<x>', lambda event: dashboard.root.destroy())

def process_can():
    print("Processing CAN messages...\n")

    while True:
        msg = bus.recv()

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
                case 'M169_Internal_Voltages':
                    dashboard.root.after(0, dashboard.update_glv, data)
            
        except KeyError:
            print(f"Unknown CAN ID: {hex(msg.arbitration_id)}")

threading.Thread(target=process_can, daemon=True).start()

dashboard.root.state('zoomed')
dashboard.root.mainloop()