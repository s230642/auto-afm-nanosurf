
##Arduino setup
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



"""

image_capured = 1
while image_capured < 15:

    move, scan = useVisualMicroscope()
    
    if move:
        preformMovement()

    if scan:
        preformScanAndSave()

    image_capured + 1

"""

from OCR_recognizition import move_mouse_to_word

screen_num = 3
target = "Approach"

found = move_mouse_to_word(screen_num, target)

if found:
    print("Found successfully!")
    print("Sending click...")
    ser.write(b"CLICK\n")
else:
    print("Text not found.")
