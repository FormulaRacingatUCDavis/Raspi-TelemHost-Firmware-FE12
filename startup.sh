sudo modprobe vcan
sudo ip link set vcan0 down
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

sudo modprobe can
sudo modprobe can_raw
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 500000 restart-ms 100 loopback on
sudo ip link set up can0

export DISPLAY=:0

cd /home/ryan/Projects/Raspi-TelemHost-Firmware-FE12
source .venv/bin/activate
python src/main.py