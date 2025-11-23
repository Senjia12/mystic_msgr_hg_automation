# script for basic window handling with pygetwindow
# before switching to pywinauto I used this module

import pygetwindow as gw
import pyautogui

# get BlueStacks window
win = gw.getWindowsWithTitle("BlueStacks App Player")[0]

# Retrieve the position and size of the window
x, y = win.left, win.top
width, height = win.width, win.height

screenshot = pyautogui.screenshot(region=(x, y, width, height))
screenshot.save("falling.png")
