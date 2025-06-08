import can
import os
import cantools.database
import time
import ADS1263
import RPi.GPIO as GPIO
from queue import Queue
from datetime import datetime
import csv

class TelemetryManager:
    def __init__(self):
        self.root = os.path.dirname(os.path.dirname(__file__))
        self.csv_file = None
        self.csv_writer = None

        self.adc = None
        self.bms_state = None
        self.vcu_state = None
        self.motor_temp = -1
        self.mc_temp = -1
        self.pack_temp = -1
        self.speed_RPM = None
        self.glv_voltage = None
        self.soc = None
        self.knob1_adc = 0
        self.knob2_adc = 0

        self.can_data = None
        self.can_queue = None
        self.db = None

    def csv_init(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = os.path.join(self.root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f'{timestamp}.csv')
        self.csv_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp'])
        self.csv_writer.writeheader()

    def adhat_init(self):
        self.adc = ADS1263.ADS1263()
        if (self.adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1):
            exit()
        self.adc.ADS1263_SetMode(0)

    def can_init(self, channel, interface, dbc_file):
        self.bus = can.interface.Bus(channel = channel, interface = interface)
        dbc_path = os.path.join(os.path.dirname(__file__), dbc_file)
        self.db = cantools.database.load_file(dbc_path)
        self.can_data = {msg.name: None for msg in self.db.messages}
        self.can_queue = Queue()


    def process_can(self):
        while True:
            msg = self.bus.recv()

            try:
                message = self.db.get_message_by_frame_id(msg.arbitration_id)
                data = message.decode(msg.data)

                self.can_queue.put(msg)

                match message.name:
                    case 'Dashboard_Vehicle_State':
                        self.vcu_state = data['State']
                    case 'PEI_BMS_Status':
                        self.bms_state = data['BMS_Status']
                    case 'M160_Temperature_Set_1':
                        self.mc_temp = (data['INV_Module_A_Temp'] + data['INV_Module_B_Temp'] + data['INV_Module_C_Temp']) / 3
                    case 'M162_Temperature_Set_3':
                        self.motor_temp = data['INV_Motor_Temp']
                    case 'PEI_Diagnostic_BMS_Data':
                        self.pack_temp = data['HI_Temp']
                        self.soc = data['SOC']
                    case 'Dashboard_Random_Shit':
                        self.speed_RPM = data['Front_Wheel_Speed']
                    case 'Dashboard_Knobs':
                        self.knob1_adc = data['Knob1']
                        self.knob2_adc = data['Knob2']
                    case 'M169_Internal_Voltages':
                        self.glv_voltage = data['INV_Ref_Voltage_12_0']
            except KeyError:
                pass

    def log_can(self):
        # Log CAN message to CSV
        while True:
            msg = self.can_queue.get()
            data_bytes = list(msg.data)
            row = {
                'ID': hex(msg.arbitration_id)[2:].upper(),
                'Timestamp': int(time.time() * 1000)
            }
            for i in range(len(data_bytes)):
                row[f'D{i}'] = f"{data_bytes[i]:02X}"
            self.csv_writer.writerow(row)
            self.csv_file.flush()

    def log_adc(self, n):
        # Log ADC data to CSV
        while True:
            adc_data = [self.adc.ADS1263_GetChannalValue(i) for i in range(n)]
            row = {
                'ID': hex(0x0382)[2:].upper(),
                'Timestamp': int(time.time() * 1000)
            }
            for i in range(len(adc_data)):
                row[f'D{i}'] = f"{adc_data[i]:02X}"
            self.csv_writer.writerow(row)
            self.csv_file.flush()