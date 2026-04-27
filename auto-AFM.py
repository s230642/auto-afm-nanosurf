import pyautogui
from computervision_refactor import findBiggestSkincell, onSkincell
from Backlash_code import primeForMovement
import cv2

##Arduino setup
import serial
import time

ArduinoUno = serial.Serial("COM7", 9600, timeout=1)
ArduinoDue = serial.Serial("COM6", 9600, timeout=1)

##Cam setup
top_view = cv2.VideoCapture(1,cv2.CAP_DSHOW)
top_view.set(cv2.CAP_PROP_FRAME_WIDTH, 648)
top_view.set(cv2.CAP_PROP_FRAME_HEIGHT, 484)

## Camera warm up
for i in range(10):
    _ , current_topview = top_view.read()
    print(i)

print("Camera all warmed up! ")
#cv2.imshow("Test topview", current_topview)
#cv2.waitKey()
#cv2.destroyAllWindows()

# Wait for Arduino to be ready
while True:
    print("waiting on arduino")
    time.sleep(1)
    line = ArduinoDue.readline().decode().strip()
    if line == "READY":
        break

def servomove(move_distance, calibration_factor):
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
        primeForMovement('U', top_view, ArduinoUno)
        move_with_repeats('U', abs(y) * calibration_factor[1])

    elif y > 0:
        primeForMovement('D', top_view, ArduinoUno)
        move_with_repeats('D', abs(y) * calibration_factor[1])
    
    print("Swapping axis")
    time.sleep(2)
    
    if x > 0:
        primeForMovement('R', top_view, ArduinoUno)
        move_with_repeats('R', abs(x) * calibration_factor[0])

    elif x < 0:
        primeForMovement('L', top_view, ArduinoUno)
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

    print("Withdrawing")
    pyautogui.moveTo(-1549, 78, duration=0.2) #Retract button
    time.sleep(1)
    print("Sending click...")
    ArduinoDue.write(b"CLICK\n")
    time.sleep(30)
    print("Scan and withdraw done")


################################
##########   RUNCODE   #########
################################


### Setup ###
images = 12 #Number of images to take
move_distance = (0, 0)
last_move_distance = (0, 0)
calibration_factor_x = 0.0079  # seconds/ pixel # Scale of pixels to distance movement
calibration_factor_y = 0.0079  # Scale of pixels to distance movement
movement_pixel_budget = 1500 

movesum_x = 0 #This can be changed for custom starting positions
movesum_y = 0 #Custom starting positions are any position not in the center of the sample


just_scanned = False
calibration_factor = calibration_factor_x , calibration_factor_y #Tuple up for compact code
scanned_blobs = []
patch = None
images_taken = 0

### Loop ###
while images_taken<20: 
    for _ in range(5):
        rec, current_topview = top_view.read()
    print(f"Current budget for movement is: ( {movesum_x} , {movesum_y} )" )
    if not rec:
        print("failed to talk to optics\nexiting...")
        break
    #Need time for new file to appear in windows

    oncell = onSkincell(current_topview)
    print("Currently on skincell is: ", oncell)
    
    #cv2.imwrite("Current_cantelever_position.png",current_topview)
    #cv2.imshow("Debugging, topview" , current_topview)
    for j in range(len(scanned_blobs)):
        scaled = cv2.resize(scanned_blobs[j], None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)

        #cv2.imshow(f"{j} scanned patch", scaled)
    #cv2.waitKey()
    #cv2.destroyAllWindows()
    
    
    if oncell and (not just_scanned):
        print("We are on a skincell, apply final centering!")
        #cv2.waitKey()
        coordinates, _ = None , None #centering() TODO centering not implemented in this version
        current_cantelever_position = (295,241) #This should be automated //TODO
        move_distance = tupleSubtract(coordinates,current_cantelever_position)
        print("Distance to move for centering", move_distance) 
        if coordinates != None: 
            print("Centering!")
            servomove(move_distance, calibration_factor)
            last_move_distance = move_distance
            time.sleep(1.5)

        print("Checking we still on skin")
        rec , frame = top_view.read()

        oncell = onSkincell(frame)
        if oncell:
            just_scanned = True
            print("Starting scan!")
            if patch is not None:
                scanned_blobs.append(patch)
            scan()
            images_taken +=1

    else:
        #Movement code
        print("Moving to get onto skincell")
        just_scanned = False
        next_point, patch = findBiggestSkincell(current_topview, scanned_blobs)
        print("Biggest nearby skincell detected at ", next_point)
        if next_point!=None:
            current_cantelever_position = (295,241) #This should be automated //TODO
            move_distance = tupleSubtract(next_point,current_cantelever_position)

            print("Distance to move ", move_distance)


            ##Would like to only use 1 single Arduino //TODO get code for "Uno"

        else: # we dont have target 
            lastX , lastY = last_move_distance
            move_distance = lastX * -2 , lastY * -2
            
            print("We didnt find any targets, going back")

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
        
        
        servomove(move_distance, calibration_factor)


    print("End of loop! Sleeping.")
    time.sleep(4) #Gives time for the servoes to move
    print("Done sleeping!")

