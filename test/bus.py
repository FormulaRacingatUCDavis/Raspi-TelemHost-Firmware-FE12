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

def test_can_stream():
    print('\nTesting stream of varied CAN messages..\n')

    msg_names = [
        'M160_Temperature_Set_1',
        'M162_Temperature_Set_3',
        'PEI_Diagnostic_BMS_Data',
        'Dashboard_Random_Shit',
        'M169_Internal_Voltages',
        'Dashboard_Knobs',
        'Dashboard_Vehicle_State',
        'PEI_BMS_Status'            # 7 message types
    ]

    vcu_states = [
        0x00,
        0x01,
        0x02,
        0x03,
        0x04, # YO WTF
        0x05,
        0x81,
        0x82,
        0x83,
        0x84,
        0x85,
        0x86,
        0x87,
        0x88,
        0x89,
        0x8A
    ]

    bms_states = [
        0x00,
        0x01,
        0x02,
        0x04,
        0x05, # YO WTF
        0x08,
        0x10,
        0x20,
        0x40,
        0x80
    ]

    while True:
        msg_name = msg_names[random.randint(0,4)]
        message = db.get_message_by_name(msg_name)
        match msg_name:
            case 'Dashboard_Vehicle_State':
                data = {
                    'HV_Requested': random.randint(0, 1),
                    'Throttle1_Level': random.randint(0, 100),
                    'Throttle2_Level': random.randint(0, 100),
                    'Brake_Level': random.randint(0, 100),
                    'VCU_ticks': random.randint(0,65535),
                    'State': vcu_states[random.randint(0,15)]
                }
            case 'PEI_BMS_Status':
                data = {
                    'BMS_Status': bms_states[random.randint(0, 9)],
                    'SPI_Error_Flags': random.randint(0, 65535),
                    'Max_Faulting_IC_Address': random.randint(0, 9),
                    'Communication_Break_ID': random.randint(-1, 9)
                }
            case 'M160_Temperature_Set_1':
                data = {
                    'INV_Gate_Driver_Board_Temp': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Module_C_Temp': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Module_B_Temp': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Module_A_Temp': round(random.uniform(-3276.8, 3276.7), 1)
                }
            case 'M162_Temperature_Set_3':
                data = {
                    'INV_Torque_Shudder': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Motor_Temp': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Hot_Spot_Temp': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Coolant_Temp': round(random.uniform(-3276.8, 3276.7), 1)
                }
            case 'PEI_Diagnostic_BMS_Data':
                data = {
                    'HI_Temp': random.randint(0, 255),
                    'SOC': random.randint(0, 100),
                    'Pack_Voltage': random.randint(-32768, 32767)
                }
            case 'Dashboard_Random_Shit':
                data = {
                    'Front_Strain_Gauge': random.randint(0, 65535),
                    'Front_Wheel_Speed': random.randint(0, 65535),
                    'TC_Torque_Request': round(random.uniform(0, 6553.5), 1)
                }
            case 'Dashboard_Knobs':
                data = {
                    'Knob1': random.randint(0, 4095),
                    'Knob2': random.randint(0, 4095)
                }
            case 'M169_Internal_Voltages':
                data = {
                    'INV_Ref_Voltage_12_0': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_5_0': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_2_5': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_1_5': round(random.uniform(-327.68, 327.67), 2)
                }

        msg = can.Message(arbitration_id=message.frame_id, data=message.encode(data))
        print(f"{message.name}: {message.decode(msg.data)}")
        process_can(msg)

if __name__ == '__main__':
    threading.Thread(target=test_can_stream, daemon=True).start()

dashboard.root.title('FE12 Dashboard - Test Mode')
dashboard.root.state('zoomed')
dashboard.root.mainloop()