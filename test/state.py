import sys
import os
import can
import time
import random
import cantools
import cantools.database
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dashboard import FE12Dashboard

dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
db = cantools.database.load_file(dbc_path)
dashboard = FE12Dashboard()
knob_update_ts = 0
dashboard.root.bind('<x>', lambda event: dashboard.root.destroy())

def process_can(msg):
    global knob_update_ts
    time.sleep(0.203) # Measured logging rate
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
                knob_update_ts = time.time()
            case 'M169_Internal_Voltages':
                dashboard.root.after(0, dashboard.update_glv, data)
        
        if time.time() - knob_update_ts > 1 and dashboard.current_frame == dashboard.gauge_frame:
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

def test_vcu_state():
    print('\nTesting VCU State..\n')

    message = db.get_message_by_name('Dashboard_Vehicle_State')
    can_id = message.frame_id
    vcu_state = 0x00

    while vcu_state <= 0x05:
        msg = can.Message(arbitration_id=can_id, data=[0x00, 0x01, 0x02, 0x03, vcu_state, 0x05, 0x06])

        print(message.decode(msg.data))
        time.sleep(1)
        process_can(msg)
        vcu_state += 0x01

    vcu_state = 0x81

    while vcu_state <= 0x8A:
        msg = can.Message(arbitration_id=can_id, data=[0x00, 0x01, 0x02, 0x03, vcu_state, 0x05, 0x06])

        print(message.decode(msg.data))
        time.sleep(1)
        process_can(msg)
        vcu_state += 0x01

    print('\nVCU state test complete.')

threading.Thread(target=test_vcu_state, daemon=True).start() # Enter the function of what you want to test
dashboard.root.title('FE12 Dashboard - Test Mode')
dashboard.root.state('zoomed')
dashboard.root.mainloop()