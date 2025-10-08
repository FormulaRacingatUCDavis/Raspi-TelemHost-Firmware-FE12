#!/bin/bash
export DISPLAY=:0

# Set up virtual CAN for testing
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
sudo ip link add dev vcan1 type vcan
sudo ip link set up vcan1

# sudo ip link set can0 up type can bitrate 500000
# sudo ip link set can1 up type can bitrate 500000

# Run Python dashboard code
cd /home/frucd/Projects/Raspi-TelemHost-Firmware-FE12/
source .venv/bin/activate
python3 Dashboard/main.py