import can
import csv
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

with open('Test/example.csv', 'r', newline='') as raw_can:
    reader = csv.reader(raw_can)
    for row in reader:
        try:
            can_id = int(row[0], 16)
        except ValueError:
            continue

        data_bytes = []
        for b in row[1:9]:
            if b.strip() == "":
                data_bytes.append(0)
            else:
                try:
                    data_bytes.append(int(b))
                except ValueError:
                    data_bytes.append(0)

        msg = can.Message(
            arbitration_id=can_id,
            data=bytes(data_bytes),
            is_extended_id=False
        )

        bus.send(msg)