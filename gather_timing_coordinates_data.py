# main and 'complete, sucessful' script for mouth position capture when click inside game window and timing between click (time data needed for sleep feature : wait amount of time needed before the player can interact with the game)
# I integrate the features onto my main script from this file's code, the two others are for specific debugging I needed to correct this one.
from pynput import mouse
import time
from pywinauto import Application
import os

log_file = "clicks_log.txt"
open(log_file, "w").close()  # clear log file
last_click_time = None

zone = {
    "x_min_pct": 0.17,
    "x_max_pct": 0.735,
    "y_min_pct": 0.93,
    "y_max_pct": 0.98
}

def get_bluestacks_window():
    try:
        app = Application(backend="win32").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error when connecting to BlueStacks: {e}")
        return None

def is_inside_bluestacks(pos, window):
    if window is None:
        print("BlueStacks window not found.")
        return False
    
    x_abs, y_abs = pos
    try:
        rect = window.wrapper_object().client_area_rect()
        return (rect.left <= x_abs <= rect.right) and (rect.top <= y_abs <= rect.bottom)
    except Exception as e:
        print(f"Error, couldn't access the window rectangle: {e}")
        return False

def log_line(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
    print(text)

def is_in_zone_dynamic(x, y, rect, zone):
    width = rect.width()
    height = rect.height()

    x_min = int(zone["x_min_pct"] * width)
    x_max = int(zone["x_max_pct"] * width)
    y_min = int(zone["y_min_pct"] * height)
    y_max = int(zone["y_max_pct"] * height)

    return x_min <= x <= x_max and y_min <= y <= y_max

def on_click(x_abs, y_abs, button, pressed):
    global last_click_time
    window = get_bluestacks_window()
    
    if window is None:
        return
    
    try:
        rect = window.wrapper_object().client_area_rect()
    except Exception as e:
        print(f"Error, couldn't access the window rectangle: {e}")
        return
    
    # Relative coordinates to client area
    x = x_abs - rect.left
    y = y_abs - rect.top

    # if resizing, calculate proportional coordinates (percentages)
    width = rect.width()
    height = rect.height()
    x_ratio = x / width if width > 0 else 0
    y_ratio = y / height if height > 0 else 0

    if not pressed:
        return

    if not is_inside_bluestacks((x_abs, y_abs), window):
        return
    
    if button.name != 'left':
        print(f"Script ended by click {button.name}.")
        return False  # Stop listener

    if last_click_time is None: # first click
        now = time.time()
        last_click_time = now
        log_line(f"First click on ({x}, {y})")
    else:
        if is_in_zone_dynamic(x, y, rect, zone):
            now = time.time()
            # delta = now - last_click_time
            # log_line(f"Time interval: {delta:.4f} s\n")
            last_click_time = now
            log_line(f"Click on ({x}, {y})\n")
        else:
            last_click_time = time.time()
            log_line(f"Click on ({x}, {y} | Ratio ({x_ratio:.3f}, {y_ratio:.3f}))")
    

# === STARTING LISTENING ===
print("Waiting for clicks in the BlueStacks window...")
with mouse.Listener(on_click=on_click) as listener:
    listener.join()