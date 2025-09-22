import can
import os
import cantools.database
import time
from queue import Queue
from datetime import datetime
import csv

class TelemetryManager:
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(__file__))
        self.csv_file = None
        self.csv_writer = None
        self.start_time = None

        self.bms_state = None
        self.vcu_state = None
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_RPM = None
        self.glv_voltage = None
        self.soc = None
        self.shutdown = None
        self.test = None
        self.throttle2 = None
        self.mc_state = None
        self.motor_speed = None
        self.torque_feedback = None

        self.can_queue = None
        self.frucd_dbc = None
        self.cm200_db = None

    def csv_init(self, can_node):
        """
        Initialize CSV file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.start_time = time.time()

        if can_node == 'can0':
            log_dir = os.path.join(self.root, 'Logs')
        elif can_node == 'vcan0':
            log_dir = os.path.join(self.root, 'TestLogs')

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f'{timestamp}.csv')
        self.csv_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp']
        )

    def can_init(self, channel):
        """
        Initialize CAN interface
        """
        self.bus = can.interface.Bus(channel=channel, interface='socketcan')

        frucd_dbc_path = os.path.join(self.root, 'FE12.dbc')
        cm200_dbc_path = os.path.join(self.root, '20240129 Gen5 CAN DB.dbc')

        self.frucd_dbc = cantools.database.load_file(frucd_dbc_path)
        self.cm200_db = cantools.database.load_file(cm200_dbc_path)

        self.can_queue = Queue()

    def process_can(self):
        """
        Process CAN message
        """
        while True:
            msg = self.bus.recv()
            self.can_queue.put(msg)

            message = None
            source_db = None
            for db in [self.frucd_dbc, self.cm200_db]:
                try:
                    message = db.get_message_by_frame_id(msg.arbitration_id)
                    source_db = db
                    break
                except KeyError:
                    continue
            if message == None:
                continue
            
            data = message.decode(msg.data)

            if source_db == self.frucd_dbc:
                match message.name:
                    case 'Dashboard_Vehicle_State':
                        self.vcu_state = data['State']
                        self.throttle2 = data['Throttle2_Level']
                    case 'PEI_BMS_Status':
                        self.bms_state = data['BMS_Status']
                    case 'PEI_Diagnostic_BMS_Data':
                        self.pack_temp = data['HI_Temp']
                        self.soc = data['SOC']
                    case 'Dashboard_Random_Shit':
                        self.speed_RPM = data['Front_Wheel_Speed']
                    case 'PEI_Status':
                        if data['PRECHARGE'] == 0:
                            self.shutdown = 'PRECHARGE'
                        elif data['AIR_NEG'] == 0:
                            self.shutdown = 'AIR NEG'
                        elif data['AIR_POS'] == 0:
                            self.shutdown = 'AIR POS'
                        elif data['BMS_OK'] == 0:
                            self.shutdown = 'BMS OK'
                        elif data['IMD_OK'] == 0:
                            self.shutdown = 'IMD OK'
                        elif data['SHUTDOWN_FINAL'] == 0:
                            self.shutdown = 'SHUTDOWN FINAL'
                        else:
                            self.shutdown = 'NO SHUTDOWN'
            elif source_db == self.cm200_db:
                match message.name:
                    case 'M160_Temperature_Set_1':
                        self.mc_temp = (
                            data['INV_Module_A_Temp'] +
                            data['INV_Module_B_Temp'] +
                            data['INV_Module_C_Temp']
                        ) / 3
                    case 'M162_Temperature_Set_3':
                        self.motor_temp = data['INV_Motor_Temp']
                    case 'M169_Internal_Voltages':
                        self.glv_voltage = data['INV_Ref_Voltage_12_0']
                    case 'M171_Fault_Codes':
                        if data['INV_Post_Fault_Lo'] != 0 and data['INV_Post_Fault_Hi'] != 0:
                            self.mc_state = hex(data['INV_Post_Fault_Lo'] | (data['INV_Post_Fault_Hi'] << 16))
                        elif data['INV_Run_Fault_Lo'] != 0 and data['INV_Run_Fault_Hi'] != 0:
                            self.mc_state = hex(data['INV_Run_Fault_Lo'] | (data['INV_Run_Fault_Hi'] << 16))
                        else:
                            self.mc_state = None
                    case 'M165_Motor_Position_Info':
                        self.motor_speed = data['INV_Motor_Speed']
                        if self.torque_feedback is not None:
                            self.test = self.motor_speed * self.torque_feedback
                    case 'M172_Torque_And_Timer_Info':
                        self.torque_feedback = data['INV_Torque_Feedback']
                        if self.motor_speed is not None:
                            self.test = self.motor_speed * self.torque_feedback

    def log_can(self):
        """
        Log CAN message to CSV
        """
        while True:
            msg = self.can_queue.get()
            data_bytes = list(msg.data)

            if len(data_bytes) > 8:
                continue

            row = {
                'ID': hex(msg.arbitration_id)[2:].upper(),
                'Timestamp': int((time.time() - self.start_time) * 1000)
            }
            for i in range(len(data_bytes)):
                row[f'D{i}'] = data_bytes[i]
            self.csv_writer.writerow(row)
            self.csv_file.flush()