#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can
import cantools
import cantools.database
import threading
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

threading.Thread(target=process_can, daemon=True).start()

dashboard.create_widgets()
dashboard.master.attributes('-zoomed', True)
dashboard.master.mainloop()