import mss
import pyautogui
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


import random

def human_like_move(x, y, duration=0.5):
    """
    Simulate a more natural, human-like mouse movement to (x, y).
    """
    # Randomize movement path slightly
    random_x = random.randint(-5, 5)
    random_y = random.randint(-5, 5)
    pyautogui.moveTo(x + random_x, y + random_y, duration=duration)

import uiautomation as auto
import time
import ctypes
import time
from ctypes import wintypes

# Define Windows API constants
MOUSEEVENTF_LEFTDOWN = 0x02
MOUSEEVENTF_LEFTUP = 0x04

# Set up ctypes for Windows API functions
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Define structures and function prototypes
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def click_with_ctypes(x, y):
    # Move the cursor
    ctypes.windll.user32.SetCursorPos(x, y)

    # Simulate mouse down and up (physical click)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.1)  # Short delay for the press action
    user32.mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    print(f"Simulated physical click at ({x}, {y}) using ctypes")


def click_with_uiautomation(target_text):
    # Find the button or control containing the target text
    control = auto.ControlFromPoint(x, y)  # You can also get control by text or other identifiers
    control.Click()

    print(f"Clicked on the target '{target_text}' with uiautomation")

# Example usage:


def human_like_click(x, y, hold_duration=1.0):
    """
    Simulate a click at (x, y) with some natural randomness.
    """
    human_like_move(x, y, duration=0.5)  # Move to the target with a human-like path
    pyautogui.mouseDown()
    time.sleep(hold_duration)
    pyautogui.mouseUp()

from pynput.mouse import Button, Controller
import time

def click_with_pynput(x, y, hold_duration=1.0):
    mouse = Controller()
    mouse.position = (x, y)
    mouse.press(Button.left)
    time.sleep(hold_duration)
    mouse.release(Button.left)
    print(f"Simulated physical click at ({x}, {y})")

import time
import win32api
import win32con
import win32gui

def click_with_win32api(x, y, hold_duration=1.0):
    # Move the mouse to the desired position
    win32api.SetCursorPos((x, y))
    print("natural click")
    # Simulate a mouse click (left button down and up)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y)
    time.sleep(0.5)  # Small delay for the press action
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y)

    print(f"Simulated physical click at ({x}, {y}) with win32api")


def click_text_on_screen_human(screen_number: int, target_text: str) -> bool:
    """
    Searches for target_text on the specified screen number and clicks it if found.

    Args:
        screen_number (int): The monitor number (1-based) as per mss.monitors.
        target_text (str): The text string to search for on the screen.

    Returns:
        bool: True if the text was found and clicked, False otherwise.
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

                human_like_move(word_x, word_y, duration=0.5)
                click_with_ctypes(word_x, word_y)
                print(f"Clicked on '{target_text}' at ({word_x}, {word_y}) on screen {screen_number}")
                return True

    print(f"'{target_text}' not found on screen {screen_number}")
    return False

def click_text_on_screen(screen_number: int, target_text: str) -> bool:
    """
    Searches for target_text on the specified screen number and clicks it if found.

    Args:
        screen_number (int): The monitor number (1-based) as per mss.monitors.
        target_text (str): The text string to search for on the screen.

    Returns:
        bool: True if the text was found and clicked, False otherwise.
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
                pyautogui.click()
                print(f"Clicked on '{target_text}' at ({word_x}, {word_y}) on screen {screen_number}")
                return True

    print(f"'{target_text}' not found on screen {screen_number}")
    return False


import mss
import pyautogui
import pytesseract
from PIL import Image
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def click_and_hold_text_on_screen(screen_number: int, target_text: str, hold_duration: float = 1.0) -> bool:
    """
    Searches for target_text on the specified screen number and clicks & holds it if found.

    Args:
        screen_number (int): The monitor number (1-based) as per mss.monitors.
        target_text (str): The text string to search for on the screen.
        hold_duration (float): Duration in seconds to hold the mouse click. Default is 1 second.

    Returns:
        bool: True if the text was found and clicked & held, False otherwise.
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
                pyautogui.mouseDown()
                time.sleep(hold_duration)
                pyautogui.mouseUp()

                print(f"Clicked and held on '{target_text}' at ({word_x}, {word_y}) on screen {screen_number} for {hold_duration} seconds")
                return True

    print(f"'{target_text}' not found on screen {screen_number}")
    return False
