import os
import cv2
import glob
import re
import csv

# === CONFIG ===
frames_folder = "/home/workspace/scripts/latency"  # Replace with your folder name
fps = 240  # Recording FPS

# === NUMERIC SORT FUNCTION ===
def extract_frame_number(path):
    match = re.search(r'frame_(\d+)\.png', os.path.basename(path))
    return int(match.group(1)) if match else -1

frame_paths = sorted(
    glob.glob(os.path.join(frames_folder, "frame_*.png")),
    key=extract_frame_number
)

if not frame_paths:
    print("No frames found. Check folder path.")
    exit()

# === INSTRUCTIONS ===
print("\n INSTRUCTIONS:")
print("→ : Next frame")
print("← : Previous frame")
print("'r': Mark REAL stopwatch frame")
print("'p': Mark Pi PREVIEW frame")
print("'s': Save current latency pair")
print("'q': Quit\n")

index = 0
real_frame_idx = None
preview_frame_idx = None
results = []

# === MAIN LOOP ===
while True:
    frame = cv2.imread(frame_paths[index])
    display = frame.copy()

    fname = os.path.basename(frame_paths[index])
    cv2.putText(display, f"Frame: {fname}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    if real_frame_idx == index:
        cv2.putText(display, "Marked: REAL", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    if preview_frame_idx == index:
        cv2.putText(display, "Marked: PREVIEW", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Latency Measurement", display)
    key = cv2.waitKey(0)

    if key == ord('q'):
        break
    elif key == 83:  # →
        index = min(index + 1, len(frame_paths) - 1)
    elif key == 81:  # ←
        index = max(index - 1, 0)
    elif key == ord('r'):
        real_frame_idx = index
        print(f"Marked REAL at {os.path.basename(frame_paths[index])}")
    elif key == ord('p'):
        preview_frame_idx = index
        print(f"Marked PREVIEW at {os.path.basename(frame_paths[index])}")
    elif key == ord('s'):
        if real_frame_idx is not None and preview_frame_idx is not None:
            delta = preview_frame_idx - real_frame_idx
            latency_ms = (delta / fps) * 1000
            result = {
                "Real Frame": os.path.basename(frame_paths[real_frame_idx]),
                "Preview Frame": os.path.basename(frame_paths[preview_frame_idx]),
                "ΔFrames": delta,
                "Latency (ms)": round(latency_ms, 2)
            }
            results.append(result)
            print(f"Saved: {result}")
            real_frame_idx = None
            preview_frame_idx = None
        else:
            print("Please mark both REAL and PREVIEW frames before saving.")

cv2.destroyAllWindows()

# === WRITE TO CSV ===
if results:
    with open("latency_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n {len(results)} latency entries saved to 'latency_results.csv'")
else:
    print("\n No latency entries to save.")
