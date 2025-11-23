import cv2
import json
from pywinauto import Application
import os
import numpy as np
import pyautogui
import time
from pynput import mouse
import pygetwindow as gw

# Directory containing the blocks
path = "./blocks"

# === GLOBAL SETTINGS ===
msg_nb = 4  # "blocks group" to compare
json_path = "templates/templates.json"
blocks_dir = "blocks/"
templates_dir = "templates/"
scores = {}

templates_dir = "templates"
with open("templates/templates.json", "r") as f:
    mapping = json.load(f)

# get BlueStacks window
win = gw.getWindowsWithTitle("BlueStacks App Player")[0]

# Get the position and size of the window
x, y = win.left, win.top
width, height = win.width, win.height

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



# Create blocks directory if not existing already
os.makedirs("blocks", exist_ok=True)
n = 0

# Loop over each contour to crop and save
for i, cnt in enumerate(contours):
    x, y, w_box, h_box = cv2.boundingRect(cnt)
    y += y_start  # adjust y to global position, not just within ROI

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

# === Loading JSON ===
json_path = "templates/templates.json"
with open(json_path, "r") as f:
    all_messages = json.load(f)

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

