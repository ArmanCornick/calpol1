#!/usr/bin/env python3
import cv2
import numpy as np
import time
from sparkybotmini import SparkybotMini

# --- PID Tuning ---
KP = 0.15   # Proportional: how hard it reacts to error
KI = 0.001  # Integral: corrects persistent drift
KD = 0.05   # Derivative: dampens oscillation

# --- Thresholds ---
DEAD_ZONE = 0.05          # Ignore if corn center is within 5% of frame center
MIN_GREEN_PIXELS = 200    # Ignore detections smaller than this (noise filter)
MAX_TURN_SPEED = 40       # Cap turn speed so it doesn't snap hard

# --- Camera / HSV ---
lower_green = np.array([40, 76, 38], dtype=np.uint8)
upper_green = np.array([80, 255, 255], dtype=np.uint8)
kernel = np.ones((3, 3), dtype=np.uint8)

# --- Init ---
bot = SparkybotMini()
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
cap.set(cv2.CAP_PROP_FPS, 5)

cv2.namedWindow("Corn Tracker", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Corn Tracker", 320, 240)

# PID state
integral = 0.0
prev_error = 0.0
prev_time = time.time()

def pid(error, dt):
    global integral, prev_error
    integral += error * dt
    integral = max(-1.0, min(1.0, integral))  # clamp windup
    derivative = (error - prev_error) / dt if dt > 0 else 0.0
    prev_error = error
    return KP * error + KI * integral + KD * derivative

def stop():
    bot.set_motor(0, 0, 0, 0)

while True:
    loop_start = time.time()
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_h, frame_w = frame.shape[:2]
    frame_cx = frame_w / 2.0

    # Detect green
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    green_pixels = cv2.countNonZero(mask)

    if green_pixels < MIN_GREEN_PIXELS:
        # Nothing meaningful detected — stop
        stop()
    else:
        # Find centroid of detected green blob
        M = cv2.moments(mask)
        if M["m00"] > 0:
            cx = M["m10"] / M["m00"]

            # Normalized error: -1.0 (far left) to +1.0 (far right)
            error = (cx - frame_cx) / frame_cx

            if abs(error) < DEAD_ZONE:
                # Corn is centered — stop rotating
                stop()
            else:
                now = time.time()
                dt = now - prev_time
                prev_time = now

                output = pid(error, dt)
                turn = int(np.clip(output * MAX_TURN_SPEED, -MAX_TURN_SPEED, MAX_TURN_SPEED))

                # Rotate in place: left motors forward, right motors back (or vice versa)
                # Positive turn = rotate right, negative = rotate left
                bot.set_motor(-turn, turn, -turn, turn)

            # Draw centroid on display
            cv2.circle(frame, (int(cx), frame_h // 2), 5, (0, 255, 0), -1)
        else:
            stop()

    # Display
    display = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.line(display, (frame_w // 2, 0), (frame_w // 2, frame_h), (255, 255, 255), 1)
    cv2.imshow("Corn Tracker", display)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    elapsed = time.time() - loop_start
    sleep_time = 0.2 - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

stop()
cap.release()
cv2.destroyAllWindows()
