#!/usr/bin/env python3
# coding: utf-8

"""
Robot Camera Viewer with Network Streaming
Displays live grayscale feed from USB webcam mounted on front of robot
Uses Raspberry Pi 5 with USB webcam
Streams video over HTTP to view from any browser
"""

import cv2
import time
import threading
from flask import Flask, Response, render_template_string

app = Flask(__name__)

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 5
FRAME_DELAY = 1.0 / TARGET_FPS

# Global state
current_frame = None
frame_lock = threading.Lock()

def init_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("❌ Failed to open camera at index", CAMERA_INDEX)
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    print(f"✅ Camera initialized: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    return cap

def camera_feed_thread():
    global current_frame
    cap = init_camera()
    if cap is None:
        return

    print("🎥 Camera thread running...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, jpeg = cv2.imencode('.jpg', gray)

        with frame_lock:
            current_frame = jpeg.tobytes()

        time.sleep(FRAME_DELAY)

def generate_frames():
    global current_frame
    while True:
        with frame_lock:
            frame = current_frame

        if frame is None:
            time.sleep(0.05)
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )
        time.sleep(FRAME_DELAY)

@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Robot Camera</title>
        <style>
            body { background: #1a1a1a; color: #fff; text-align: center; font-family: Arial, sans-serif; padding: 20px; }
            img { border: 2px solid #4CAF50; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🤖 Robot Camera Feed</h1>
        <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    print("\n🤖 Robot Camera Viewer")
    print("=" * 40)
    t = threading.Thread(target=camera_feed_thread, daemon=True)
    t.start()

    # Wait for first frame before serving
    print("⏳ Waiting for camera...")
    while current_frame is None:
        time.sleep(0.1)
    print("✅ Camera ready")
    print("🌐 Open http://localhost:5000 in your browser\n")

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
