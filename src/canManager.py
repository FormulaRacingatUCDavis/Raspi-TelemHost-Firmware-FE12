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

def test_can_bus():
    try:
        # Assuming you're using a socketcan interface on 'can0'
        bus = can.interface.Bus(channel='can0', interface='socketcan')
        print("CAN bus initialized successfully!")
    except Exception as e:
        print(f"Error initializing CAN bus: {e}")

test_can_bus()
