# Minimal scipt to find mouse position when click inside game window is detected with both relative (to the window) and absolute (screen) coordinates

from pynput import mouse
import time
from pywinauto import Application
import os

log_file = "clicks_log.txt"
app = Application(backend="uia").connect(title_re="BlueStacks App Player")

def get_bluestacks_window():
    try:
        app = Application(backend="uia").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error when connecting to BlueStack: {e}")
        return None


# w = lambda: rect().width()
# h = lambda: rect().height()

def log_line(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
    print(text)

def on_click(x, y, button, pressed):

    if not pressed:
        return
    
    if button.name != 'left':
        return False  # Stop listener
    
    window = get_bluestacks_window()
    rect = window.wrapper_object().client_rect(text_area_rect=True)
    
    rel_x = x - rect.left
    rel_y = y - rect.top
    
    log_line(f"Mouse abs: ({x}, {y})")
    # log_line(f"Window pos: left={rect.left}, top={rect.top}")
    log_line(f"Click on ({rel_x}, {rel_y})\n")

with mouse.Listener(on_click=on_click) as listener:
    listener.join()