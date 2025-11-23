# drawing feature with cv2 to visualize ROI position inside game window
# There are modules versions issues due to cv2 not supporting latest python, so I have to use python 312. the screenshot feature does not work anymore due to compatibilities issues with pyscreeze, used by pillow and pyautogui, so until I fix my cv2 version issue, the script cannot run
# I recently clean installed windows and changed my python environment, I try to figure how I managed to make evrything work without cv2 versions incompatibilities

import cv2
import numpy as np
from pywinauto import Application
import pyautogui

x_min = 80
x_max = 355
y_min = 760
y_max = 800
x = 0
y = 0
y_pct = 0.912
x_pct_1 = 0.166
x_pct_2 = 0.765
rect = None
rect_width = 0
rect_height = 0
side_bar = 45

def get_bluestacks_window():
    try:
        app = Application(backend="uia").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error when connecting to BlueStacks: {e}")
        return None

def get_coordinates():
    global window
    window = get_bluestacks_window()
    if window is None:
        print("BlueStacks window not found.")
        return False
    try:
        global rect
        global rect_width
        global rect_height
        rect = window.wrapper_object().rectangle()
        rect_width = rect.width()
        rect_height = rect.height()
    except Exception as e:
        print(f"Error when trying to access window's rectangle: {e}")
        return

get_coordinates()

# Example: 4 points of the rectangle (order is important to ensure it is properly closed)
points = np.array([[x_pct_1 * rect_width, y_pct * rect_height], [x_pct_2 * rect_width, y_pct * rect_height], [x_pct_2 * rect_width, rect_height], [x_pct_1 * rect_width, rect_height]])

points = points.astype(np.int32)

# Get the position and size of the window
screenshot = pyautogui.screenshot(region=(window.left, window.top, rect.width() - side_bar, rect.height()))

screenshot.save("my_image.png")
img = cv2.imread("my_image.png")

if img is None:
        print("Error: image not found.")
else:
    # Draw the rectangle (closed polygon in red)
    cv2.polylines(img, [points], isClosed=True, color=(0, 0, 255), thickness=2)

# Save the result
cv2.imwrite("contours_zone.png", img)
print("All done!")