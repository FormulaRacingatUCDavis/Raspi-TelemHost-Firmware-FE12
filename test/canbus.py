import random
import os
import can
import cantools


# Test CAN messages 0 to N
N = 11
# Or test one CAN message if N = None
MSG_IND = 7


fe_dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
cm200_dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', '20230606 Gen5 CAN DB.dbc'))
cm200_db = cantools.database.load_file(cm200_dbc_path)
fe_db = cantools.database.load_file(fe_dbc_path)
bus = can.interface.Bus(channel='vcan0', interface='socketcan')

msg_names = [
    'M160_Temperature_Set_1',
    'M162_Temperature_Set_3',
    'PEI_Diagnostic_BMS_Data',
    'Dashboard_Random_Shit',
    'M169_Internal_Voltages',
    'PEI_Status',
    'M171_Fault_Codes',
    'M165_Motor_Position_Info',
    'M172_Torque_And_Timer_Info',
    'Dashboard_Vehicle_State',
    'PEI_BMS_Status',
    'Dashboard_Inputs'
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

    for db_name, db in [('fe', fe_db), ('cm200', cm200_db)]:
        try:
            message = db.get_message_by_name(msg_name)
            source_db = db_name
            break  # Exit loop once found
        except KeyError:
            continue

    if source_db == 'fe':
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
            case 'Dashboard_Inputs':
                data = {
                    'Knob1': random.randint(0, 100),
                    'Knob2': random.randint(0, 100),
                    'OVERTAKE': random.randint(0, 1),
                    'MARKER': random.randint(0, 1),
                    'TC': random.randint(0, 1),
                    'DISPLAY_MODE': random.randint(0, 1)
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
    elif source_db == 'cm200':
        match msg_name:
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
            case 'M169_Internal_Voltages':
                data = {
                    'INV_Ref_Voltage_12_0': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_5_0': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_2_5': round(random.uniform(-327.68, 327.67), 2),
                    'INV_Ref_Voltage_1_5': round(random.uniform(-327.68, 327.67), 2)
                }
            case 'M171_Fault_Codes':
                data = {
                    'INV_Post_Fault_Lo': random.randint(0, 65535),
                    'INV_Post_Fault_Hi': random.randint(0, 65535),
                    'INV_Run_Fault_Lo': random.randint(0, 65535),
                    'INV_Run_Fault_Hi': random.randint(0, 65535) 
                }
            case 'M165_Motor_Position_Info':
                data = {
                    'INV_Motor_Angle_Electrical': round(random.uniform(0, 3276.7), 1),
                    'INV_Motor_Speed': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Electrical_Output_Frequency': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Delta_Resolver_Filtered': round(random.uniform(-3276.8, 3276.7), 1)
                }
            case 'M172_Torque_And_Timer_Info':
                data = {
                    'INV_Commanded_Torque': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Torque_Feedback': round(random.uniform(-3276.8, 3276.7), 1),
                    'INV_Power_On_Timer': random.randint(0, 1.28848e07)
                }
            
    encoded = message.encode(data)
    msg = can.Message(arbitration_id=message.frame_id, data=encoded, is_extended_id=False)
    bus.send(msg)
    print(msg)