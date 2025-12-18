# simple script for automated clicking for ancillary operations (loading convo, accepting rewards, set chat at max speed...)
# Current coordinates are relative to the game window, which must not be moved while the script is running (otherwise include lines 71 and 72 in the loop line 74, however with a slight performance impact)

import json
import os
from pynput.mouse import Controller, Button
import time
from pywinauto import Application

mouse = Controller()
# === GLOBAL SETTINGS ===
msg_nb = 4  # "blocks group" to compare
json_path = "templates/other_auto_clicks.json"
templates_dir = "templates/"

# === ACCESSING GAME WINDOW === 
def get_bluestacks_window():
    try:
        app = Application(backend="win32").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error when connecting to BlueStacks: {e}")
        return None

def get_window_position(window):
    if window is None:
        print("BlueStacks window not found.")
        return (0, 0)
    
    try:
        rect = window.wrapper_object().client_area_rect()
        pos = (rect.left, rect.top)
        return pos

    except Exception as e:
        print(f"Error when trying to access window's rectangle: {e}")
        return (0, 0)

# === Loading JSON ===
with open(json_path, "r") as f:
    ancillary_clicks = json.load(f)

def clicking(nth_click, data, offset):
    """
    Perform a single click based on the nth entry in the JSON data.
    
    Args:
        nth_click: The click number (key in JSON)
        data: The loaded JSON dictionary
        offset: Tuple (x, y) representing window position offset
    """
    click_data = data.get(str(nth_click))

    if not click_data:
        raise ValueError(f"{nth_click}th ancillary click is missing from JSON template or couldn't be loaded.")

    #Extracting coordinates and delay values
    coors = click_data["coors"]
    delay = click_data["delay"]
    # Applying offset relative coordinates
    abs_x = coors[0] + offset[0] 
    abs_y = coors[1] + offset[1]

    mouse.position = (abs_x, abs_y) # Like mouse.move but set position in absolute way (while mouse.move 'adds' x and y values to previous position, so relatively)
    mouse.click(Button.left, 1)

    print(f"{nth_click}th click, position ({abs_x}, {abs_y}), delay {delay} s \n")
    
    time.sleep(delay)

window = get_bluestacks_window()
offset = get_window_position(window)

for nth_click in sorted(ancillary_clicks.keys(), key=int):
    clicking(nth_click, ancillary_clicks, offset)