import platform

if platform.system() == 'Linux':
    tcan = dict(
        channel = 'can1',
        interface = 'socketcan'
    )
    pcan = dict(
        channel = 'can0',
        interface = 'socketcan'
    )
else:
    tcan = dict(
        channel = 'vcan1',
        interface = 'virtual'
    )
    pcan = dict(
        channel = 'vcan0',
        interface = 'virtual'
    )