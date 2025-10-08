#!/bin/bash

cd /home/frucd/Projects/Raspi-TelemHost-Firmware-FE12/WebServer
source ../.venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000