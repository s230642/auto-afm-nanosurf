import pyautogui
from computervision_new import findBiggestSkincellFileName, onSkincellFile, centering


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
    if move_distance == None:
        return
    x, y = move_distance
    stop = 'S'

    def move_with_repeats(command, duration):
        print("Moving ", command)
        start = time.time()
        while time.time() - start < duration:
            ArduinoUno.write(command.encode())
            time.sleep(0.01)  # send every 10 ms (faster than Arduino timeout)
        ArduinoUno.write(stop.encode())

    if y < 0:
        if backlash[1]!=0:
            print("Doing backlash compensation")
            move_with_repeats('U', backlash[1])
            print("Backlash movement done")
            time.sleep(1)

        print("Starting linear move")

        move_with_repeats('U', abs(y) * calibration_factor[1])

    elif y > 0:
        if backlash[1]!=0:
            print("Doing backlash compensation")
            move_with_repeats('D', backlash[1])
            print("Backlash movement done")
            time.sleep(1)

        print("Starting linear move")

        move_with_repeats('D', abs(y) * calibration_factor[1])
    print("Swapping axis")
    time.sleep(2)
    if x > 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('R', backlash[0])
            print("Backlash movement done")
            time.sleep(1)

        print("Starting linear move")

        move_with_repeats('R', abs(x) * calibration_factor[0])


    elif x < 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('L', backlash[0])
            print("Backlash movement done")
            time.sleep(1)
        print("Starting linear move")
        move_with_repeats('L', abs(x) * calibration_factor[0])


def sign(n):
    return (n > 0) - (n < 0)

def tupleSubtract(t1, t2):
    if t1 == None or t2 == None:
        return None
    return t1[0] - t2[0] , t1[1] - t2[1]

def scan():
    aprooach_button = -1588, 82 #Screen location
    print("Starting approach and then imageing")
    pyautogui.moveTo(aprooach_button[0] , aprooach_button[1], duration=0.2)
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")
    print("For now, wait 4 minutes, then press finish")
    time.sleep(60*4)
    pyautogui.moveTo(-1330, 114, duration=0.2) #FINISH button
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")
    time.sleep(1)
    pyautogui.moveTo(-980, 540, duration=0.2) #ok button
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")
    print("Now wait for image to finish")
    for i in range(16):
        print("there is", 16-i, "minutes left of scanning")
        time.sleep(60)
    print("We should be done imaging now!, stopping")
    #Withdraw twice //TODO
    #print("Withdrawing")
    #pyautogui.moveTo(-1549, 78, duration=0.2)
    #time.sleep(1)
    #print("Sending click...")
    #ArduinoDue.write(b"CLICK\n")
    #time.sleep(20)
    print("Withdrawing")
    pyautogui.moveTo(-1549, 78, duration=0.2) #Retract button
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")
    time.sleep(20)
    print("Scan and withdraw done")


def saveImage(): #Highly sensitive to screen sizing //TODO
    print("Attept to autosave")
    pyautogui.moveTo(-253, 258, duration=0.2)
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

    pyautogui.moveTo( -488, 789, duration=0.2)
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

    pyautogui.moveTo(-913, 529, duration=0.2)
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")

################################
##########   RUNCODE   #########
################################


### Setup ###
move_distance = (0, 0)
last_move_distance = (0, 0)
calibration_factor_x = 0.0082  # seconds/ pixel # Scale of pixels to distance movement
calibration_factor_y = 0.0082  # Scale of pixels to distance movement
backlash_x_constant = 1.40
backlash_y_constant = 1.40
movement_pixel_budget = 2500 # Estimate, //TODO test correctness of this

movesum_x = 0 #This can be changed for custom starting positions
movesum_y = 0 #Custom starting positions are any position not in the center of the sample


just_scanned = False
calibration_factor = calibration_factor_x , calibration_factor_y #Tuple up for compact code

print("Doing backlash calibration")
move_distance = (1,1) #Custom for first calibration round
last_move_distance = move_distance
print("(Last) move distance set to (1 ,1 )")
backlash_constant = (backlash_x_constant, backlash_y_constant)
servomove(move_distance, calibration_factor, backlash_constant)
time.sleep(1)
print("Backlash calibration done")

### Loop ###
while True: 
    print(f"Current budget for movement is: ( {movesum_x} , {movesum_y} )" )
    saveImage()

    #Need time for new file to appear in windows
    print("Saving....")
    time.sleep(1)

    oncell = onSkincellFile("images/currentPosition.JPG")
    print("Currently on skincell is: ", oncell)

    if oncell and (not just_scanned):
        print("We are on a skincell, apply final centering!")

        coordinates, _ = centering()
        current_cantelever_position = (305,310) #This should be automated //TODO
        move_distance = tupleSubtract(coordinates,current_cantelever_position)
        print("Distance to move for centering", move_distance) ## //TODO Maybe its clever to only move half the distance? This way we can keep some bias to the initial endpoint
        if coordinates != None: 
            backlash_x = backlash_x_constant if sign(move_distance[0]) != sign(last_move_distance[0]) else 0
            backlash_y = backlash_y_constant if sign(move_distance[1]) != sign(last_move_distance[1]) else 0
            backlash_constant = (backlash_x, backlash_y)
        
            print("Current applied backlash: ", backlash_constant)
            print("Centering!")
            servomove(move_distance, calibration_factor, backlash_constant)
            last_move_distance = move_distance
            time.sleep(1.5)

        print("Checking we still on skin")
        saveImage()
        #Need time for new file to appear in windows
        print("Saving....")
        time.sleep(1)

        oncell = onSkincellFile("images/currentPosition.JPG")
        if oncell:
            just_scanned = True
            print("Starting scan!")
            scan()

    else:
        #Movement code
        print("Moving to get onto skincell")
        just_scanned = False
        next_point = findBiggestSkincellFileName("images/currentPosition.JPG")
        print("Biggest nearby skincell detected at ", next_point)
        if next_point!=None:
            current_cantelever_position = (305,310) #This should be automated //TODO
            
            move_distance = tupleSubtract(next_point,current_cantelever_position)

            print("Distance to move ", move_distance)


            ##Would like to only use 1 single Arduino //TODO get code for "Uno"

        else: # we dont have target 
            lastX , lastY = last_move_distance
            move_distance = lastX * -2 , lastY * -2
            
            print("We didnt find any targets, going back")

       
           
        backlash_x = backlash_x_constant if sign(move_distance[0]) != sign(last_move_distance[0]) else 0
        backlash_y = backlash_y_constant if sign(move_distance[1]) != sign(last_move_distance[1]) else 0
        last_move_distance = move_distance
        backlash_constant = (backlash_x, backlash_y)
        if (abs(movesum_x+move_distance[0]) > movement_pixel_budget) or (abs(movesum_y+move_distance[1]) > movement_pixel_budget):
            print("We cannot move this distance, too close to edge!")
            if movesum_x>(movement_pixel_budget-500): #Too far east
                move_distance = (-500, move_distance[1])
            if -1*movesum_x>(movement_pixel_budget-500): #Too far west
                move_distance = (500, move_distance[1])
            if movesum_y>(movement_pixel_budget-500): #Too far south
                move_distance = (move_distance[0],-500)
            if -1*movesum_y>(movement_pixel_budget-500): #Too far north
                move_distance = (move_distance[0],500)

        
        movesum_x+=move_distance[0]
        movesum_y+=move_distance[1]    
        print("Current applied backlash: ", backlash_constant)
        
        servomove(move_distance, calibration_factor, backlash_constant)


    print("End of loop! Sleeping.")
    time.sleep(4) #Gives time for the servoes to move
    print("Done sleeping!")

