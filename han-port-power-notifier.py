from py_control_zaptec.turn_on import main as turn_on_zaptec
from py_control_zaptec.turn_off import main as turn_off_zaptec
import datetime
import serial
import requests
 
NTFYSH_PASSWORD = ...
NTFYSH_URL = f"https://ntfy.sh/{NTFYSH_PASSWORD}"
OBIS_SEARCH_BYTES = b'\x01\x00\x01\x07\x00\xff\x06'  # OBIS messages vary from meter brands
 
 
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=2400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=4)
print("Connected to: " + ser.portstr)
 
watt_list = []
hourly_list = []
cur_time = prev_time = datetime.datetime.now()
charger_state = None
 
while True:
    received_bytes = ser.read(1024)
    if received_bytes:
        print('Got %d bytes' % len(received_bytes), end="; ")
        try:
            start_index = received_bytes.index(OBIS_SEARCH_BYTES) + len(OBIS_SEARCH_BYTES)
        except ValueError:
            print("No A+ value found in message.")
            continue
        watt_value_bytes = received_bytes[start_index:start_index + 4]
        watt_value_int = int.from_bytes(watt_value_bytes, "big")
        print(f"Watts: {watt_value_int}")
        watt_list.append(watt_value_int)
        hourly_list.append(watt_value_int)
    else:
        print('Got nothing')
 
    if len(watt_list) % 20 == 1:
        hourly_avg = sum(hourly_list) // len(hourly_list)
        new_charger_state = None
        if hourly_avg < 2000:
            new_charger_state = True
        elif hourly_avg > 3100:
            new_charger_state = False
        print(f"Considering charger input: Hourly avg. {hourly_avg} W, new state: {new_charger_state}, old state: {charger_state}")
        if new_charger_state is not None:
            if charger_state != new_charger_state:
                if new_charger_state:
                    turn_on_zaptec()
                else:
                    turn_off_zaptec()
                print(f"Changed charger state")
                charger_state = new_charger_state
 
    if len(watt_list) == 100:
        max_value = max(watt_list)
        min_value = min(watt_list)
        avg_value = sum(watt_list) // len(watt_list)
        hourly_avg = sum(hourly_list) // len(hourly_list)
        url_suffix = "ny" if hourly_avg >= 3700 else ""
        if url_suffix:
            turn_off_zaptec()  # Just to be sure the it really is turned off
        requests.post(NTFYSH_URL + url_suffix, data=f"Max: {max_value} W, min: {min_value} W, avg: {avg_value} W, hourly avg: {hourly_avg} W")
        watt_list = []
    cur_time = datetime.datetime.now()
    if cur_time.hour != prev_time.hour:
        hourly_avg = sum(hourly_list) // len(hourly_list)
        requests.post(NTFYSH_URL, data=f"Hourly avg {prev_time.hour}-{cur_time.hour}: {hourly_avg} W")
        hourly_list = []
    prev_time = cur_time
