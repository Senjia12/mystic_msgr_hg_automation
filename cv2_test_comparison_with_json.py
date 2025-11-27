# dynamic JSON feature incorporating comparison feature using cv2

import cv2
import json
import os

# === GLOBAL SETTINGS ===
msg_nb = 4  # "blocks group" to compare
json_path = "templates/templates.json"
blocks_dir = "blocks/"
templates_dir = "templates/"
scores = {}

# === Loading JSON ===
with open(json_path, "r") as f:
    all_messages = json.load(f)

def get_blocks_and_template(msg_nb, data):
    msg_data = data.get(str(msg_nb))
    if not msg_data:
        raise ValueError(f"msg_nb {msg_nb} not found in JSON template file.")

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
            print(f"{block_name} deleted (score {score:.4f})")
    
    scores.clear()  # Clear scores for the next comparison

comparison(blocks, template_path, blocks_dir)