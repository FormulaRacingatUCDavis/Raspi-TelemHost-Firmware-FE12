#!/home/frucd/projects/FE12TelemetryHost/.venv/bin/python

# from dashboard import FE12Dashboard
# raspiDashboard = FE12Dashboard('vcan0', 'socketcan')

import socket
import can
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus = can.interface.Bus(channel='vcan0',interface='socketcan')

server.bind(('0.0.0.0', 9999))

server.listen(5)

client, addr = server.accept()

while True:
    msg = bus.recv()
    can_data = {'arbitration_id': msg.arbitration_id, 'data': list(msg.data)}
    json_data = json.dumps(can_data)

    client.send((json_data + '\n').encode('utf-8'))