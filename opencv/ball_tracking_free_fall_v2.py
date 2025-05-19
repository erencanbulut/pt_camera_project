import cv2
import numpy as np
from picamera2 import Picamera2
from collections import deque
import time
import csv
import os

# --- Parameters ---
yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)
pts = deque(maxlen=64)

duration = 1  # Detection time after drop
prep_delay = 3  # Time to get ready before detection
output_dir = "free_fall_detection_results" # Output directory
os.makedirs(output_dir, exist_ok=True)

# --- Get user-defined distance label ---
distance_label = input("Enter the distance label (e.g., 0.5, 1.0 in meters): ")

# --- File paths ---
timestamp = time.strftime("%Y%m%d_%H%M%S")
csv_filename = f"free_fall_detection_{timestamp}.csv"
csv_path = os.path.join(output_dir, csv_filename)
summary_path = os.path.join(output_dir, "summary_results.csv")

# --- Initialize camera ---
print("Initializing PiCamera2...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1296, 972), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# Force full field of view
sensor_mode_width, sensor_mode_height = 2028, 1520
picam2.set_controls({"ScalerCrop": (0, 0, sensor_mode_width, sensor_mode_height)})

# --- Preparation time ---
print(f"Get ready. Detection starts in {prep_delay} seconds...")
time.sleep(prep_delay)

print(f"Starting free-fall detection for {duration} seconds...")
start_time = time.time()
frame_count = 0
detected_count = 0

# --- Create per-frame CSV ---
with open(csv_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Detected", "X", "Y", "Radius (px)"])

    while (time.time() - start_time) < duration:
        frame = picam2.capture_array()
        if frame is None or frame.size == 0:
            continue

        frame_resized = cv2.resize(frame.copy(), (600, 450))
        blurred = cv2.GaussianBlur(frame_resized, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, yellowLower, yellowUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        center = None
        detected = 0
        x, y, radius = -1, -1, -1

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                detected = 1
                x, y = int(x), int(y)

            if radius > 10:
                cv2.circle(frame_resized, (x, y), int(radius), (0, 255, 255), 2)
                cv2.circle(frame_resized, center, 5, (0, 0, 255), -1)

        pts.appendleft(center)
        for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            cv2.line(frame_resized, pts[i - 1], pts[i], (0, 0, 255), thickness)

        writer.writerow([
            round(time.time() - start_time, 3),
            detected,
            x,
            y,
            int(radius) if radius > 0 else -1
        ])

        frame_count += 1
        detected_count += detected

        cv2.imshow("Free Fall Detection", frame_resized)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

picam2.stop()
cv2.destroyAllWindows()

# --- Write summary results ---
detection_rate = (detected_count / frame_count) * 100 if frame_count > 0 else 0

write_header = not os.path.exists(summary_path)
with open(summary_path, mode="a", newline="") as summary_file:
    writer = csv.writer(summary_file)
    if write_header:
        writer.writerow(["Distance", "Total Frames", "Detected Frames", "Detection Rate (%)"])
    writer.writerow([distance_label, frame_count, detected_count, round(detection_rate, 2)])

print(f"\n✅ Detection complete.")
print(f"Per-frame CSV saved: {csv_path}")
print(f"Summary updated: {summary_path}")
