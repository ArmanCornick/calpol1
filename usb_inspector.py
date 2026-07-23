#!/usr/bin/env python3
import subprocess
import os

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()

print("\n" + "="*50)
print("USB DEVICE INSPECTOR")
print("="*50)

print("\n--- USB Devices (lsusb) ---")
print(run("lsusb"))

print("\n--- Video Devices ---")
print(run("ls -la /dev/video* 2>/dev/null || echo 'No video devices found'"))

print("\n--- V4L2 Devices ---")
print(run("v4l2-ctl --list-devices 2>/dev/null || echo 'v4l2-ctl not installed'"))

print("\n--- All USB Ports & Connected Devices ---")
print(run("ls /sys/bus/usb/devices/"))

print("\n--- Detailed USB Tree ---")
print(run("lsusb -t"))

print("\n--- dmesg USB Events (last 30 lines) ---")
print(run("dmesg | grep -i usb | tail -30"))

print("\n--- Serial/ttyUSB Devices ---")
print(run("ls -la /dev/ttyUSB* 2>/dev/null || echo 'No ttyUSB devices found'"))
print(run("ls -la /dev/ttyACM* 2>/dev/null || echo 'No ttyACM devices found'"))

print("\n" + "="*50)
