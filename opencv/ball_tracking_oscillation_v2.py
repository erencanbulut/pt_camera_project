import cv2
import numpy as np
from collections import deque
from picamera2 import Picamera2
import time
import csv
from datetime import datetime
import os

# Yellow ball HSV bounds
yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)
pts = deque(maxlen=64)

prep_delay = 3  # Time to get ready before detection
duration = 20  # Detection duration after leave the ball
output_dir = "oscillation_detection_results" # Output directory
os.makedirs(output_dir, exist_ok=True)

# Ask distance
test_distance = input("Enter the distance label (e.g., 0.5, 1.0 in meters): ").strip()

# Time and file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"detection_data_{test_distance}m_{timestamp}.csv"
csv_path = os.path.join(output_dir, csv_filename)

# Initialize camera
print("Initializing camera...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1296, 972), "format": "RGB888"}
)
picam2.configure(config)

# --- Preparation time ---
print(f"Get ready. Detection starts in {prep_delay} seconds...")
time.sleep(prep_delay)
print(f"Starting oscillation detection for {duration} seconds...")

# Raw size
try:
    raw_stream_config = picam2.camera_config['raw']
    sensor_mode_width = raw_stream_config['size'][0]
    sensor_mode_height = raw_stream_config['size'][1]
except KeyError:
    sensor_mode_width = 2028
    sensor_mode_height = 1520

picam2.start()
picam2.set_controls({"ScalerCrop": (0, 0, sensor_mode_width, sensor_mode_height)})
time.sleep(2.0)

cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 800, 600)

# Data counters
total_frames = 0
detected_frames = 0

# Write per-frame CSV
csv_file = open(csv_path, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Time (s)", "Detected", "X", "Y", "Radius (px)", "Distance (m)"])

start_time = time.time()
try:
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > duration:
            print(f"{duration} seconds elapsed. Stopping.")
            break

        frame = picam2.capture_array()
        if frame is None or frame.size == 0:
            continue

        frame_proc = cv2.resize(frame.copy(), (600, 450))
        blurred = cv2.GaussianBlur(frame_proc, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, yellowLower, yellowUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        center = None
        detected = False
        radius = 0
        cx = cy = -1

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cx, cy = center
                if radius > 10:
                    detected = True
                    cv2.circle(frame_proc, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame_proc, center, 5, (0, 0, 255), -1)

        pts.appendleft(center)
        for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            cv2.line(frame_proc, pts[i - 1], pts[i], (0, 0, 255), thickness)

        # Track detection stats
        total_frames += 1
        if detected:
            detected_frames += 1

        # Save row
        csv_writer.writerow([
            round(elapsed_time, 2),
            int(detected),
            cx,
            cy,
            round(radius, 2),
            test_distance
        ])

        cv2.imshow("Frame", frame_proc)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("User terminated early.")
            break

except KeyboardInterrupt:
    print("Keyboard interrupt.")
finally:
    print("Finalizing and saving...")

    # Save summary
    detection_rate = 100.0 * detected_frames / total_frames if total_frames else 0
    summary_filename = "summary_results.csv"
    summary_path = os.path.join(output_dir, summary_filename)

    summary_exists = os.path.exists(summary_path)
    with open(summary_path, mode='a', newline='') as summary_file:
        summary_writer = csv.writer(summary_file)
        if not summary_exists:
            summary_writer.writerow(["Distance (m)", "Total Frames", "Detected Frames", "Detection Rate (%)"])
        summary_writer.writerow([
            test_distance,
            total_frames,
            detected_frames,
            round(detection_rate, 2)
        ])

    print(f"Detection CSV saved to: {csv_path}")
    print(f"Summary CSV updated at: {summary_path}")

    csv_file.close()
    picam2.stop()
    cv2.destroyAllWindows()
