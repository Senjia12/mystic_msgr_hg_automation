import cv2
import json
from pywinauto import Application
import os
import numpy as np
import pyautogui
import time
from pynput import mouse

path = "./blocks"
msg_nb = 4  # "blocks group" to compare
json_path = "templates/templates.json"
blocks_dir = "blocks/"
templates_dir = "templates/"
scores = {}
reply_zone = {
    "x_min_pct": 0.166,
    "x_max_pct": 0.755,
    "y_min_pct": 0.92
}

with open(json_path, "r") as f:
    all_messages = json.load(f)

x_min = 80
x_max = 355
y_min = 760
y_max = 800
x = 0
y = 0
side_bar = 45
image_path = "my_image.png" #TO BE EDITED this will be given by screenshot and main loop

def get_bluestacks_window():
    try:
        app = Application(backend="uia").connect(title_re="BlueStacks App Player")
        window = app.top_window()
        return window
    except Exception as e:
        print(f"Error while connecting to BlueStacks: {e}")
        return None

def is_inside_bluestacks(pos, window):
    if window is None:
        print("BlueStacks window not found.")
        return False
    
    x_abs, y_abs = pos
    try:
        rect = window.wrapper_object().rectangle()
        x = x_abs - rect.left
        y = y_abs - rect.top
        return (rect.left <= x_abs <= rect.right) and (rect.top <= y_abs <= rect.bottom)
    except Exception as e:
        print(f"Error when trying to access window's rectangle: {e}")
        return

# get BlueStacks window
window = get_bluestacks_window()
# Get the position and size of the window
width = window.wrapper_object().rectangle().width()
height = window.wrapper_object().rectangle().height()
screenshot = pyautogui.screenshot(region=(x, y, width, height))
screenshot.save("my_image.png")

# Load the full image
img = cv2.imread("my_image.png")
h, w = img.shape[:2]

# Define Region Of Interest (centered vertically)
roi_height = int(h * 0.4)
y_start = int(h * 0.3)
y_end = int(h * 0.9)
roi = img[y_start:y_end, :]

# Processing only inside ROI
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



# Create the blocks folder if it does not exist
os.makedirs("blocks", exist_ok=True)
n = 0

# Loop over each contour to crop and save
for i, cnt in enumerate(contours):
    x, y, w_box, h_box = cv2.boundingRect(cnt)
    y += y_start  # y based on global position not in ROI

    # Filter out small unwanted contours
    if w_box > 50 and h_box > 30:
        n += 1
        block = img[y:y + h_box, x:x + w_box]
        cv2.imwrite(f"blocks/block_{n}.png", block)

# Redraw on the full image with vertical offset
for cnt in contours:
    cnt[:, 0, 1] += y_start  # shift the contour vertically
    cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)

# Save the result
cv2.imwrite("central_zone_contours.png", img)

def get_blocks_and_template(msg_nb, data):
    msg_data = data.get(str(msg_nb))
    if not msg_data:
        raise ValueError(f"msg_nb {msg_nb} not found in JSON file.")

    print(f"Blocks for the message {msg_nb} : {msg_data['blocks']}")
    print(f"Template for the message {msg_nb} : {msg_data['template']}")
    return msg_data["blocks"], msg_data["template"]
    
blocks, template_filename = get_blocks_and_template(msg_nb, all_messages)
template_path = os.path.join(templates_dir, template_filename)


def comparison(blocks, template_path, blocks_dir):
    template = cv2.imread(template_path, 0)
    if template is None:
        raise FileNotFoundError(f"Template {template_path} not found.")
    scores = {}

    for block_name in blocks:
        block_path = os.path.join(blocks_dir, block_name)
        img = cv2.imread(block_path, 0)
        if img is None:
            print(f"[!] Image not found: {block_path}")
            continue
        res = cv2.matchTemplate(template, img, cv2.TM_CCOEFF_NORMED)
        score = res.max()
        scores[block_name] = score
        print(f"{block_name} → score {score:.4f}")

    best_block = max(scores, key = scores.get)
    best_score = scores[best_block]

    print(f"\nBlock kept: {best_block} (score {best_score:.4f})")

    for block_name, score in scores.items():
        if block_name != best_block:
            path = os.path.join(blocks_dir, block_name)
            os.remove(path)
            print(f"{block_name} removed (score {score:.4f})")
    
    scores.clear()  # Clear scores for the next comparison

comparison(blocks, template_path, blocks_dir)

def find_yellow():
    global h, w, x_min, x_max, y_min, y_max, img_yellow, points
    img_yellow = cv2.imread(image_path)
    if img_yellow is None:
        raise FileNotFoundError(f"Image {image_path} not found.")

    h, w, _ = img_yellow.shape

    #  Apply the cropping directly here
    x_min = int(reply_zone["x_min_pct"] * w)
    x_max = int(reply_zone["x_max_pct"] * w)
    y_min = int(reply_zone["y_min_pct"] * h)
    y_max = h

    points = np.array([
    [x_min, y_min],
    [x_max, y_min],
    [x_max, y_max],
    [x_min, y_max]
], dtype=np.int32)
    
    roi = img_yellow[y_min:y_max, x_min:x_max]  # Cropped image (Region Of Interest)
    cv2.imwrite("roi.png", roi)

    # ↓ Downsampling to speed up processing
    roi_small = cv2.resize(roi, (roi.shape[1] // 4, roi.shape[0] // 4))

    h, w = roi.shape[:2]

    x_min = int(reply_zone["x_min_pct"] * w)
    x_max = int(reply_zone["x_max_pct"] * w)
    y_min = int(reply_zone["y_min_pct"] * h)
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

def find_red():
    global h, w, x_min, x_max, y_min, y_max, img_red, points
    img_red = cv2.imread(image_path)
    if img_red is None:
        raise FileNotFoundError(f"Image {image_path} not found.")

    h, w, _ = img_red.shape

    # Get the position and size of the window
    x_min = int(reply_zone["x_min_pct"] * w)
    x_max = int(reply_zone["x_max_pct"] * w)
    y_min = int(reply_zone["y_min_pct"] * h)
    y_max = h

    points = np.array([
    [x_min, y_min],
    [x_max, y_min],
    [x_max, y_max],
    [x_min, y_max]
    ], dtype=np.int32)
    
    roi = img_red[y_min:y_max, x_min:x_max]  # cropped image (Region Of Interest)
    cv2.imwrite("roi.png", roi)

    # ↓ Downsampling to speed up processing
    roi_small = cv2.resize(roi, (roi.shape[1] // 4, roi.shape[0] // 4))

    h, w = roi.shape[:2]

    x_min = int(reply_zone["x_min_pct"] * w)
    x_max = int(reply_zone["x_max_pct"] * w)
    y_min = int(reply_zone["y_min_pct"] * h)
    y_max = h

    hsv = cv2.cvtColor(roi_small, cv2.COLOR_BGR2HSV)  # BGR → HSV

    # Dynamic red range
    # 1st range: dark red to medium (Hue around 0)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    mask_1 = cv2.inRange(hsv, lower_red1, upper_red1)

    ratio_1 = cv2.countNonZero(mask_1) / (mask_1.shape[0] * mask_1.shape[1])
    cv2.imwrite("debug_mask_1.png", mask_1)

    if ratio_1 > 0.01:
        print("End of dialogue detected → the player must save and exit")
        return True

    return False

# Example: 4 points of the rectangle (order is important to ensure it is properly closed)
# find_yellow()
# cv2.polylines(img_yellow, [points], isClosed=True, color=(100, 100, 255), thickness=5)
# cv2.imwrite("yellow_contours.png", img_yellow)

# Example: 4 points of the rectangle (order is important to ensure it is properly closed)
# find_red()
# cv2.polylines(img_red, [points], isClosed=True, color=(0, 0, 255), thickness=2)
# cv2.imwrite("red_contours.png", img_red)

def main_loop():
    get_blocks_and_template(msg_nb, all_messages)
    get_bluestacks_window