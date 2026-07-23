#!/usr/bin/env python3
# coding: utf-8
"""
Robot Camera Viewer with Network Streaming
Displays live grayscale feed from USB webcam mounted on front of robot
100x200 resolution at 5 FPS
Uses Raspberry Pi 5 with USB webcam
Streams video over HTTP to view from any browser
"""

import cv2
import time
import threading
from flask import Flask, render_template_string, Response

app = Flask(__name__)

# Camera settings
CAMERA_INDEX = 0  # USB webcam (usually /dev/video0)
FRAME_WIDTH = 100
FRAME_HEIGHT = 200
TARGET_FPS = 5
FRAME_DELAY = 1.0 / TARGET_FPS  # Time between frames in seconds

# Global camera and frame variables
camera = None
current_frame = None
frame_lock = threading.Lock()
frame_count = 0
start_time = None

def init_camera():
    """Initialize the camera."""
    print("📷 Initializing USB webcam...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("❌ Failed to open camera at index", CAMERA_INDEX)
        return None
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    
    # Verify settings
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Camera initialized")
    print(f"   Resolution: {actual_width}x{actual_height}")
    print(f"   Target FPS: {TARGET_FPS}")
    print(f"   Actual FPS: {actual_fps:.1f}\n")
    
    return cap

def camera_feed_thread():
    """
    Capture frames from camera in a separate thread.
    """
    global camera, current_frame, frame_count, start_time
    
    camera = init_camera()
    if camera is None:
        return
    
    start_time = time.time()
    last_frame_time = time.time()
    
    print("🎥 Camera feed thread started")
    print("   View stream at: http://[RASPBERRY_PI_IP]:5000\n")
    
    try:
        while True:
            # Maintain target FPS
            current_time = time.time()
            elapsed = current_time - last_frame_time
            
            if elapsed < FRAME_DELAY:
                time.sleep(FRAME_DELAY - elapsed)
            
            last_frame_time = time.time()
            
            # Capture frame
            ret, frame = camera.read()
            
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Store frame for streaming
            with frame_lock:
                current_frame = gray_frame
            
            frame_count += 1
            
            # Print stats every 5 frames
            if frame_count % 5 == 0:
                elapsed_total = time.time() - start_time
                actual_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
                print(f"⏱️  Frame {frame_count} | Actual FPS: {actual_fps:.2f}")
    
    except Exception as e:
        print(f"\n❌ Error in camera thread: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if camera:
            camera.release()
        print("🔌 Camera disconnected")

def generate_frames():
    """
    Generate JPEG frames for streaming.
    """
    global current_frame
    
    while True:
        with frame_lock:
            if current_frame is None:
                continue
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', current_frame)
            frame_data = buffer.tobytes()
        
        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame_data)).encode() + b'\r\n\r\n'
               + frame_data + b'\r\n')
        
        time.sleep(0.05)  # 20 Hz update rate for smooth viewing

@app.route('/')
def index():
    """Serve the HTML page with video stream."""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Robot Camera Viewer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #1a1a1a;
                color: #fff;
                padding: 20px;
            }
            h1 {
                color: #4CAF50;
            }
            img {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                max-width: 100%;
                height: auto;
            }
            .stats {
                margin-top: 20px;
                font-family: monospace;
                background-color: #333;
                padding: 15px;
                border-radius: 5px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>🤖 Robot Camera Viewer</h1>
        <p>Live Grayscale Feed (100x200 @ 5 FPS)</p>
        <img src="{{ url_for('video_feed') }}" width="400" height="800">
        <div class="stats">
            <p>Settings:</p>
            <p>Resolution: 100x200<br>Target FPS: 5<br>Format: Grayscale<br>Camera: USB Webcam</p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    """Stream video feed as MJPEG."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    """
    Start the camera feed thread and Flask web server.
    """
    print("\n" + "="*50)
    print("🤖 Robot Camera Viewer (Network Streaming)")
    print("="*50)
    print("\nSettings:")
    print(f"  Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  FPS: {TARGET_FPS}")
    print(f"  Format: Grayscale")
    print(f"  Camera: USB Webcam\n")
    
    # Start camera feed in background thread
    camera_thread = threading.Thread(target=camera_feed_thread, daemon=True)
    camera_thread.start()
    
    # Give camera time to initialize
    time.sleep(1)
    
    # Start Flask web server
    print("🌐 Starting web server...")
    print("   Access camera stream at: http://localhost:5000")
    print("   Or from another machine: http://[RASPBERRY_PI_IP]:5000\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n✋ Stopping camera feed...")
        print("\n🎉 Camera session ended successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
