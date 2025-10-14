#!/bin/bash

cd /home/frucd/projects/Raspi-TelemHost-Firmware/WebGUI
source ../.venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000