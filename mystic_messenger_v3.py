#Latest version of the script, doesn't run because I haven't finished to implement everything (minor features and adjustments missing) and for the following reason :
# There are modules versions issues due to cv2 not supporting latest python, so I have to use python 312
# I recently clean installed windows and changed my python environment, I try to figure how I managed to make evrything work without cv2 versions incompatibilities

# ADDITIONAL DETAILS
# cv2 relies on np 2.2.6 and pip is unable to install it even on python 313 (while this version of python is said to be supported by cv2 on their docs)
# all fix found failed for me, so I had to downgrade python, cv2 is functionning but now pyautogui's related modules are causing issues
#  the screenshot features does not work anymore due to compatibilities issues with pyscreeze, used by pillow and pyautogui, so until I fix my cv2 version issue, the scripts using it cannot run

import cv2
import json
from pywinauto import Application
import os
import numpy as np
import pyautogui
import time
from pynput import mouse

msg_nb = 1  # "blocks group" to compare
json_path = "templates/templates.json"
blocks_dir = "blocks/"
templates_dir = "templates/"
coorsBlocks = {}
nth_block = 0
window = None
# Create blocks directory if not existing already
os.makedirs("blocks", exist_ok=True)

with open(json_path, "r") as f:
    all_messages = json.load(f)
    msgCount = len(all_messages)

zone = {
    "x_min_pct": 0.166,
    "x_max_pct": 0.755,
    "y_min_pct": 0.912
}
    
# NOT USED
# x_min = 80
# x_max = 355
# y_min = 760
# y_max = 800
# x = 0
# y = 0
# roi_height = int(img_h * 0.4) # UNUSED

def startAndGobalLoop():
    global window, rect, w, h
    for msg_nb in range(1, msgCount + 1): # msg_nb starts at 1 and end at 17. default range behavior is 0 to n-1
        # get BlueStacks window
        window = get_bluestacks_window()
        if window is None:
            continue #RETURN ???

        if find_yellow() is True: # check if yellow is detected and if yes => time to reply
            clickOnCoors() # missing arguments : define zone to be clicked
            cv2.polylines(img, [points], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.imwrite("contours_area_reply.png", img)

        takeScreenShot()

        blocks, template_filename = get_blocks_and_templates(msg_nb, all_messages)
        template_path = os.path.join(templates_dir, template_filename)
    
        roi, y_start = setRoi(img, img_h)

        contours = findContours(roi)

        # resets matching block and related's data. Start fresh
        nth_block = 0
        coorsBlocks.clear()

        cropEachBlock(contours, y_start)

        # compare blocks to template and get middle's coordinates of the matching one
        x_click, y_click = comparison(blocks, template_path, blocks_dir)

        clickOnCoors(x_click, y_click)

def get_bluestacks_window():
    try:
        app = Application(backend="win32").connect(title_re="BlueStacks App Player")
        return app.top_window()
    except Exception as e:
        print(f"Error while connecting to BlueStacks: {e}")
        return None

def is_inside_bluestacks(pos, window): # NOT USED, WHY ?
    if window is None:
        print("BlueStacks window not found. If your system is not in english, launch app and replace title_re value by the name displayed at the top of the app.\ntitle_re can be found in mystic_messenger.py within get_bluestacks_window() function inside app variable.")
        return False
    
    x_abs, y_abs = pos
    try:
        rect = window.wrapper_object().client_area_rect() # rectangle() object has 4 attributes : left right top bottom and 2 methods : width and height
        x = x_abs - rect().left
        y = y_abs - rect().top
        return (rect().left <= x_abs <= rect().right) and (rect().top <= y_abs <= rect().bottom)
    except Exception as e:
        print(f"Error when trying to access window's rectangle: {e}")
        return


rect = lambda: window.wrapper_object().rectangle()
w = lambda: rect().width()
h = lambda: rect().height()

def takeScreenShot():
    screenshot = pyautogui.screenshot(region=(rect().left, rect().top, w(), h()))
    screenshot.save("my_image.png")

# Loading the screenshot
img = cv2.imread("my_image.png")
img_h, img_w = img.shape[:2]

def setRoi(img, img_h):
    # Define Region Of Interest (centered vertically)
    y_start = int(img_h * 0.3)
    y_end = int(img_h * 0.9)
    roi = img[y_start:y_end, :]
    return roi, y_start

def findContours(roi):
    # Processing only inside ROI
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def cropEachBlock(contours, y_start):
    # Loop over each contour to crop and save
    global nth_block

    for cnt in contours:
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        y += y_start  # adjust y to global position, not just within ROI
        
        # Filter out small unwanted contours
        if w_box > 50 and h_box > 30:
            nth_block += 1
            block = img[y:y + h_box, x:x + w_box] # slicing vertically and horizontally to crop block
            cv2.imwrite(f"blocks/block_{nth_block}.png", block)
            # HERE ADD COORDINATES TO DICT TO BE CLICKED
            y_click = rect().top + y + h_box / 2
            x_click = rect().left + x + w_box / 2

            global coorsBlocks
            coorsBlocks[nth_block] = {# nth block detected in the image (is the answer)
                "coors" : (x_click, y_click),
                "path": f"blocks/block_{nth_block}.png"
            }
            
            # Redraw on the full image with vertical offset
            cnt[:, 0, 1] += y_start  # shift the contour vertically
            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)

    # save result
    cv2.imwrite("central_zone_contours.png", img)

def get_blocks_and_templates(msg_nb, data):
    msg_data = data.get(str(msg_nb))
    if not msg_data:
        raise ValueError(f"msg_nb {msg_nb} not found in JSON file.")

    print(f"Blocks for the message {msg_nb} : {msg_data['blocks']}")
    print(f"Template for the message {msg_nb} : {msg_data['template']}")
    return msg_data["blocks"], msg_data["template"], msg_data["delay"]

blocks, template_filename, delays = get_blocks_and_templates(msg_nb, all_messages)
template_path = os.path.join(templates_dir, template_filename)


def comparison(blocks, template_path, blocks_dir):
    template = cv2.imread(template_path, 0)
    if template is None:
        raise FileNotFoundError(f"Template {template_path} not found.")
    scores = {}

    for index, block_name in enumerate(blocks):
        block_path = os.path.join(blocks_dir, block_name)
        img = cv2.imread(block_path, 0)
        if img is None:
            print(f"[!] Image not found: {block_path}")
            continue
        res = cv2.matchTemplate(template, img, cv2.TM_CCOEFF_NORMED)
        score = res.max()
        scores[block_name] = (score, index)
        print(f"{block_name} → score {score:.4f}")

    best_block = max(scores, key = scores.get)
    best_score, best_idx = scores[best_block]
    global coorsBlocks

    print(f"\nBlock kept: {best_block} (score {best_score:.4f}, data {coorsBlocks[best_idx]})")

    for block_name, score in scores.items(): # removes crop of other blocks
        if block_name != best_block:
            path = os.path.join(blocks_dir, block_name)
            os.remove(path)
            print(f"{block_name} removed (score {score:.4f})")
    
    # get index of the matching block, so I know its position (in the detected blocks) and can retrieve its coordinates
    x_click, y_click = coorsBlocks[best_idx]["coors"]
    coorsBlocks.clear()
    return x_click, y_click

def clickOnCoors(x, y): # if click not working, check AV for restrictions on mouse control and run as administrator if needed (mandatory if bluestacks run as admin)
    pyautogui.click(x, y)

def find_yellow():
    global h, w, x_min, x_max, y_min, y_max, img, points
    cv2.imread(img)
    if img is None:
        raise FileNotFoundError(f"Image {img} not found.")

    h, w, _ = img.shape

    # Apply the cropping directly here
    x_min = int(zone["x_min_pct"] * w)
    x_max = int(zone["x_max_pct"] * w)
    y_min = int(zone["y_min_pct"] * h)
    y_max = h

    points = np.array([
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ], dtype=np.int32)
    
    roi = img[y_min:y_max, x_min:x_max]  # Cropped image (Region Of Interest)
    cv2.imwrite("roi.png", roi)

    # ↓ Downsampling to speed up processing
    roi_small = cv2.resize(roi, (roi.shape[1] // 4, roi.shape[0] // 4))

    h, w = roi.shape[:2]

    x_min = int(zone["x_min_pct"] * w)
    x_max = int(zone["x_max_pct"] * w)
    y_min = int(zone["y_min_pct"] * h)
    y_max = h

    hsv = cv2.cvtColor(roi_small, cv2.COLOR_BGR2HSV)  # BGR → HSV

    # Dynamic yellow range
    lower_yellow = np.array([20, 100, 180])
    upper_yellow = np.array([40, 255, 255])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    ratio = cv2.countNonZero(mask) / (mask.shape[0] * mask.shape[1])
    cv2.imwrite("debug_mask.png", mask)

    if ratio > 0.1:
        print("Yellow frame detected → the player must respond")
        return True

    return False