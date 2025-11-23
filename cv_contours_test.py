# finding the area displaying choices when clicked, preparation for contour detection with image 'denoising' then blocks detection and cropping them for saving

import cv2
import json
import pygetwindow as gw
import os
import numpy as np

# Directory containing the blocks
path = "./blocks"

# Load the full image
img = cv2.imread("my_image.png")
h, w = img.shape[:2]

# Define the search area (central in height)
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

# Loop through each contour to crop and save
for i, cnt in enumerate(contours):
    x, y, w_box, h_box = cv2.boundingRect(cnt)
    y += y_start  # y based on global position not on ROI

    # Filter out small irrelevant contours
    if w_box > 50 and h_box > 30:
        n += 1
        block = img[y:y + h_box, x:x + w_box]
        cv2.imwrite(f"blocks/block_{n}.png", block)

# Redraw on the full image with vertical offset
for cnt in contours:
    cnt[:, 0, 1] += y_start  # Reposition the contour vertically
    cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)

# Save the result
cv2.imwrite("central_zone_contours.png", img)

