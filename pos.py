# Minimal scipt to find mouse position when click inside game window is detected with both relative (to the window) and absolute (screen) coordinates

from pynput import mouse
import time
from pywinauto import Application
import os

log_file = "clicks_log.txt"
app = Application(backend="win32").connect(title_re="BlueStacks App Player")

def get_bluestacks_window():
    try:
        app = Application(backend="win32").connect(title_re="BlueStacks App Player")
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

def on_click(x_abs, y_abs, button, pressed):

    window = get_bluestacks_window()

    if window is None:
        return
    
    try:
        rect = window.wrapper_object().client_area_rect()
    except Exception as e:
        print(f"Error, couldn't access the window rectangle: {e}")
        return

    if not pressed:
        return
    
    if button.name != 'left':
        return False  # Stop listener
    
    window = get_bluestacks_window()
    rect = window.wrapper_object().client_area_rect()
    
    rel_x = x_abs - rect.left
    rel_y = y_abs - rect.top
    
    log_line(f"Mouse abs: ({x_abs}, {y_abs})")
    # log_line(f"Window pos: left={rect.left}, top={rect.top}")
    log_line(f"Inside game window: {is_inside_window(rel_x, rel_y, rect)}\n")
    # log_line(f"Game window global position (left, right, top, bottom sides) :{rect.left, rect.right, rect.top, rect.bottom}")

def is_inside_window(rel_x, rel_y, rect):
    if 0 <= rel_x <= rect.right - rect.left and 0 <= rel_y <= rect.bottom - rect.top:
        log_line(f"Click on ({rel_x}, {rel_y})")
        return True
    else:
        log_line(f"Game window global position (left, right, top, bottom sides) :{rect.left, rect.right, rect.top, rect.bottom}")
        return False


with mouse.Listener(on_click=on_click) as listener:
    listener.join()