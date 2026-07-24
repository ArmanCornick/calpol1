#!/usr/bin/env python3

import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

# Low resolution and low FPS to reduce robot processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
cap.set(cv2.CAP_PROP_FPS, 5)

# Green HSV range
lower_green = np.array([40, 76, 38], dtype=np.uint8)
upper_green = np.array([80, 255, 255], dtype=np.uint8)

kernel = np.ones((3, 3), dtype=np.uint8)

cv2.namedWindow("Binary Green Object", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Binary Green Object", 240, 180)

while True:
    start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Convert camera frame from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Binary detection:
    # green object = 255 (white)
    # everything else = 0 (black)
    binary_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # Remove small white noise
    binary_mask = cv2.morphologyEx(
        binary_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Fill small black gaps inside the detected object
    binary_mask = cv2.morphologyEx(
        binary_mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    cv2.imshow("Binary Green Object", binary_mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Limit processing to about 5 FPS
    elapsed = time.time() - start_time
    sleep_time = 0.2 - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)

cap.release()
cv2.destroyAllWindows()        upper_green
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
