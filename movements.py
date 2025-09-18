import serial
import time

#ArduinoUno = serial.Serial("COM7", 9600, timeout=1)


#print("Connected")

def move_with_repeats(command, duration):
        stop = 'S'
        print("Moving ", command)
        start = time.time()
        while time.time() - start < duration:
            ArduinoUno.write(command.encode())
            time.sleep(0.02)  # send every 20 ms (faster than Arduino timeout)
        ArduinoUno.write(stop.encode())

def sign(n):
    return (n > 0) - (n < 0)

print(sign(6) == sign(0))