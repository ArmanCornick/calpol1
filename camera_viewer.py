#!/usr/bin/env python3
import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
cap.set(cv2.CAP_PROP_FPS, 5)

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

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    binary_mask = cv2.inRange(hsv, lower_green, upper_green)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("Binary Green Object", binary_mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    elapsed = time.time() - start_time
    sleep_time = 0.2 - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

cap.release()
cv2.destroyAllWindows()
