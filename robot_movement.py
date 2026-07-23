#!/usr/bin/env python3
# coding: utf-8
"""
Robot Interactive Movement Controller
WASD keyboard controls for movement with Q/E for rotation
Uses Yahboom YB-ERF 01-v3.0 with 4 x 550 RPM omni wheels on Raspberry Pi 5

Requires: pip install pynput
"""

import time
from pynput import keyboard
from sparkybotmini import SparkyBotMini

# Motor speed and timing calibration
# 550 RPM motors with omni wheels
MOTOR_SPEED = 70  # 0-100 (70% power for smooth movement)

# Key states - tracks which keys are currently held down
key_pressed = {
    'w': False,  # Forward
    'a': False,  # Left
    's': False,  # Backward
    'd': False,  # Right
    'q': False,  # Turn left (counter-clockwise)
    'e': False,  # Turn right (clockwise)
}

# Control loop flag
control_running = True

def on_press(key):
    """
    Callback for when a key is pressed.
    """
    global key_pressed
    try:
        # Get the character representation
        char = key.char
        if char and char.lower() in key_pressed:
            key_pressed[char.lower()] = True
    except AttributeError:
        # Handle special keys if needed
        pass

def on_release(key):
    """
    Callback for when a key is released.
    """
    global key_pressed, control_running
    try:
        # Get the character representation
        char = key.char
        if char and char.lower() in key_pressed:
            key_pressed[char.lower()] = False
    except AttributeError:
        pass
    
    # Exit on Ctrl+C
    if key == keyboard.Key.esc:
        control_running = False
        return False

def update_motor_commands(robot):
    """
    Update motor commands based on current key states.
    Omni wheels allow for holonomic movement (can move in any direction).
    
    Motor layout (for omni wheels):
    - Motor 1: Front-Left
    - Motor 2: Front-Right
    - Motor 3: Back-Right
    - Motor 4: Back-Left
    """
    speed = MOTOR_SPEED
    
    # Determine movement vector
    forward = int(key_pressed['w']) - int(key_pressed['s'])  # -1, 0, or 1
    strafe = int(key_pressed['d']) - int(key_pressed['a'])   # -1, 0, or 1
    
    # Determine rotation
    rotate = int(key_pressed['e']) - int(key_pressed['q'])   # -1 (CCW), 0, or 1 (CW)
    
    # Holonomic motor commands for omni wheels
    # Each motor gets a combination of forward, strafe, and rotation components
    m1 = forward * speed - strafe * speed + rotate * speed  # Front-Left
    m2 = forward * speed + strafe * speed - rotate * speed  # Front-Right
    m3 = forward * speed + strafe * speed + rotate * speed  # Back-Right
    m4 = forward * speed - strafe * speed - rotate * speed  # Back-Left
    
    # Clamp values to [-100, 100]
    m1 = max(-100, min(100, m1))
    m2 = max(-100, min(100, m2))
    m3 = max(-100, min(100, m3))
    m4 = max(-100, min(100, m4))
    
    # Send command to robot
    robot.set_motor(m1, m2, m3, m4)

def print_controls():
    """
    Print control instructions to the user.
    """
    print("\n" + "="*50)
    print("🤖 Robot Interactive Movement Controller")
    print("="*50)
    print("\n📋 Controls:")
    print("  W - Move Forward")
    print("  A - Strafe Left")
    print("  S - Move Backward")
    print("  D - Strafe Right")
    print("  Q - Turn Left (Counter-Clockwise)")
    print("  E - Turn Right (Clockwise)")
    print("\n  Combine keys for diagonal movement!")
    print("  Example: Hold W+D = forward-right")
    print("  Example: Hold W+E = forward while turning right")
    print("\nPress ESC to exit\n")
    print("="*50 + "\n")

def robot_interactive_control():
    """
    Run interactive WASD keyboard control for the robot with responsive key holding.
    """
    global control_running
    
    # Initialize robot
    robot = SparkyBotMini(port="/dev/ttyUSB0", baudrate=115200, debug=False)
    
    try:
        # Connect to robot
        print("🤖 Connecting to robot...")
        if not robot.connect():
            print("❌ Failed to connect to robot")
            return False
        
        print("✅ Connected to robot")
        time.sleep(0.5)
        
        # Enable auto-reporting for sensor feedback
        robot.set_auto_report(True)
        time.sleep(0.5)
        
        # Get firmware version
        version = robot.get_version()
        print(f"🔧 Firmware version: v{version}")
        
        print_controls()
        
        # Set up keyboard listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        
        print("✅ Keyboard listener active - Ready for control!\n")
        
        # Main control loop
        last_state = None
        iteration = 0
        
        while control_running:
            # Update motor commands based on current key state
            update_motor_commands(robot)
            
            # Print status when key state changes (throttled)
            current_state = key_pressed.copy()
            if current_state != last_state:
                active_keys = [k.upper() for k, v in current_state.items() if v]
                if active_keys:
                    print(f"🎮 Keys held: {' + '.join(active_keys)}")
                else:
                    print("➖ Idle")
                last_state = current_state
            
            iteration += 1
            time.sleep(0.05)  # 20 Hz update rate for smooth control
        
        print("\n✋ Shutting down...")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during movement: {e}")
        import traceback
        traceback.print_exc()
        robot.set_motor(0, 0, 0, 0)
        return False
    
    finally:
        # Ensure motors are stopped
        robot.set_motor(0, 0, 0, 0)
        
        # Disconnect
        robot.disconnect()
        print("🔌 Disconnected from robot")


if __name__ == "__main__":
    print("Starting Robot Controller...\n")
    print("Make sure pynput is installed:")
    print("  pip install pynput\n")
    
    success = robot_interactive_control()
    if success:
        print("\n🎉 Robot interactive control session ended successfully!")
    else:
        print("\n💥 Robot interactive control session failed!")
