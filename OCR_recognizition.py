import mss
import pyautogui
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def move_mouse_to_word(screen_number: int, target_text: str, quadrant=None) -> bool:
    """
    Searches for target_text on the specified screen number and moves the mouse to it if found.
    
    Args:
        screen_number (int): The monitor number (1-based) as per mss.monitors.
        target_text (str): The text string to search for on the screen.
        quadrant (str or None): One of None, 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
    
    Returns:
        bool: True if the text was found and mouse moved, False otherwise.
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if screen_number < 1 or screen_number >= len(monitors):
            raise ValueError(f"Invalid screen_number {screen_number}. Available monitors: 1 to {len(monitors) - 1}")

        monitor = monitors[screen_number]

        # Full monitor region
        left = monitor["left"]
        top = monitor["top"]
        width = monitor["width"]
        height = monitor["height"]

        if quadrant is None:
            region = {
                "top": top,
                "left": left,
                "width": width,
                "height": height,
            }
        else:
            # Calculate half width and height for quadrants
            half_width = width // 2
            half_height = height // 2

            quadrant = quadrant.lower()
            if quadrant == 'top-left':
                region = {"top": top, "left": left, "width": half_width, "height": half_height}
            elif quadrant == 'top-right':
                region = {"top": top, "left": left + half_width, "width": half_width, "height": half_height}
            elif quadrant == 'bottom-left':
                region = {"top": top + half_height, "left": left, "width": half_width, "height": half_height}
            elif quadrant == 'bottom-right':
                region = {"top": top + half_height, "left": left + half_width, "width": half_width, "height": half_height}
            else:
                raise ValueError("Invalid quadrant specified. Choose from None, 'top-left', 'top-right', 'bottom-left', 'bottom-right'.")

        # Grab the screenshot of the defined region
        screenshot = sct.grab(region)

        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # OCR: get word-level data
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        print(data['text'])
        for i, word in enumerate(data['text']):
            if word.lower() == target_text.lower():
                # Calculate the absolute coordinates on the full screen
                x = region["left"] + data['left'][i]
                y = region["top"] + data['top'][i]
                w = data['width'][i]
                h = data['height'][i]

                # Calculate center point to click
                center_x = x + w // 2
                center_y = y + h // 2

                # Move mouse and click (optional)
                pyautogui.moveTo(center_x, center_y)
                # pyautogui.click()  # Uncomment if you want to click

                print(f"Found '{target_text}' at ({center_x}, {center_y})")
                return True

    return False
