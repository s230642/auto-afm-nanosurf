import cv2
##Arduino setup
import serial
import time
import csv
from numpy import sum as npsum

######## Constants #########
SIMILARITY = 0.2

def get_fresh_frame(cam):
    for _ in range(3):
        cam.read()
    return cam.read()

def backlashTester():
    data = [["Direction", "Steps"]]

    cam = cv2.VideoCapture(0)

    for _ in range(20):
        cam.read()
    _ , frame = get_fresh_frame(cam)
    TOTAL_DATAPOINTS = 400
    direction = 'L'

    def getDirection(i, d):
        if i > (TOTAL_DATAPOINTS/2) :
            if d=='L':
                return 'R'
            else:
                return 'L'
        else:         
            if d=='U':
                return 'D'
            else:
                return 'U'

    for datapoint in range(TOTAL_DATAPOINTS):
        print("Doing datapoint: " , datapoint)
        for _ in range(10):
            cam.read()
            rec , frame = cam.read()

        steps = 0 
        last_movement = 0
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        last_image = gray
        direction = getDirection(datapoint,direction)

        while True:
                
                rec , frame = get_fresh_frame(cam)
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray, last_image)
                movement = npsum(diff)
                if movement == 0:
                    continue
                percent_diff = abs(last_movement / movement - 1.0)
                print(f"{percent_diff:.8f}")  # 2 decimal places → 3.14

                last_movement = movement
                last_image = gray

                if percent_diff>SIMILARITY and steps > 0:
                    print("Movement detected!")
                    break
                    
                for _ in range(10):
                    ArduinoUno.write(direction.encode())
                    time.sleep(0.005)
                ArduinoUno.write('S'.encode())

                steps += 1

        data.append([direction,steps-1])
        print("Backlash was ", steps - 1 , " steps, in direction ", direction) # last step was actual movement
        time.sleep(2)


    cam.release()
    with open('backlash_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


def primeForMovement(direction, cam, ArduinoUno,):
    _ , frame = get_fresh_frame(cam)
    steps = -1 
    last_movement = 0
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    last_image = gray

    
    while True:     
        _ , frame = get_fresh_frame(cam)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, last_image)
        movement = npsum(diff)
        if movement == 0:
            continue
        percent_diff = abs(last_movement / movement - 1.0)
        last_movement = movement

        if steps == -1:
            steps += 1
            continue # First movement is always different because there was no last image. Dont move stage
        
        if percent_diff>SIMILARITY:
            print("dynamic backlash mitigation done!")
            ArduinoUno.write('S'.encode())
            time.sleep(0.1)
            break
            
        last_image = gray
        for _ in range(10):
            ArduinoUno.write(direction.encode())
            time.sleep(0.005)
        ArduinoUno.write('S'.encode())
        steps += 1 


if __name__ == "__main__":
    try:
        ArduinoUno = serial.Serial("COM7", 9600, timeout=1)
        time.sleep(2)
    except Exception as e:
        print("Serial connection failed:", e)


    backlashTester()
