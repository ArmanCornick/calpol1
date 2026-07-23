#!/usr/bin/env python3
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 5)

# HSV ranges converted from given values:
# Hue: 80-160 degrees -> OpenCV hue is 0-179, so divide by 2 -> 40-80
# Saturation: 30%-100% -> 0-255 scale -> 76-255
# Brightness (Value): 15%-100% -> 0-255 scale -> 38-255
lower_green = np.array([40, 76, 38])
upper_green = np.array([80, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Apply RGB channel clamps
    # R: 0-118, G: 118-255, B: 0-255
    mask_rgb = (
        (frame[:, :, 2] <= 118) &           # Red channel 0-118
        (frame[:, :, 1] >= 118) &           # Green channel 118-255
        (frame[:, :, 0] <= 255)             # Blue channel 0-255 (full range, no-op)
    ).astype(np.uint8) * 255

    # Apply HSV ranges
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_hsv = cv2.inRange(hsv, lower_green, upper_green)

    # Combine both masks
    mask = cv2.bitwise_and(mask_rgb, mask_hsv)

    # Apply mask to original frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("Green Isolation", result)

    if cv2.waitKey(200) & 0xFF == ord('q'):  # 200ms = 5 FPS
        break

cap.release()
cv2.destroyAllWindows()
