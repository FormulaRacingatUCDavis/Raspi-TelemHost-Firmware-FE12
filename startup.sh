#!/bin/bash
export DISPLAY=:0

# Run Python dashboard code
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
cd /home/frucd/projects/Raspi-TelemHost-Firmware-FE12/
source .venv/bin/activate
python3 src/main.py