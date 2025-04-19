#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can
import json

class FE12_CAN_Manager:
    def __init__(self, channel, interface):
        
        print("Instantiating CAN manager...")

        self.can_id = -1
        self.data = None
        
        # self.speed = -1         # Speed [mph]
        # self.vehicle_state = -1      # Vehicle state [LV, Precharge, HV, Drive, ...]
        # self.bms_state = -1 
        # self.glv_voltage = -1    # GLV voltage [V]
        # self.motor_temp = -1     # Motor temperature [C]
        # self.mc_temp = -1        # Motor controller temperature; average [C]
        # self.pack_temp = -1      # Battery temperature [C]
        # self.soc = -1           # State of Charge [%]

        self.VCU_STATE_ID = 0x500
        self.TORQUE_REQUEST_ID = 0x0C0
        self.RANDOM_SHIT_ID = 0x500
        self.PEI_STATUS_ID = 0x387
        self.BMS_STATUS_ID = 0x380
        self.DIAGNOSTIC_BMS_DATA_ID = 0x381
        self.COOLING_LOOP_TEMPS_ID = 0x400
        self.WHEEL_SPEED_REAR_ID = 0x401
        self.COOLING_LOOP_PRESSURES_ID = 0x402
        self.STRAIN_GAUGES_REAR_ID = 0x403
        self.CHARGER_STATUS_ID = 0x18FF50E5
        self.CHARGER_COMMAND_ID = 0x1806E5F4

        self.bus = can.interface.Bus(channel=channel, interface=interface)

    def readMsg(self):
        print("Reading messsage...")

        msg = self.bus.recv()
        self.can_id = msg.arbitration_id

        match self.can_id:
            case self.VCU_STATE_ID:
                if len(msg) < 7:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 7 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'hv_requested': msg.data[0], # 0 = requested, 1 = not requested
                    'throttle_1_level': msg.data[1], # %
                    'throttle_2_level': msg.data[2], # %
                    'brake_level': msg.data[3], # %
                    'vehicle_state': msg.data[4], # LV, Precharge, ...
                    'vcu_ticks': int.from_bytes(msg.data[5:7], "big") # ms
                }
            case self.TORQUE_REQUEST_ID:
                if len(msg) < 8:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 8 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'torque': int.from_bytes(msg.data[0:2], "big"), # Nm * 10
                    'speed': int.from_bytes(msg.data[2:4], "big"), # RPM
                    'direction_command': msg.data[4],  # 0 = reverse, 1 = forward
                    'enable': msg.data[5], # Bit 0 = inverter enable, Bit 1 = discharge enable, Bit 2 = speed mode enable
                    'torque_limit': int.from_bytes(msg.data[6:8], "big") # Nm * 10
                }
            case self.RANDOM_SHIT_ID:
                if len(msg) < 6:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 6 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'front_strain_gauge': int.from_bytes(msg.data[0:2], "big"), # raw ADC
                    'front_wheel_speed': int.from_bytes(msg.data[2:4], "big"), # RPM
                    'tc_torque_request': int.from_bytes(msg.data[4:6], "big") # Nm * 10
                }
            case self.PEI_STATUS_ID:
                if len(msg) < 6:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 6 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'shutdown_circuit_flags': msg.data[0],
                    'current_adc': int.from_bytes(msg.data[1:3], "big"),
                    'current_ref_adc': int.from_bytes(msg.data[3:5], "big")
                }
            case self.BMS_STATUS_ID:
                if len(msg) < 5:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 5 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'bms_status': msg.data[0], # Normal / No error, charge mode, ...
                    'spi_error_flags': int.from_bytes(msg.data[1:3], "big"),
                    'max_faulting_ic_addr': msg.data[3],
                    'comm_break_id': msg.data[4] # Address of IC where communication break occurred
                }
            case self.DIAGNOSTIC_BMS_DATA_ID:
                if len(msg) < 4:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 4 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'hi_temp': msg.data[0], # Maximum temp in degrees C
                    'soc': msg.data[1], # %
                    'pack_voltage': int.from_bytes(msg.data[2:4], "big") # V
                }
            case self.COOLING_LOOP_PRESSURES_ID:
                if len(msg) < 8:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 8 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'inlet_water_temp': int.from_bytes(msg.data[0:2], "big"), # degrees C * 10
                    'outlet_water_temp': int.from_bytes(msg.data[2:4], "big"), # degrees C * 10
                    'air_in_radiator_temp': int.from_bytes(msg.data[4:6], "big"), # degrees C * 10
                    'air_out_radiator_temp': int.from_bytes(msg.data[6:8], "big") # degrees C * 10
                }
            case self.WHEEL_SPEED_REAR_ID:
                if len(msg) < 4:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 4 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'wheel_speed_rr': int.from_bytes(msg.data[0:2], "big"), # clicks per second
                    'wheel_speed_rl': int.from_bytes(msg.data[2:4], "big") # clicks per second
                }
            case self.COOLING_LOOP_PRESSURES_ID:
                if len(msg) < 4:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 4 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'inlet_water_pressure': int.from_bytes(msg.data[0:2], "big"), # PSI * 100
                    'outlet_water_pressure': int.from_bytes(msg.data[2:4], "big") # PSI * 100
                }
            case self.STRAIN_GAUGES_REAR_ID:
                if len(msg) < 8:
                    print(f"\nData length requirement unmet: {msg.data}. Expected at least 8 bytes: {msg}")
                    return
                self.data = {
                    'CAN_ID': self.can_id,
                    'rl_toe_strain_gauge': int.from_bytes(msg.data[0:2], "big"), # raw ADC
                    'rluf_strain_gauge': int.from_bytes(msg.data[2:4], "big"), # raw ADC
                    'rlub_strain_gauge': int.from_bytes(msg.data[4:6], "big"), # raw ADC
                    'rllf_strain_gauge': int.from_bytes(msg.data[6:8], "big") # raw ADC
                }
            case self.CHARGER_STATUS_ID:
                pass
            case self.CHARGER_COMMAND_ID:
                pass
            case _:
                print(f"\nInvalid CAN ID ({self.canID}): {msg}")