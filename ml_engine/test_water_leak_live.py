import cv2
from modules.water_leak.leak_pipeline import process_water_frame
from utils.roi_utils import extract_floor
import os

BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "test_images", "wet.jpg")

# 🔁 change this to your test image path


img = cv2.imread(IMAGE_PATH)

if img is None:
    print("Image not found!")
    exit()

# Run water intelligence
result, mask = process_water_frame(img, raining=False)

floor = extract_floor(img)

if result:
    print("WATER ISSUE DETECTED:", result)
    cv2.putText(img, "WATER ISSUE DETECTED",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0,0,255), 2)
else:
    print("No water issue detected")

# Show visual debug
cv2.imshow("Original Image", img)
cv2.imshow("Floor ROI", floor)
cv2.imshow("Water Mask", mask)

cv2.waitKey(0)
cv2.destroyAllWindows()
