import can
import os
import cantools.database
from cantools.database.can.signal import NamedSignalValue
import random
from queue import Queue
import sqlite3

class TelemetryManager:
    """Manages telemetry data received by Raspberry Pi Telemetry Host."""

    def __init__(self):
        # Initialize CAN bus and load DBC files for decoding
        self.can_bus = can.interface.Bus(channel = 'test', interface = 'virtual', receive_own_messages=True)
        self.can_queue = Queue()
        self.fe_dbc = cantools.database.load_file(os.path.join(os.path.dirname(__file__), 'FE12.dbc'))
        self.mc_dbc = cantools.database.load_file(os.path.join(os.path.dirname(__file__), '20240129 Gen5 CAN DB.dbc'))

        self.conn = None
        self.cursor = None

    def queue_can(self):
        """Queue CAN messages"""

        while True:
            msg = self.can_bus.recv()
            self.can_queue.put(msg)

    def log_can(self):
        """Decode CAN messages from queue then log it to SQLite database."""

        # Initialize SQLite database for logging telemetry data
        self.conn = sqlite3.connect('telemetry_data.db')
        self.cursor = self.conn.cursor()

        for dbc in [self.fe_dbc, self.mc_dbc]:
            for message in dbc.messages:
                columns = ['Timestamp REAL']
                for signal in message.signals:
                    columns.append(f'{signal.name} REAL')

                sql = f"""
                CREATE TABLE IF NOT EXISTS {message.name} (
                    {', '.join(columns)}
                )
                """
                self.cursor.execute(sql)

        self.conn.commit()

        # Log CAN messages
        buffer_count = 0
        while True:
            msg = self.can_queue.get()

            # Decode CAN message using either DBC file
            for dbc in [self.fe_dbc, self.mc_dbc]:
                try:
                    message = dbc.get_message_by_frame_id(msg.arbitration_id)
                    break
                except KeyError:
                    continue

            table = message.name
            timestamp = msg.timestamp
            data = message.decode(msg.data)

            # Normalize data
            clean_data = {
                k: (str(v) if isinstance(v, NamedSignalValue) else v)
                for k, v in data.items()
            }

            # Prepare SQL insert
            columns = ['Timestamp'] + list(clean_data.keys())
            values = [timestamp] + list(clean_data.values())
            placeholders = ', '.join(['?'] * len(values))

            sql = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({placeholders})
            """

            try:
                self.cursor.execute(sql, values)
                buffer_count += 1

                # Commit every 100 messages
                if buffer_count >= 100:
                    self.conn.commit()
                    buffer_count = 0

                print(f'Queued {table}: {clean_data}')

            except Exception as e:
                print(f'Error logging {table}: {e}')

            print(clean_data)
            
    def simulate_can(self):
        """Simulate FE12 CAN bus."""

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
            msg_name = msg_names[random.randint(0,11)]

            for db in [self.fe_dbc, self.mc_dbc]:
                try:
                    message = db.get_message_by_name(msg_name)
                    break
                except KeyError:
                    continue

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
                case 'Dashboard_Knobs':
                    data = {
                        'Knob1': random.randint(0, 4095),
                        'Knob2': random.randint(0, 4095),
                        'Button': random.randint(0, 1)
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
                        'PRECHARGE': random.randint(0, 1)
                    }
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
            self.can_bus.send(msg)