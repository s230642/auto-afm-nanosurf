import pyautogui
from computervision_new import findBiggestSkincellFileName, onSkincellFile


##Arduino setup
import serial
import time
ArduinoUno = serial.Serial("COM7", 9600, timeout=1)


def servomove(move_distance, calibration_factor, backlash):
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
            print("----------------------")
        time.sleep(4)
        print("Starting linear move")

        move_with_repeats('U', abs(y) * calibration_factor[1])
        print("----------------------")

    elif y > 0:
        if backlash[1]!=0:
            print("Doing backlash compensation")
            move_with_repeats('D', backlash[1])
            print("Backlash movement done")
            print("----------------------")
        time.sleep(4)
        print("Starting linear move")

        move_with_repeats('D', abs(y) * calibration_factor[1])
        print("----------------------")
    print("Switching axis")
    time.sleep(4)
    if x > 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('R', backlash[0])
            print("Backlash movement done")
            print("----------------------")
        time.sleep(4)
        print("Starting linear move")

        move_with_repeats('R', abs(x) * calibration_factor[0])
        print("----------------------")


    elif x < 0:
        if backlash[0]!=0:
            print("Doing backlash compensation")
            move_with_repeats('L', backlash[0])
            print("Backlash movement done")
            print("----------------------")
        time.sleep(4)
        print("Starting linear move")
        move_with_repeats('L', abs(x) * calibration_factor[0])
        print("----------------------")

def tupleSubtract(t1, t2):
    return t1[0] - t2[0] , t1[1] - t2[1]

calibration_factor_x = 0.0085  # seconds/ pixel # Scale of pixels to distance movement
calibration_factor_y = 0.0113  # Scale of pixels to distance movement
backlash_x_constant = 1.6
backlash_y_constant = 2.6

next_point = findBiggestSkincellFileName("images/currentPosition.JPG")
print(next_point)
current_cantelever_position = (301,322) #This should be automated //TODO

move_distance = tupleSubtract(next_point,current_cantelever_position)

print(move_distance)
servomove(move_distance, (calibration_factor_x,calibration_factor_y), (backlash_x_constant,backlash_y_constant))
