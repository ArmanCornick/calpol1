#!/usr/bin/env python3
# coding: utf-8
"""
Robot Camera Viewer
Displays live grayscale feed from USB webcam mounted on front of robot
100x200 resolution at 5 FPS
Uses Raspberry Pi 5 with USB webcam
"""

import cv2
import time

# Camera settings
CAMERA_INDEX = 0  # USB webcam (usually /dev/video0)
FRAME_WIDTH = 100
FRAME_HEIGHT = 200
TARGET_FPS = 5
FRAME_DELAY = 1.0 / TARGET_FPS  # Time between frames in seconds

def display_camera_feed():
    """
    Display live grayscale camera feed from USB webcam.
    """
    # Initialize camera
    print("📷 Initializing USB webcam...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("❌ Failed to open camera at index", CAMERA_INDEX)
        return False
    
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
    
    print("🎥 Camera feed active")
    print("   Press 'q' to quit\n")
    
    frame_count = 0
    start_time = time.time()
    last_frame_time = time.time()
    
    try:
        while True:
            # Maintain target FPS
            current_time = time.time()
            elapsed = current_time - last_frame_time
            
            if elapsed < FRAME_DELAY:
                time.sleep(FRAME_DELAY - elapsed)
            
            last_frame_time = time.time()
            
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Display frame
            cv2.imshow('🤖 Robot Camera (Grayscale 100x200 @ 5 FPS)', gray_frame)
            
            frame_count += 1
            
            # Print stats every 5 frames
            if frame_count % 5 == 0:
                elapsed_total = time.time() - start_time
                actual_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
                print(f"⏱️  Frame {frame_count} | Actual FPS: {actual_fps:.2f}")
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n✋ Stopping camera feed...")
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final stats
        elapsed_total = time.time() - start_time
        actual_fps = frame_count / elapsed_total if elapsed_total > 0 else 0
        print(f"\n📊 Session Stats:")
        print(f"   Total frames: {frame_count}")
        print(f"   Duration: {elapsed_total:.1f}s")
        print(f"   Average FPS: {actual_fps:.2f}")
        print(f"   Target FPS: {TARGET_FPS}")
        print("\n🔌 Camera disconnected")
        return True


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 Robot Camera Viewer")
    print("="*50)
    print("\nSettings:")
    print(f"  Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  FPS: {TARGET_FPS}")
    print(f"  Format: Grayscale")
    print(f"  Camera: USB Webcam\n")
    
    success = display_camera_feed()
    
    if success:
        print("\n🎉 Camera session ended successfully!")
    else:
        print("\n💥 Camera session failed!")
