

##Arduino setup
import serial
import time


ser = serial.Serial("COM6", 9600, timeout=1)
# Wait for Arduino to be ready
while True:
    print("waiting on arduino")
    time.sleep(1)
    line = ser.readline().decode().strip()
    if line == "READY":
        break

#Other setups
import pyautogui
from OCR_recognizition import move_mouse_to_word
pyautogui.moveTo(-467, 253, duration=0.2) #Save button position
print("Sending click...")
ser.write(b"CLICK\n")


time.sleep(3)


for word in ["Save"]:
    screen_num = 3


    found = move_mouse_to_word(screen_num, word,"bottom-left")

    if found:
        print(f"{word} successfully!")
        print("Sending click...")
        ser.write(b"CLICK\n")
    else:
        print("Text not found.")