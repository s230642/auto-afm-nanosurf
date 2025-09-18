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
        if backlash[1]!=0:
            print("Doing backlash compensation")
            move_with_repeats('U', backlash[1])
            print("Backlash movement done")
        time.sleep(3)
        print("Starting linear move")

        move_with_repeats('U', abs(y) * calibration_factor[1])

    elif y > 0:
        if backlash[1]!=0:
            print("Doing backlash compensation")
            move_with_repeats('D', backlash[1])
            print("Backlash movement done")
        time.sleep(3)
        print("Starting linear move")

        move_with_repeats('D', abs(y) * calibration_factor[1])

    if x > 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('R', backlash[0])
            print("Backlash movement done")
        time.sleep(3)
        print("Starting linear move")

        move_with_repeats('R', abs(x) * calibration_factor[0])


    elif x < 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('L', backlash[0])
            print("Backlash movement done")
        time.sleep(3)
        print("Starting linear move")
        move_with_repeats('L', abs(x) * calibration_factor[0])


def sign(n):
    return (n > 0) - (n < 0)

def tupleSubtract(t1, t2):
    return t1[0] - t2[0] , t1[1] - t2[1]

def scan():
    print("Scanning is not yet implemented") #//TODO

def saveImage(): #Highly sensitive to screen sizing //TODO
    print("Attept to autosave")
    pyautogui.moveTo(-373, 268, duration=0.2)
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
calibration_factor_x = 0.0091  # Scale of pixels to distance movement
calibration_factor_y = 0.0079  # Scale of pixels to distance movement
backlash_x_constant = 1.6
backlash_y_constant = 1.5

just_scanned = False
calibration_factor = calibration_factor_x , calibration_factor_y #Tuple up for compact code

### Loop ###
while True: 

    saveImage()

    #Need time for new file to appear in windows
    print("Saving....")
    time.sleep(1)

    oncell = onSkincellFile("images/currentPosition.JPG")
    print("Currently on skincell is: ", oncell)

    if oncell and (not just_scanned):
        print("We are on a skincell, so we scan!")
        just_scanned = True
        scan()

    else:
        print("Moving to get onto skincell")
        next_point = findBiggestSkincellFileName("images/currentPosition.JPG")
        print("Biggest nearby skincell detected at ", next_point)

        current_cantelever_position = (298,319) #This should be automated //TODO
        last_move_distance = move_distance
        move_distance = tupleSubtract(next_point,current_cantelever_position)
        print("Distance to move ", move_distance)

        ##Would like to only use 1 single Arduino //TODO get code for "Uno"

        # Determine backlash based on direction change
        if last_move_distance!=(0,0): #Dont go on first round
            backlash_x = backlash_x_constant if sign(move_distance[0]) != sign(last_move_distance[0]) else 0
            backlash_y = backlash_y_constant if sign(move_distance[1]) != sign(last_move_distance[1]) else 0
            backlash_constant = (backlash_x, backlash_y)
       
            print("Current applied backlash: ", backlash_constant)
            servomove(move_distance, calibration_factor, backlash_constant)
        else:
            print("this is first round")
            print("Doing backlash calibration")
            move_distance = (1,1) #Custom for first calibration round
            print("(Last) move distance set to (1 ,1 )")
            backlash_constant = (backlash_x_constant, backlash_y_constant)
            servomove(move_distance, calibration_factor, backlash_constant)
            time.sleep(1)
            print("Backlash calibration done")
    
    

    print("End of loop! Sleeping.")
    time.sleep(7) #Can be lowered for production runs
    print("Done sleeping!")