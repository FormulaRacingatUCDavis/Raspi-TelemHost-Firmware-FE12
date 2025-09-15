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
        self.shutdown = None
        self.test = None
        self.throttle2 = None
        self.mc_state = None
        self.motor_speed = None
        self.torque_feedback = None
        self.mode = 0

        self.can_queue = None
        self.fe_db = None
        self.cm200_db = None

        self.adc_data = None
        self.REF = None
        self.n_adc = None

    def csv_init(self, can_node):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if can_node == 'can0':
            log_dir = os.path.join(self.root, 'logs')
        elif can_node == 'vcan0':
            log_dir = os.path.join(self.root, 'testlogs')

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f'{timestamp}.csv')
        self.csv_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=['ID', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Timestamp']
        )
        self.csv_writer.writeheader()

    def adhat_init(self, n, ref):
        self.n_adc = n
        self.adc_data = [0 for _ in range(self.n_adc)]
        self.REF = ref

        try:
            adc = ADS1263.ADS1263()
            if adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1:
                print("ADS1263 init failed")
                return
            adc.ADS1263_SetMode(0)

            # Run self offset calibration once
            adc.ADS1263_WriteCmd(ADS1263.ADS1263_CMD['CMD_SFOCAL1'])
            time.sleep(0.1)

            self.adc = adc
            print("ADS1263 initialized successfully")

        except Exception as e:
            print(f"ADS1263 init exception: {e}")
            self.adc = None

    def can_init(self, channel, interface, fe_dbc_file, cm200_dbc_file):
        self.bus = can.interface.Bus(channel=channel, interface=interface)

        fe_dbc_path = os.path.join(os.path.dirname(__file__), fe_dbc_file)
        cm200_dbc_path = os.path.join(os.path.dirname(__file__), cm200_dbc_file)

        self.fe_db = cantools.database.load_file(fe_dbc_path)
        self.cm200_db = cantools.database.load_file(cm200_dbc_path)

        self.can_queue = Queue()

    def process_can(self):
        while True:
            try:
                # Timeout prevents blocking forever when CAN is quiet/off
                msg = self.bus.recv(timeout=0.01)
            except Exception:
                msg = None

            if msg is None:
                continue

            # try both dbs
            message = None
            source_db = None
            for db_name, db in [('fe', self.fe_db), ('cm200', self.cm200_db)]:
                try:
                    message = db.get_message_by_frame_id(msg.arbitration_id)
                    source_db = db_name
                    break
                except KeyError:
                    continue

            if message is None:
                continue

            data = message.decode(msg.data)
            self.can_queue.put(msg)

            if source_db == 'fe':
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
                    case 'Dashboard_Inputs':
                        self.knob1_adc = data['Knob1']
                        self.knob2_adc = data['Knob2']
                        self.mode = data['DISPLAY_MODE']
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

            elif source_db == 'cm200':
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

    def log_adc(self):
        # Log ADC data to CSV
        def voltage(raw):
            if raw >> 31 == 1:
                return self.REF * 2 - raw * self.REF / 0x80000000
            else: 
                return raw * self.REF / 0x7fffffff

        while True:
            for i in range(self.n_adc):
                self.adc_data[i] = voltage(self.adc.ADS1263_GetChannalValue(i))
            
            row = {
                'ID': hex(0x0382)[2:].upper(),
                'Timestamp': int(time.time() * 1000)
            }
            for i in range(len(self.adc_data)):
                row[f'D{i}'] = f"{self.adc_data[i]}"
            self.csv_writer.writerow(row)
            self.csv_file.flush()

    # def log_all(self):
    #     def voltage(raw):
    #         # signed conversion
    #         val = raw if raw < 0x80000000 else raw - 0x100000000
    #         return (val / 0x7FFFFFFF) * self.REF

    #     last_adc_time = 0
    #     adc_interval = 0.05  # 50 ms

    #     while True:
    #         now = time.time()

    #         # --- Drain all CAN frames available ---
    #         while True:
    #             try:
    #                 msg = self.can_queue.get_nowait()
    #             except Exception:
    #                 break  # empty

    #             row = {
    #                 'ID': hex(msg.arbitration_id)[2:].upper(),
    #                 'Timestamp': int(now * 1000)
    #             }
    #             for i, b in enumerate(msg.data):
    #                 row[f'D{i}'] = f"{b:02X}"
    #             self.csv_writer.writerow(row)

    #         # --- ADC sample at fixed rate ---
    #         if self.adc and now - last_adc_time >= adc_interval:
    #             raw_values = self.adc.ADS1263_GetAll(range(self.n_adc))
    #             self.adc_data = [voltage(v) for v in raw_values]

    #             row = {
    #                 'ID': hex(0x0382)[2:].upper(),
    #                 'Timestamp': int(now * 1000)
    #             }
    #             for i, val in enumerate(self.adc_data):
    #                 row[f'D{i}'] = f"{val:.6f}"
    #             self.csv_writer.writerow(row)

    #             last_adc_time = now

    #         # flush once per loop
    #         self.csv_file.flush()
    #         time.sleep(0.001)  # yield