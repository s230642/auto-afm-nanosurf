import pyautogui
from computervision_new import findBiggestSkincellFileName


##Arduino setup
import serial
import time

ArduinoUno = serial.Serial("COM7", 9600, timeout=1)
ArduinoDue = serial.Serial("COM6", 9600, timeout=1)

# Wait for Arduino to be ready
while True:
    print("waiting on arduino")
    time.sleep(1)
    line = ArduinoDue.readline().decode().strip()
    if line == "READY":
        break

def tupleSubtract(t1, t2):
    return t1[0] - t2[0] , t1[1] - t2[1]

def saveImage(): #Highly sensitive to screen sizing //TODO
    print("Attept to autosave")
    pyautogui.moveTo(-364, 186, duration=0.2)
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

    pyautogui.moveTo(-347, 690, duration=0.2)
    time.sleep(2)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

    pyautogui.moveTo(-913, 529, duration=0.2)
    time.sleep(2)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

################################
##########   RUNCODE   #########
################################

saveImage()
next_point = findBiggestSkincellFileName("images\currentPosition.JPG")
print("Biggest nearby skincell detected at ", next_point)

current_cantelever_position = (298,319) #This should be automated //TODO
move_distance = tupleSubtract(next_point,current_cantelever_position)
print("Distance to move ", move_distance)

##Would like to only use 1 single Arduino //TODO get code for "Uno"

data = 'U'  # string you want to send
ArduinoUno.write(data.encode())  # encode string to bytes before writing