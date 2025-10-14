# Raspberry Pi Telemetry Host

## Hardware
| Component | Description |
|------------|-------------|
| Raspberry Pi 4 Model B | Running Debian 12 (Bookworm) with Python 3.11 |
| [Waveshare 2-CH CAN HAT](https://www.waveshare.com/wiki/2-CH_CAN_HAT) | Dual MCP2515 SPI CAN interface for vehicle data |
| [Waveshare High-Precision ADC HAT](https://www.waveshare.com/wiki/High-Precision_AD_HAT) | ADS1263 24-bit ADC for high-resolution analog sensor input |
| [4" IPS Touchscreen LCD Display (800×480)](https://www.amazon.com/dp/B07XBVF1C9) | HDMI touchscreen display for dashboard |
| [Panda PAU0D AC1200 USB Wi-Fi Adapter](https://www.amazon.com/Panda-Wireless%C2%AE-Wireless-Adapter-Antennas/dp/B0B2QD6RPX) | Dual-band Wi-Fi adapter for wireless telemetry |
| [x2 RP-SMA 22 dBi Wi-Fi Antennas](https://www.amazon.com/Kaunosta-Universal-Omni-Directional-Extension-Wireless/dp/B08LPPML46) | High-gain antennas for extended Wi-Fi range |

## Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Dashboard Example
![DashboardScreenshot](Assets/example.png)