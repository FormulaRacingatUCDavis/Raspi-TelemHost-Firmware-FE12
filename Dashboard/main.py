#!/home/frucd/projects/Raspi-TelemHost-Firmware-FE12/.venv/bin/python

import threading
import multiprocessing
import time
from ui import Dashboard
from daq import DAQEngine
import platform

def update_dashboard(daq, stop_event, dashboard):
    while not stop_event.is_set():
        dashboard.update_state(daq.vcu_state, daq.bms_state)
        dashboard.update_temp(daq.motor_temp, daq.mc_temp, daq.pack_temp, daq.soc)
        dashboard.update_speed(daq.speed_MPH)
        dashboard.update_glv(daq.glv_voltage)

def process_tcan(stop_event):
    daq = DAQEngine()
    daq.init_can('tcan')

    threading.Thread(target=daq.queue_can, daemon=True).start()
    threading.Thread(target=daq.log_can, daemon=True).start()

    while not stop_event.is_set():
        time.sleep(0.1)

if __name__ == '__main__':
    stop_event = multiprocessing.Event()
    
    tcan_proc = multiprocessing.Process(target=process_tcan, args=(stop_event,))
    tcan_proc.start()

    daq = DAQEngine()
    daq.init_can('pcan')
    dashboard = Dashboard()

    threading.Thread(target=daq.queue_can, daemon=True).start()
    threading.Thread(target=daq.log_can, daemon=True).start()
    threading.Thread(target=update_dashboard, daemon=True, args=(daq, stop_event, dashboard)).start()

    if platform.system() == 'Linux':
        dashboard.root.attributes('-fullscreen', True)
    else:
        dashboard.root.state('zoomed')
        
    dashboard.root.config(cursor="none")

    try:
        dashboard.root.mainloop()
    finally:
        stop_event.set()

    tcan_proc.join()