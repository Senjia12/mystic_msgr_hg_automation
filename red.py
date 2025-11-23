# red detection feature : red is displayed inside area when the ingame discussion has ended

import numpy as np
import cv2

x_min = 80
x_max = 355
y_min = 760
y_max = 800
x = 0
y = 0
y_pct = 0.912
x_pct_1 = 0.166
x_pct_2 = 0.765
rect = None
rect_width = 0
rect_height = 0
side_bar = 45
image_path = "my_image.png"

area = {
    "x_min_pct": 0.166,
    "x_max_pct": 0.755,
    "y_min_pct": 0.92
}

def find_red():
    global h, w, x_min, x_max, y_min, y_max, img, points
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image {image_path} not found.")

    h, w, _ = img.shape

    # Apply the cropping directly here
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
find_red()
cv2.polylines(img, [points], isClosed=True, color=(0, 0, 255), thickness=2)
cv2.imwrite("contours_area.png", img)