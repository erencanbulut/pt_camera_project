# USAGE
# python usv_tracking_ai.py

import cv2
import numpy as np
from collections import deque
from picamera2 import Picamera2
import time

# Define the lower and upper boundaries for the orange color in HSV
orangeLower = (5, 100, 100)
orangeUpper = (15, 255, 255)
pts = deque(maxlen=64)

print("Initializing camera…")
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (1296, 972), "format": "RGB888"}
)
picam2.configure(config)

try:
    raw_stream_config = picam2.camera_config['raw']
    sensor_mode_width = raw_stream_config['size'][0]
    sensor_mode_height = raw_stream_config['size'][1]
    print(f"Raw stream: {sensor_mode_width}x{sensor_mode_height}")
except KeyError:
    print("Defaulting to 2028x1520 for ScalerCrop.")
    sensor_mode_width = 2028
    sensor_mode_height = 1520

picam2.start()
picam2.set_controls({"ScalerCrop": (0, 0, sensor_mode_width, sensor_mode_height)})
time.sleep(2.0)

cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 800, 600)

try:
    while True:
        frame = picam2.capture_array()

        if frame is None or frame.size == 0:
            print("Warning: Captured empty frame.")
            continue

        frame_for_processing = cv2.resize(frame.copy(), (600, 450))
        blurred = cv2.GaussianBlur(frame_for_processing, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, orangeLower, orangeUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        center = None

        if len(cnts) > 0:
            for c in cnts:
                area = cv2.contourArea(c)
                if area < 500:
                    continue

                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = float(w) / h if h != 0 else 0

                if 2.0 < aspect_ratio < 5.0:
                    center = (int(x + w / 2), int(y + h / 2))
                    cv2.rectangle(frame_for_processing, (x, y), (x + w, y + h), (0, 165, 255), 2)
                    cv2.putText(frame_for_processing, "SeaDragon", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    cv2.circle(frame_for_processing, center, 5, (0, 0, 255), -1)
                    pts.appendleft(center)

        # Removed tracking lines section

        cv2.imshow("Frame", frame_for_processing)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    print("Cleaning up...")
    picam2.stop()
    cv2.destroyAllWindows()
    print("Done.")
