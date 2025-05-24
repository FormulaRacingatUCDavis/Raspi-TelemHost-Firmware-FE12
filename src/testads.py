import time
import ADS1263
import RPi.GPIO as GPIO

REF = 3.3

adc = ADS1263.ADS1263()

if (adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1):
    exit()

adc.ADS1263_SetMode(0)

while True:
    raw = adc.ADS1263_GetChannalValue(0)
    if raw >> 31 == 1:
        voltage = REF * 2 - raw * REF / 0x80000000
    else:
        voltage = raw * REF / 0x7fffffff

    print(f"\rADC1 IN0 = {voltage: .6f} V", end="", flush=True)
    time.sleep(0.01)