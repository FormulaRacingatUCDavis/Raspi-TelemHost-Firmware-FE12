'''
Speed: Front wheels
> CAN ID: 500
> Bytes 5-2

Vehicle State
> CAN ID: 766
> Byte 5

GLV Voltage (MC_INTERNAL_VOLTS)
> CAN ID: A9
> Bytes 7-6

Motor Temperature (motor_temp)
> CAN ID: A2
> Bytes 5-4

Motor Controller Temperature (mc_temp): Average of Modules A, B, and C
> CAN ID: A0
> Module A: Bytes 1-0
> Module B: Bytes 3-2
> Module C: Bytes 5-4

Battery Temperature (PACK_TEMP)
> CAN ID: 380
> Byte 0

State of charge
> CAN ID: 380
> Byte 1
'''

import can

class FE12CANBus:
    def __init__(self, channel, interface):
        self.speed = -1
        self.state = -1
        self.glvVoltage = -1
        self.motorTemp = -1
        self.mcTemp = -1
        self.packTemp = -1
        self.soc = -1

        self.stateMessage = {
            '0x00': 'LV',
            '0x01': 'PRECHARGE',
            '0x02': 'HV',
            '0x03': 'DRIVE',
            '0x05': 'STARTUP',
            '0x81': 'DRVREQUEST',           # FAULT: Drive request from LV
            '0x82': 'PRCHTOUT',             # FAULT: Precharge timeout
            '0x83': 'BRKFAULT',             # FAULT: Brake not pressed
            '0x84': 'HVDISDRIVE',           # FAULT: HV disabled while driving
            '0x85': 'SENSFAULT',            # FAULT: Sensor discrepancy
            '0x86': 'BSPDTRIP',             # FAULT: BSPD tripped
            '0x87': 'CKTOPEN',              # FAULT: Shutdown Circuit Open
            '0x88': 'UNCALIBRTD',           # FAULT: Uncalibrated
            '0x89': 'BSPDHARD',             # FAULT: Hard BSPD
            '0x8A': 'MCFAULT'               # FAULT: MC Fault
        }

        self.idHandlers = {
            '0x500': self.handleSpeed,      # Speed [mph]
            '0x766': self.handleState,      # Vehicle state [LV, Precharge, HV, Drive, ...]
            '0xA9': self.handleGLVVoltage,  # GLV voltage [V]
            '0xA2': self.handleMotorTemp,   # Motor temperature [C]
            '0xA0': self.handleMCTemp,      # Motor controller temperature; average [C]
            '0x380': self.handlePackTemp    # Battery temperature [C] and State of Charge [%]
        }

        self.bus = can.interface.Bus(channel=channel, interface=interface)

    def handleSpeed(self, msg):
        self.speed = int.from_bytes(msg.data[5:1:-1], "big")

    def handleState(self, msg):
        self.state = self.stateMessage[hex(msg.data[5])]

    def handleGLVVoltage(self, msg):
        self.glvVoltage = int.from_bytes(msg.data[8:6:-1], "big")

    def handleMotorTemp(self, msg):
        self.motorTemp = int.from_bytes(msg.data[5:3:-1], "big")

    def handleMCTemp(self, msg):
        self.mcTemp = sum((
        int.from_bytes(msg.data[1::-1], "big"),         # Module A
        int.from_bytes(msg.data[3:1:-1], "big"),        # Module B
        int.from_bytes(msg.data[5:3:-1], "big")         # Module C
        )) / 3

    def handlePackTemp(self, msg):
        self.packTemp = msg.data[0]
    
    def handleSOC(self, msg):
        self.soc = msg.data[1]

    def readMsg(self):
        msg = self.bus.recv()
        canID = hex(msg.arbitration_id)
        try:
            self.idHandlers[canID](msg)
        except:
            print(f"Unknown CAN ID: {canID}")