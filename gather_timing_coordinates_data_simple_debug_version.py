# I had an issue with accessing client window (wrong pywinauto method used) and resizing (I wasn't taking into account the window size change and looked at the problem the wrong way)
# this file aimed to fully debbug the gather_timing_coordinates_data.py file with minimum code and only essential parts

from pynput import mouse
import time
from pywinauto import Application
import os

log_file = "clicks_log.txt"
open(log_file, "w").close()  # clear log file

last_click_time = None

area = {
    "x_min_pct": 0.10,
    "x_max_pct": 0.40,
    "y_min_pct": 0.90,
    "y_max_pct": 0.95
}

def get_bluestacks_window():
    try:
        print("Attempting to connect to BlueStacks...")
        app = Application(backend="uia").connect(title_re="BlueStacks App Player")
        window = app.top_window()
        print(f"✓ Connected to BlueStacks: {window.window_text()}")
        return window
    except Exception as e:
        print(f"✗ Error while connecting to BlueStacks: {e}")
        print("\nAttempt to list all available windows:")
        try:
            from pywinauto import Desktop
            windows = Desktop(backend="uia").windows()
            for w in windows:
                if w.window_text():
                    print(f"  - {w.window_text()}")
        except:
            pass
        return None

def is_inside_bluestacks(pos, window):
    if window is None:
        return False
    
    x_abs, y_abs = pos
    try:
        rect = window.wrapper_object().rectangle()
        inside = (rect.left <= x_abs <= rect.right) and (rect.top <= y_abs <= rect.bottom)
        return inside
    except Exception as e:
        print(f"Error when trying to access window's rectangle: {e}")
        return False

def log_line(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
    print(text)

def is_in_zone_dynamic(x, y, rect, area):
    width = rect.width()
    height = rect.height()
    x_min = int(area["x_min_pct"] * width)
    x_max = int(area["x_max_pct"] * width)
    y_min = int(area["y_min_pct"] * height)
    y_max = int(area["y_max_pct"] * height)
    return x_min <= x <= x_max and y_min <= y <= y_max

def on_click(x_abs, y_abs, button, pressed):
    global last_click_time
    
    # Debug: print every click
    print(f"[DEBUG] Click detected: pos=({x_abs}, {y_abs}), button={button.name}, pressed={pressed}")
    
    if not pressed:
        print("[DEBUG] Click release ignored")
        return
    
    window = get_bluestacks_window()
    
    if window is None:
        print("[DEBUG] BlueStacks window missing.")
        return
    
    try:
        rect = window.wrapper_object().rectangle()
        print(f"[DEBUG] BlueStacks rect: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
    except Exception as e:
        print(f"[DEBUG] Error with rectangle : {e}")
        return
    
    x = x_abs - rect.left
    y = y_abs - rect.top
    print(f"[DEBUG] Relative position: ({x}, {y})")
    
    inside = is_inside_bluestacks((x_abs, y_abs), window)
    print(f"[DEBUG] Inside BlueStacks? {inside}")
    
    if not inside:
        print("[DEBUG] Click outside BlueStacks, ignored")
        return
    
    if button.name != 'left':
        print(f"[INFO] Script ended by click {button.name}.")
        return False  # Stop listener
    
    if last_click_time is None:  # first click
        now = time.time()
        last_click_time = now
        log_line(f"First click on ({x}, {y})")
    else:
        in_zone = is_in_zone_dynamic(x, y, rect, area)
        print(f"[DEBUG] In zone? {in_zone}")
        
        if in_zone:
            now = time.time()
            delta = now - last_click_time
            log_line(f"Time interval : {delta:.4f} s")
            last_click_time = now
        else:
            last_click_time = time.time()
            log_line(f"Click on ({x}, {y})")

# === INITIAL TEST ===
print("=" * 50)
print("BLUESTACKS CONNECTION TEST")
print("=" * 50)
test_window = get_bluestacks_window()
if test_window:
    try:
        rect = test_window.wrapper_object().rectangle()
        print(f"Window position: ({rect.left}, {rect.top}) to ({rect.right}, {rect.bottom})")
        print(f"Size: {rect.width()}x{rect.height()}")
    except Exception as e:
        print(f"Error during the test: {e}")
else:
    print("\n⚠ WARNING: BlueStacks could not be detected!")
    print("The script will continue, but will log only if BlueStacks is found.")

print("\n" + "=" * 50)
print("STARTING CLICK LISTENING")
print("=" * 50)
print("Waiting for clicks in the BlueStacks window...")
print("Right click to end the script.\n")

# === STARTING LISTENING ===
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

print("\nScript end.")