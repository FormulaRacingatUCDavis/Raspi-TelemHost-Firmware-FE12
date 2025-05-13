import sys
import os
import can
import time
import cantools
import cantools.database
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dashboard import FE12Dashboard

dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
db = cantools.database.load_file(dbc_path)
dashboard = FE12Dashboard()
dashboard.root.bind('<x>', lambda event: dashboard.root.destroy())

def process_can(msg):
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
            case 'M169_Internal_Voltages':
                dashboard.root.after(0, dashboard.update_glv, data)
    except KeyError:
        print(f"Unknown CAN ID: {hex(msg.arbitration_id)}")

def test_vcu_state():
    print('Testing VCU State..\n')

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

def test_knobs():
    print('Testing dashboard knobs..\n')
    time.sleep(1) # Show dashboard before switching frames

    message = db.get_message_by_name('Dashboard_Knobs')
    can_id = message.frame_id
    knob1 = 0x00
    knob2 = 0x00

    while knob1 <= 4095:
        knob_data = {
            'Knob1': knob1,
            'Knob2': knob2
        }
        encoded_knob_data = message.encode(knob_data)
        msg = can.Message(arbitration_id=can_id, data=encoded_knob_data)

        print(message.decode(msg.data))
        time.sleep(0.005)
        process_can(msg)

        knob1 += 1

    print('\Bar gauge state test complete.')

threading.Thread(target=test_vcu_state, daemon=True).start() # Enter the function of what you want to test
dashboard.root.title('FE12 Dashboard - Test Mode')
dashboard.root.state('zoomed')
dashboard.root.mainloop()