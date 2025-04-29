#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

import can

class Manager:
    def __init__(self, channel, interface):
        
        print("Instantiating CAN manager...")

        self.canID = -1
        
        self.speed = -1
        self.vcuState = -1
        self.bmsState = -1
        self.glvVoltage = -1
        self.motorTemp = -1
        self.mcTemp = -1
        self.packTemp = -1
        self.soc = -1

        self.idHandlers = {
            '0x500': self.handleSpeed,      # Speed [mph]
            '0x766': self.handleVCUState,      # Vehicle state [LV, Precharge, HV, Drive, ...]
            '0x380': self.handleBMSState,
            '0xa9': self.handleGLVVoltage,  # GLV voltage [V]
            '0xa2': self.handleMotorTemp,   # Motor temperature [C]
            '0xa0': self.handleMCTemp,      # Motor controller temperature; average [C]
            '0x381': self.handlePackTemp    # Battery temperature [C] and State of Charge [%]
        }

        self.bus = can.interface.Bus(channel=channel, interface=interface)

    def readMsg(self):
        print("Reading messsage...")

        msg = self.bus.recv()
        self.canID = hex(msg.arbitration_id)

        if self.canID in self.idHandlers:
            self.idHandlers[self.canID](msg)
        else:
            print(f"\nInvalid CAN ID ({self.canID}): {msg}")

    def lenError(self, msg, size):
        if len(msg) < size:
            print(f"\nData length requirement unmet: {msg.data}. Expected at least {size} bytes: {msg}")

        return len(msg) < size

# Speed: Front wheels
# CAN ID: 500
# Bytes 2-5

    def handleSpeed(self, msg):
        if not self.lenError(msg, 3):
            self.speed = int.from_bytes(msg.data[2:4], "big")

# Vehicle State
# CAN ID: 766
# Byte 5

    def handleVCUState(self, msg):
        if not self.lenError(msg, 5):
            self.vcuState = msg.data[5]

# BMS State
# CAN ID: 380
# Byte 0

    def handleBMSState(self, msg):
        if not self.lenError(msg, 0):
            self.bmsState = msg.data[0]

# GLV Voltage (MC_INTERNAL_VOLTS)
# CAN ID: A9
# Bytes 6-7

    def handleGLVVoltage(self, msg):
        if not self.lenError(msg, 8):
            self.glvVoltage = int.from_bytes(msg.data[6:8], "big")

# Motor Temperature (motor_temp)
# CAN ID: A2
# Bytes 4-5

    def handleMotorTemp(self, msg):
        if not self.lenError(msg, 5):
            self.motorTemp = int.from_bytes(msg.data[4:6], "big")

# Motor Controller Temperature (mc_temp): Average of Modules A, B, and C
# CAN ID: A0
# Module A: Bytes 0-1
# Module B: Bytes 2-3
# Module C: Bytes 4-5

    def handleMCTemp(self, msg):
        if not self.lenError(msg, 5):
            self.mcTemp = sum((
            int.from_bytes(msg.data[0:2], "big"),         # Module A
            int.from_bytes(msg.data[2:4], "big"),        # Module B
            int.from_bytes(msg.data[4:6], "big")         # Module C
            )) / 3

# Battery Temperature (PACK_TEMP)
# CAN ID: 381
# Byte 0, 1

    def handlePackTemp(self, msg):
        if not self.lenError(msg, 1):
            self.packTemp = msg.data[0]
            self.soc = msg.data[1]