# Virtual CAN node
sudo modprobe vcan
sudo ip link set vcan0 down
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# CAN node
sudo modprobe can
sudo modprobe can_raw
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 500000 restart-ms 100 loopback on
sudo ip link set up can0

# export DISPLAY=:0