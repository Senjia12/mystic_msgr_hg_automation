# yellow detection feature : yellow is displayed inside area when the player can send a message ingame

import numpy as np
import cv2

image_path = "my_image.png" # defined in takeScreenshot function in automation script (main and final file : mystic_messenger.py)

area = {
    "x_min_pct": 0.166,
    "x_max_pct": 0.755,
    "y_min_pct": 0.92
}

def find_yellow():
    global h, w, x_min, x_max, y_min, y_max, img, points
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image {image_path} not found.")

    h, w, _ = img.shape

    #  Apply the cropping directly here
    x_min = int(area["x_min_pct"] * w)
    x_max = int(area["x_max_pct"] * w)
    y_min = int(area["y_min_pct"] * h)
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

    x_min = int(area["x_min_pct"] * w)
    x_max = int(area["x_max_pct"] * w)
    y_min = int(area["y_min_pct"] * h)
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

# Example: 4 points of the rectangle (order is important to ensure it is properly closed)
find_yellow()
cv2.polylines(img, [points], isClosed=True, color=(0, 0, 255), thickness=2)
cv2.imwrite("contours_area_reply.png", img)