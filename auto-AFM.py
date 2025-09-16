import pyautogui
from computervision_new import findBiggestSkincellFileName, onSkincellFile


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

def servomove(move_distance, calibration_factor, backlash):
    x, y = move_distance
    stop = 'S'

    def move_with_repeats(command, duration):
        print("Moving ", command)
        start = time.time()
        while time.time() - start < duration:
            ArduinoUno.write(command.encode())
            time.sleep(0.02)  # send every 20 ms (faster than Arduino timeout)
        ArduinoUno.write(stop.encode())

    if y < 0:
        move_with_repeats('U', abs(y) * calibration_factor + backlash[1])
    elif y > 0:
        move_with_repeats('D', abs(y) * calibration_factor + backlash[1])

    if x > 0:
        move_with_repeats('R', abs(x) * calibration_factor + backlash[0])
    elif x < 0:
        move_with_repeats('L', abs(x) * calibration_factor + backlash[0])

def sign(n):
    return (n > 0) - (n < 0)

def tupleSubtract(t1, t2):
    return t1[0] - t2[0] , t1[1] - t2[1]

def scan():
    print("Scanning is not yet implemented") #//TODO

def saveImage(): #Highly sensitive to screen sizing //TODO
    print("Attept to autosave")
    pyautogui.moveTo(-336, 261, duration=0.2)
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


### Setup ###
move_distance = (0, 0)
last_move_distance = (0, 0)
calibration_factor = 0.004  # Scale of pixels to distance movement
backlash_x_constant = 2.45
backlash_y_constant = 2.8


### Loop ###
while True: 

    saveImage()

    #Need time for new file to appear in windows
    print("Saving....")
    time.sleep(1)

    oncell = onSkincellFile("images/currentPosition.JPG")
    print("Currently on skincell is: ", oncell)

    if not oncell:
        print("Moving to get onto skincell")
        next_point = findBiggestSkincellFileName("images/currentPosition.JPG")
        print("Biggest nearby skincell detected at ", next_point)

        current_cantelever_position = (298,319) #This should be automated //TODO
        last_movedistance = move_distance
        move_distance = tupleSubtract(next_point,current_cantelever_position)
        print("Distance to move ", move_distance)

        ##Would like to only use 1 single Arduino //TODO get code for "Uno"

        # Determine backlash based on direction change
        backlash_x = backlash_x_constant if sign(move_distance[0]) != sign(last_move_distance[0]) else 0
        backlash_y = backlash_y_constant if sign(move_distance[1]) != sign(last_move_distance[1]) else 0
        backlash_constant = (backlash_x, backlash_y)

        print("Current applied backlash: ", backlash_constant)
        servomove(move_distance, calibration_factor, backlash_constant)

    elif oncell:
        print("We are on a skincell, so we scan!")
        scan()
    

    print("End of loop! Sleeping.")
    time.sleep(5)
    print("Done sleeping!")