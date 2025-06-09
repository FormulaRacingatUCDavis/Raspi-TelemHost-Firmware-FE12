import os
import can
import cantools

TESTKNOB = 1

dbc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'FE12.dbc'))
db = cantools.database.load_file(dbc_path)
bus = can.interface.Bus(channel='vcan0', interface='socketcan')

knob = 0
while knob <= 4095:
    message = db.get_message_by_name('Dashboard_Knobs')

    if TESTKNOB == 1:
        data = {'Knob1': knob, 'Knob2': 0}
    elif TESTKNOB == 2:
        data = {'Knob1': 0, 'Knob2': knob}
            
    encoded = message.encode(data)
    msg = can.Message(arbitration_id=message.frame_id, data=encoded, is_extended_id=False)
    bus.send(msg)

    knob += 1