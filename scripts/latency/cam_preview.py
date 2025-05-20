# cam_preview.py
from picamera2 import Picamera2, Preview
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (1280, 720)}))
picam2.start_preview(Preview.QTGL)  # or Preview.DRM
picam2.start()
input("Press Enter to exit…")
picam2.stop()