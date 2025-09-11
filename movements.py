import serial
import time

ArduinoUno = serial.Serial("COM7", 9600, timeout=1)


print("Connected")


data = 'U'  # string you want to send

for i in range(10):
    ArduinoUno.write(data.encode())  # encode string to bytes before writing
    print("Sending U")
    time.sleep(0.5)

