import mss
import pyautogui
import pytesseract
from PIL import Image

# Define region to search (x, y, width, height)
x, y, width, height = 0, 0, 1920, 1080   # full screen, adjust if needed

with mss.mss() as sct:
    region = {"top": y, "left": x, "width": width, "height": height}
    screenshot = sct.grab(region)
    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

# Run OCR
text_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# Look for the target string
target = "auto-AFM.py"
for i, word in enumerate(text_data["text"]):
    if target in word:
        # Compute screen coordinates
        word_x = text_data["left"][i] + text_data["width"][i] // 2 + x
        word_y = text_data["top"][i] + text_data["height"][i] // 2 + y
        
        # Move mouse and click
        pyautogui.moveTo(word_x, word_y, duration=0.2)
        pyautogui.click()
        print(f"Clicked on {target} at ({word_x}, {word_y})")
        break
else:
    print(f"{target} not found on screen")
