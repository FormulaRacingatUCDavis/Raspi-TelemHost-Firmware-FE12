#!/bin/bash
export DISPLAY=:0

# Wait for display (LCD or VNC)
for i in {1..20}; do
    if [ -S /tmp/.X11-unix/X0 ]; then
        echo "Display ready"
        break
    fi
    echo "Waiting for display"
    sleep 2
done

# Set up virtual CAN for testing
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
sudo ip link add dev vcan1 type vcan
sudo ip link set up vcan1

# Set up CAN channels
sudo ip link set can0 up type can bitrate 500000
sudo ip link set can1 up type can bitrate 500000

# Run dashboard if display available, else fallback
cd /home/frucd/Projects/Raspi-TelemHost-Firmware-FE12/
source .venv/bin/activate

if [ -S /tmp/.X11-unix/X0 ]; then
    echo "Starting dashboard"
    python3 Dashboard/main.py
else
    echo "No display found"
fi