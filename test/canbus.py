import random
import os
import can
import cantools

dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
db = cantools.database.load_file(dbc_path)
bus = can.interface.Bus(channel='vcan0', interface='socketcan')


# Test CAN messages 0 to N
N = 6
# Or test one CAN message if N = None
MSG_IND = 7


msg_names = [
    'M160_Temperature_Set_1',
    'M162_Temperature_Set_3',
    'PEI_Diagnostic_BMS_Data',
    'Dashboard_Random_Shit',
    'M169_Internal_Voltages',
    'PEI_Status',
    'Dashboard_Vehicle_State',
    'PEI_BMS_Status',
    'Dashboard_Knobs'
]

vcu_states = [
    0x00, 0x01, 0x02,
    0x03, 0x04, # YO WTF
    0x05, 0x81, 0x82,
    0x83, 0x84, 0x85,
    0x86, 0x87, 0x88,
    0x89, 0x8A
]

bms_states = [
    0x00, 0x01,
    0x02, 0x04, 0x05, # YO WTF
    0x08, 0x10, 0x20,
    0x40, 0x80
]

while True:
    if N != None:
        msg_name = msg_names[random.randint(0,N)]
    else:
        msg_name = msg_names[MSG_IND]

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
                'BMS_Status': bms_states[random.randint(0, 4)],
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
        case 'PEI_Status':
            data = {
                'Current_ADC': random.randint(0, 65535),
                'Current_Reference': random.randint(0, 65535),
                'IMD_OK': random.randint(0, 1),
                'BMS_OK': random.randint(0, 1),
                'SHUTDOWN_FINAL': random.randint(0, 1),
                'AIR_NEG': random.randint(0, 1),
                'AIR_POS': random.randint(0, 1),
                'PRECHARGE': random.randint(0, 1),
            }
            
    encoded = message.encode(data)
    msg = can.Message(arbitration_id=message.frame_id, data=encoded, is_extended_id=False)
    bus.send(msg)