# Raspberry Pi Telemetry Host (FE12)
Displays and logs telemetry data received over CAN using a Raspberry Pi.

![DashboardScreenshot](assets/example.png)

```ini
# Example Service
[Unit]
Description=FRUCD Dashboard

[Service]
ExecStart=/bin/bash /home/ryan/Projects/Raspi-TelemHost-Firmware-FE12/startup.sh
User=ryan
Restart=always

[Install]
WantedBy=multi-user.target