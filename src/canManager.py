# Speed: Front wheels
# > CAN ID: 500
# > Bytes 5-2

# Vehicle State
# > CAN ID: 766
# > Byte 5

# GLV Voltage (MC_INTERNAL_VOLTS)
# > CAN ID: A9
# > Bytes 7-6

# Motor Temperature (motor_temp)
# > CAN ID: A2
# > Bytes 5-4

# Motor Controller Temperature (mc_temp): Average of Modules A, B, and C
# > CAN ID: A0
# > Module A: Bytes 1-0
# > Module B: Bytes 3-2
# > Module C: Bytes 5-4

# Battery Temperature (PACK_TEMP)
# > CAN ID: 380
# > Byte 0

# State of charge
# > CAN ID: 380
# > Byte 1

import can

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

state_message = {
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

while True:
    msg = bus.recv()
    match hex(msg.arbitration_id):
        case '0x500': # Speed [mph]
            pass
        case '0x766': # Vehicle state [LV, Precharge, HV, Drive, ...]
            state = hex(msg.data[5])
            pass
        case '0x0A9': # GLV voltage [V]
            pass
        case '0x0A2': # Motor temperature [C]
            pass
        case '0x0A0': # Motor controller temperature [C]
            pass
        case '0x380': # Battery temperature [C] and State of Charge [%]
            pass