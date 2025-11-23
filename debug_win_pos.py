# first attempt to debug the click coordinates (relative to game window) issue

from pynput import mouse
import time
from pywinauto import Application
import os
import pyautogui
import numpy as np
import cv2

log_file = "clicks_log.txt"
app = Application(backend="uia").connect(title_re="BlueStacks App Player")

def get_bluestacks_window():
    try:
        app = Application(backend="uia").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error while connecting to BlueStacks: {e}")
        return None


# w = lambda: rect().width()
# h = lambda: rect().height()
window = None
rect = lambda: window.wrapper_object().rectangle()
w = lambda: rect().width()
h = lambda: rect().height()

def takeScreenShot():
    screenshot = pyautogui.screenshot(region=(rect().left, rect().top, w(), h()))
    screenshot.save("my_image.png")

def log_line(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
    print(text)

def drawOnCoordinates(x_1, x_2, y_1, y_2):
    # Example: 4 points of the rectangle (order is important to ensure it is properly closed)
    points = np.array([[x_1, y_1], [x_2, y_1], [x_2, y_2], [x_1, y_2]])

    points = points.astype(np.int32)
    img = cv2.imread("my_image.png")

    # Draw the rectangle (closed polygon in red)
    cv2.polylines(img, [points], isClosed=True, color=(0, 0, 255), thickness=2)

    with open("sc/my_image.png") as f:
        # Save the result
        cv2.imwrite("contours_zone.png", img)
        print("All done!")

def on_click(x, y, button, pressed):

    if not pressed:
        return
    
    if button.name != 'left':
        return False  # Stop listener
    
    window = get_bluestacks_window()
    rect = window.wrapper_object().rectangle()
    
    for i in 4:
        rel_x = x - rect.left
        rel_y = y - rect.top
        
        log_line(f"Mouse abs: ({x}, {y})")
        # log_line(f"Window pos: left={rect.left}, top={rect.top}")
        log_line(f"Click on ({rel_x}, {rel_y})\n")
        takeScreenShot()

with mouse.Listener(on_click=on_click) as listener:
    listener.join()