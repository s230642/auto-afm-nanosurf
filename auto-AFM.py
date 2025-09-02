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
from OCR_recognizition import click_and_hold_text_on_screen, click_text_on_screen_human

screen_num = 3
target = "Approach"

found = click_text_on_screen_human(screen_num, target)

if found:
    print("Clicked successfully!")
else:
    print("Text not found.")
