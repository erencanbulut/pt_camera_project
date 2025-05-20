import cv2
import os

# === CONFIGURATION ===
video_path = "/home/workspace/scripts/latency/latency_exp_1.mov"  # Video file
output_folder = "frames_output"
start_time_sec = 0.0     # Start around just before the stopwatch ticks (e.g., 4.99 → 5.00)
duration_sec = 1.0       # How many seconds to analyze (e.g., 1s window)
fps = 240

# ======================

# Create output folder
os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_FPS, fps)

start_frame = int(start_time_sec * fps)
end_frame = int((start_time_sec + duration_sec) * fps)

cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

frame_id = start_frame
while frame_id <= end_frame:
    ret, frame = cap.read()
    if not ret:
        break
    filename = os.path.join(output_folder, f"frame_{frame_id}.png")
    cv2.imwrite(filename, frame)
    frame_id += 1

cap.release()
print(f"Saved frames {start_frame} to {end_frame} in folder: {output_folder}")
