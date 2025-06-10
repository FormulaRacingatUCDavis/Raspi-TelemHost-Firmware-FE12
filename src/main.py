#!/home/frucd/projects/Raspi-TelemHost-Firmware-FE12/.venv/bin/python

import threading
from dashboard import Dashboard
from telemetry import TelemetryManager


CAN_NODE = 'can0'
CAN_INTERFACE = 'socketcan'
FE_DBC_FILE = 'FE12.dbc'
CM200_DBC_FILE = '20230606 Gen5 CAN DB.dbc'
N_ADC = 6
REF = 5
DEBUG_FREE_SLOT = ''
DEBUG_FREE_SLOT_UNIT = ''


dashboard = Dashboard('FE12 Dashboard')
dashboard.root.bind('<Escape>', lambda event: dashboard.root.destroy())

telem = TelemetryManager()
telem.csv_init()
telem.can_init(CAN_NODE, CAN_INTERFACE, FE_DBC_FILE, CM200_DBC_FILE)
telem.adhat_init(N_ADC, REF)

def update_dashboard():
    while True:
        if telem.mode == 0:
            if dashboard.current_frame != dashboard.main_frame:
                dashboard.switch_frame(dashboard.main_frame)
            dashboard.update_state(telem.vcu_state, telem.bms_state)
            dashboard.update_temp(telem.motor_temp, telem.mc_temp, telem.pack_temp, telem.soc)
            dashboard.update_speed(telem.speed_RPM)
            dashboard.update_glv(telem.glv_voltage)
            dashboard.update_knob(telem.knob1_adc, telem.knob2_adc)
        elif telem.mode == 1:
            if dashboard.current_frame != dashboard.debug_frame:
                dashboard.switch_frame(dashboard.debug_frame)
            dashboard.debug(
                telem.soc,
                telem.pack_temp,
                telem.shutdown,
                telem.mc_temp,
                telem.motor_temp,
                telem.mc_state,
                telem.vcu_state,
                telem.glv_voltage,
                telem.test, # Free slot
                DEBUG_FREE_SLOT,
                DEBUG_FREE_SLOT_UNIT
            )
            dashboard.update_knob(telem.knob1_adc, telem.knob2_adc)

if __name__ == '__main__':
    threading.Thread(target=telem.process_can, daemon=True).start()
    threading.Thread(target=update_dashboard, daemon=True).start()
    threading.Thread(target=telem.log_can, daemon=True).start()
    threading.Thread(target=telem.log_adc, daemon=True).start()

    dashboard.root.attributes('-fullscreen', True)
    dashboard.root.config(cursor="none")
    dashboard.root.mainloop()