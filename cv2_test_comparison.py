# comparison feature using cv2 based on templates and blocks of references pre selected manually

import cv2
import json
import os

# === SETTINGS ===
json_path = "templates/templates.json"
blocks_dir = "blocks/"
templates_dir = "templates/"

# === LOADING JSON ===
with open(json_path, "r") as f:
    matches = json.load(f)

# Select blocks 1 and 2
block1_name = "block_1.png"
block2_name = "block_2.png"
template_name = matches[block1_name]  # same as for block_2

# === FILEPATHS ===
block1_path = os.path.join(blocks_dir, block1_name)
block2_path = os.path.join(blocks_dir, block2_name)
template_path = os.path.join(templates_dir, template_name)

# === LOADING IMAGES ===
template = cv2.imread(template_path, 0)
img1 = cv2.imread(block1_path, 0)
img2 = cv2.imread(block2_path, 0)

# === COMPARISON ===
res1 = cv2.matchTemplate(template, img1, cv2.TM_CCOEFF_NORMED)
res2 = cv2.matchTemplate(template, img2, cv2.TM_CCOEFF_NORMED)
score1 = res1.max()
score2 = res2.max()

# === REMOVING THE LEAST SIMILAR ===
if score1 < score2:
    os.remove(block1_path)
    print(f"{block1_name} deleted (score {score1:.4f} < {score2:.4f})")
else:
    os.remove(block2_path)
    print(f"{block2_name} deleted (score {score2:.4f} < {score1:.4f})")
