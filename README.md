# Raspberry Pi Telemetry Host (FE12)
Displays and logs telemetry data received over CAN using a Raspberry Pi.

## Set Up
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Dashboard
```
python Dashboard/main.py
```

## Run Web Server (on Raspberry Pi)
```
cd WebGUI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

![DashboardScreenshot](Assets/example.png)