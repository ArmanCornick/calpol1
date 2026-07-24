#!/usr/bin/env python3

import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

# Low resolution to reduce work for the robot
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
cap.set(cv2.CAP_PROP_FPS, 5)

# Green HSV range
lower_green = np.array([40, 76, 38], dtype=np.uint8)
upper_green = np.array([80, 255, 255], dtype=np.uint8)

cv2.namedWindow("Isolated Green Object", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Isolated Green Object", 240, 180)

while True:
    start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Convert frame to HSV for green detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Find green pixels
    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # Remove small dots/noise
    kernel = np.ones((3, 3), dtype=np.uint8)
    green_mask = cv2.morphologyEx(
        green_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Convert the original camera frame to grayscale
    grayscale_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Keep the grayscale pixels only where green was detected
    isolated_object = cv2.bitwise_and(
        grayscale_frame,
        grayscale_frame,
        mask=green_mask
    )

    cv2.imshow(
        "Isolated Green Object",
        isolated_object
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Limit program to around 5 FPS
    elapsed = time.time() - start_time
    sleep_time = 0.2 - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)

cap.release()
cv2.destroyAllWindows()
