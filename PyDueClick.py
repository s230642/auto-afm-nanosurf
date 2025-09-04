import serial
import time

ser = serial.Serial("COM9", 9600, timeout=1)

# Wait for Arduino to be ready
while True:
    print("waiting on arduino")
    time.sleep(1)
    line = ser.readline().decode().strip()
    if line == "READY":
        break

print("Sending click...")
ser.write(b"CLICK\n")
