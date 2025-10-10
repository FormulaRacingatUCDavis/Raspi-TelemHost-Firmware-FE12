import can
import os
import cantools.database
import time
from queue import Queue
from datetime import datetime
import csv
import config

class DAQEngine:
    def __init__(self):
        # Logging
        self.start_time = None
        self.root = os.path.dirname(os.path.dirname(__file__))
        self.log_path = None

        # CAN configs
        self.can_bus = None
        self.can_src = None
        self.can_q = None

        self.frucd_dbc = None
        self.cm200_dbc = None

        # Dashboard values
        self.bms_state = None
        self.vcu_state = None
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.glv_voltage = None
        self.soc = None
        self.shutdown = None
        self.test = None
        self.throttle2 = None
        self.mc_state = None
        self.speed_MPH = None
        
    def init_can(self, src):
        """
        Initialize CAN bus and logging file
        """
        if src not in ('pcan', 'tcan'):
            raise ValueError(f"Invalid bus '{src}'. Expected 'pcan' or 'tcan'.")
        self.can_src = src

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.start_time = time.time()

        if self.can_src == 'tcan':
            channel = config.tcan['channel']
            interface = config.tcan['interface']
        if self.can_src == 'pcan':
            channel = config.pcan['channel']
            interface = config.pcan['interface']
        
        if channel == 'vcan0' or channel == 'vcan1':
            log_dir = os.path.join(self.root, f'TestLogs/{self.can_src}')
        elif channel == 'can0' or channel == 'can1':
            log_dir = os.path.join(self.root, f'Logs/{self.can_src}')
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, f'{timestamp}.csv')

        self.can_bus = can.interface.Bus(channel=channel, interface=interface)

        frucd_dbc_path = os.path.join(self.root, 'FE12.dbc')
        cm200_dbc_path = os.path.join(self.root, '20240129 Gen5 CAN DB.dbc')

        self.frucd_dbc = cantools.database.load_file(frucd_dbc_path)
        self.cm200_dbc = cantools.database.load_file(cm200_dbc_path)

        self.can_q = Queue()

    def queue_can(self):
        """
        Process CAN bus messages and queue for logging
        """
        while True:
            msg = self.can_bus.recv()
            self.can_q.put(msg)

            if self.can_src == 'tcan':
                continue

            # Decode PCAN messages
            message = None
            for dbc in [self.frucd_dbc, self.cm200_dbc]:
                try:
                    message = dbc.get_message_by_frame_id(msg.arbitration_id)
                    break
                except KeyError:
                    continue
            if message == None:
                continue
            
            data = message.decode(msg.data)

            if dbc == self.frucd_dbc:
                match message.name:
                    case 'Dashboard_Vehicle_State':
                        self.vcu_state = data['State']
                        self.throttle2 = data['Throttle2_Level']
                    case 'PEI_BMS_Status':
                        self.bms_state = data['BMS_Status']
                    case 'PEI_Diagnostic_BMS_Data':
                        self.pack_temp = data['HI_Temp']
                        self.soc = data['SOC']
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
            elif dbc == self.cm200_dbc:
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
                        self.speed_MPH = abs(data['INV_Motor_Speed']) * 0.016349 # = rpm * (60 * pi * Tire Diameter) / (Final Drive Ratio * 63360)

    def log_can(self):
        """
        Log all data as raw CAN messages to a CSV
        """
        csv_file = open(self.log_path, 'w', newline='')
        csv_writer = csv.DictWriter(
            csv_file,
            fieldnames=['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp']
        )

        count = 0
        while True:
            msg = self.can_q.get()

            data_raw = list(msg.data)
            if len(data_raw) > 8:
                continue

            row = {
                'ID': hex(msg.arbitration_id)[2:].upper(),
                'Timestamp': int((msg.timestamp - self.start_time) * 1000)
            }
            for i in range(len(data_raw)):
                row[f'D{i}'] = data_raw[i]
            csv_writer.writerow(row)
            count += 1

            if count == 500:
                csv_file.flush()
                count = 0