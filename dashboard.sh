#!/bin/bash
export DISPLAY=:0

# Run Python dashboard code
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# sudo ip link set can0 up type can bitrate 500000
# sudo ip link set can1 up type can bitrate 500000

cd /home/frucd/projects/Raspi-TelemHost-Firmware-FE12/
source .venv/bin/activate
python3 Dashboard/main.py