#!/usr/bin/env python3
# coding: utf-8
"""
Robot Square Movement Controller
Moves robot in a square pattern: forward 2 feet, turn 90°, repeat 3 times
Uses Yahboom YB-ERF 01-v3.0 with 4 x 550 RPM omni wheels.
"""

import time
from sparkybotmini import SparkyBotMini

# Motor speed and timing calibration
# 550 RPM motors with omni wheels
MOTOR_SPEED = 70  # 0-100 (70% power for smooth movement)

# Distance and rotation parameters
FORWARD_DISTANCE_FEET = 2.0  # Move forward 2 feet per segment
TARGET_DISTANCE_METERS = FORWARD_DISTANCE_FEET * 0.3048  # Convert to meters

# Encoder calibration for 550 RPM motors with omni wheels
# Adjust these values based on actual testing
ENCODER_COUNTS_PER_METER = 1500  # Counts per meter traveled (needs tuning)
ENCODER_COUNTS_PER_ROTATION = 3000  # Counts for full 360° rotation (needs tuning)

# Square pattern: 3 segments (forward-turn-forward-turn-forward-turn, 3 times = 9 moves, but it forms a square after 4)
# We'll do 3 complete cycles
CYCLES = 3

def move_forward_distance(robot, distance_meters, motor_speed):
    """
    Move robot forward for a specific distance
    
    Args:
        robot: SparkyBotMini instance
        distance_meters: Distance to travel in meters
        motor_speed: Motor speed (0-100)
    """
    target_encoder_delta = int(distance_meters * ENCODER_COUNTS_PER_METER)
    
    print(f"  🚀 Moving forward {distance_meters:.2f}m ({distance_meters * 3.28084:.2f} ft) at {motor_speed}% speed...")
    
    # Get initial encoder readings
    initial_encoders = robot.get_encoders()
    print(f"     Initial encoders: {initial_encoders}")
    
    # Start movement - all motors same direction for forward motion
    robot.set_motor(motor_speed, motor_speed, motor_speed, motor_speed)
    
    # Monitor movement
    start_time = time.time()
    max_movement_time = 15.0  # Safety timeout
    
    while time.time() - start_time < max_movement_time:
        current_encoders = robot.get_encoders()
        
        # Calculate average encoder delta
        encoder_deltas = [abs(current_encoders[i] - initial_encoders[i]) for i in range(4)]
        avg_delta = sum(encoder_deltas) / 4
        
        elapsed = time.time() - start_time
        
        # Print progress every 0.5 seconds
        if int(elapsed * 2) % 1 == 0:
            print(f"     ⏱️  {elapsed:.1f}s | Encoder delta (avg): {avg_delta:.0f}/{target_encoder_delta} | "
                  f"Individual: {[f'{d:.0f}' for d in encoder_deltas]}")
        
        # Check if we've traveled the target distance
        if avg_delta >= target_encoder_delta:
            print(f"     ✅ Distance reached: {avg_delta:.0f} counts")
            break
        
        time.sleep(0.1)
    
    # Stop movement
    robot.set_motor(0, 0, 0, 0)
    time.sleep(0.2)
    
    final_encoders = robot.get_encoders()
    final_deltas = [abs(final_encoders[i] - initial_encoders[i]) for i in range(4)]
    print(f"     Final encoders: {final_encoders} | Deltas: {final_deltas}\n")

def turn_90_degrees(robot, motor_speed, clockwise=True):
    """
    Turn robot 90 degrees in place
    
    Args:
        robot: SparkyBotMini instance
        motor_speed: Motor speed (0-100)
        clockwise: True for clockwise, False for counter-clockwise
    """
    target_encoder_delta = int(ENCODER_COUNTS_PER_ROTATION / 4)  # 90° = 1/4 rotation
    
    direction_str = "clockwise (right)" if clockwise else "counter-clockwise (left)"
    print(f"  🔄 Turning 90° {direction_str} at {motor_speed}% speed...")
    
    # Get initial encoder readings
    initial_encoders = robot.get_encoders()
    print(f"     Initial encoders: {initial_encoders}")
    
    # For omni wheels: clockwise rotation
    # Motor configuration for 90° turn (in-place rotation):
    # Clockwise: left motors forward, right motors backward
    # Counter-clockwise: left motors backward, right motors forward
    if clockwise:
        # Motors 1,2 (left) forward; Motors 3,4 (right) backward
        robot.set_motor(motor_speed, motor_speed, -motor_speed, -motor_speed)
    else:
        # Motors 1,2 (left) backward; Motors 3,4 (right) forward
        robot.set_motor(-motor_speed, -motor_speed, motor_speed, motor_speed)
    
    # Monitor rotation
    start_time = time.time()
    max_rotation_time = 10.0  # Safety timeout
    
    while time.time() - start_time < max_rotation_time:
        current_encoders = robot.get_encoders()
        
        # Calculate average encoder delta
        encoder_deltas = [abs(current_encoders[i] - initial_encoders[i]) for i in range(4)]
        avg_delta = sum(encoder_deltas) / 4
        
        elapsed = time.time() - start_time
        
        # Print progress every 0.5 seconds
        if int(elapsed * 2) % 1 == 0:
            print(f"     ⏱️  {elapsed:.1f}s | Encoder delta (avg): {avg_delta:.0f}/{target_encoder_delta} | "
                  f"Individual: {[f'{d:.0f}' for d in encoder_deltas]}")
        
        # Check if we've completed the 90° turn
        if avg_delta >= target_encoder_delta:
            print(f"     ✅ 90° turn completed: {avg_delta:.0f} counts")
            break
        
        time.sleep(0.1)
    
    # Stop rotation
    robot.set_motor(0, 0, 0, 0)
    time.sleep(0.2)
    
    final_encoders = robot.get_encoders()
    final_deltas = [abs(final_encoders[i] - initial_encoders[i]) for i in range(4)]
    print(f"     Final encoders: {final_encoders} | Deltas: {final_deltas}\n")

def robot_square_pattern():
    """
    Execute square pattern movement: forward 2ft, turn 90°, repeat 3 times
    """
    # Initialize robot
    robot = SparkyBotMini(port="/dev/ttyUSB0", baudrate=115200, debug=True)
    
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
        print(f"🔧 Firmware version: v{version}\n")
        
        print(f"📋 Starting square pattern: {CYCLES} cycles")
        print(f"   Each cycle: 2 ft forward → 90° turn\n")
        
        # Execute square pattern
        for cycle in range(CYCLES):
            print(f"▶️  Cycle {cycle + 1}/{CYCLES}\n")
            
            # Move forward
            move_forward_distance(robot, TARGET_DISTANCE_METERS, MOTOR_SPEED)
            
            # Turn 90 degrees clockwise
            turn_90_degrees(robot, MOTOR_SPEED, clockwise=True)
        
        print("✅ Square pattern complete!")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        robot.set_motor(0, 0, 0, 0)
        return False
    
    except Exception as e:
        print(f"\n❌ Error during movement: {e}")
        robot.set_motor(0, 0, 0, 0)
        return False
    
    finally:
        # Ensure motors are stopped
        robot.set_motor(0, 0, 0, 0)
        
        # Disconnect
        robot.disconnect()
        print("🔌 Disconnected from robot")


if __name__ == "__main__":
    success = robot_square_pattern()
    if success:
        print("\n🎉 Robot square pattern test successful!")
    else:
        print("\n💥 Robot square pattern test failed!")
