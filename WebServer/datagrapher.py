import csv
import cantools
import matplotlib.pyplot as plt
import os

root = os.path.dirname(os.path.dirname(__file__))
fe_dbc_path = os.path.join(root, "FE12.dbc")
mc_dbc_path = os.path.join(root, "20240129 Gen5 CAN DB.dbc")

mc_dbc = cantools.database.load_file(mc_dbc_path)
fe_dbc = cantools.database.load_file(fe_dbc_path)

def extract_from_csv(filename, category, can_id):
    data_points = []

    message = None
    for db in [fe_dbc, mc_dbc]:
        try:
            message = db.get_message_by_frame_id(can_id)
            break
        except KeyError:
            continue
    if message is None:
        raise ValueError(f"CAN ID {hex(can_id)} not found in provided DBCs")

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 10:
                continue

            try:
                row_id = int(row[0], 16)
            except ValueError:
                continue
            if row_id != can_id:
                continue

            try:
                raw_data = bytes(map(int, row[1:9])) # bytes(int(x, 16) if x else 0 for x in row[1:9])
                ts = float(row[9]) / 1000.0
            except ValueError:
                continue

            decoded = message.decode(raw_data)
            if category in decoded:
                data_points.append((decoded[category], ts))

    return data_points