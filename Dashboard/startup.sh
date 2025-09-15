#!/bin/bash
export DISPLAY=:0

# Run C++ dashboard code
cd /home/frucd/projects/FE13FW-Display
./Build/frucd_raspi_dash

# Run Python dashboard code (backup)
# cd /home/frucd/projects/Raspi-TelemHost-Firmware-FE12/
# source .venv/bin/activate
# python3 src/main.py