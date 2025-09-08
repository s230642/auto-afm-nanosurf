import mss
import pyautogui
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def move_mouse_to_word(screen_number: int, target_text: str) -> bool:
    """
    Searches for target_text on the specified screen number and moves to it if found.

    Args:
        screen_number (int): The monitor number (1-based) as per mss.monitors.
        target_text (str): The text string to search for on the screen.

    Returns:
        bool: True if the text was found , False otherwise.
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if screen_number < 1 or screen_number >= len(monitors):
            raise ValueError(f"Invalid screen_number {screen_number}. Available monitors: 1 to {len(monitors) - 1}")

        monitor = monitors[screen_number]
        region = {
            "top": monitor["top"],
            "left": monitor["left"],
            "width": monitor["width"],
            "height": monitor["height"],
        }
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        for i, word in enumerate(text_data["text"]):
            if target_text in word:
                word_x = text_data["left"][i] + text_data["width"][i] // 2 + region["left"]
                word_y = text_data["top"][i] + text_data["height"][i] // 2 + region["top"]

                pyautogui.moveTo(word_x, word_y, duration=0.2)
                
                print(f"Moved to '{target_text}' at ({word_x}, {word_y}) on screen {screen_number}")
                return True

    print(f"'{target_text}' not found on screen {screen_number}")
    return False
