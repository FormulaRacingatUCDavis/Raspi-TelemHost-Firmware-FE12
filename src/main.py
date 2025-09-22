#!/home/frucd/projects/Raspi-TelemHost-Firmware-FE12/.venv/bin/python

import threading
from dashboard import Dashboard
from telemetry import TelemetryManager


CAN_NODE = 'vcan0'
CAN_INTERFACE = 'socketcan'
FE_DBC_FILE = 'FE12.dbc'
CM200_DBC_FILE = '20240129 Gen5 CAN DB.dbc'


dashboard = Dashboard('FE12 Dashboard')
dashboard.root.bind('<Escape>', lambda event: dashboard.root.destroy())

telem = TelemetryManager()
telem.csv_init(CAN_NODE)
telem.can_init(CAN_NODE, CAN_INTERFACE, FE_DBC_FILE, CM200_DBC_FILE)

def update_dashboard():
    while True:
        dashboard.update_state(telem.vcu_state, telem.bms_state)
        dashboard.update_temp(telem.motor_temp, telem.mc_temp, telem.pack_temp, telem.soc)
        dashboard.update_speed(telem.speed_RPM)
        dashboard.update_glv(telem.glv_voltage)

if __name__ == '__main__':
    threading.Thread(target=telem.process_can, daemon=True).start()
    threading.Thread(target=update_dashboard, daemon=True).start()
    threading.Thread(target=telem.log_can, daemon=True).start()

    dashboard.root.attributes('-fullscreen', True)
    dashboard.root.config(cursor="none")
    dashboard.root.mainloop()