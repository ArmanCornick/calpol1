#!/usr/bin/env python3
# coding: utf-8
"""
Robot Forward Movement Controller
Moves the robot forward for 5 seconds to travel 5 feet, then stops.
Uses Yahboom YB-ERF 01-v3.0 with 4 x 520 RPM omni wheels.
"""

import time
from sparkybotmini import SparkyBotMini

# Motor speed calculation
# Target: 5 feet in 5 seconds = 1 foot/second
# With 520 RPM motors and omni wheels, this requires tuning
# Start with moderate speed (60% power) for smooth acceleration
MOTOR_SPEED = 60  # 0-100 (60% power)
MOVEMENT_DURATION = 5.0  # seconds

def move_robot_forward():
    """
    Move robot forward for 5 seconds to travel 5 feet
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
        
        # Get initial encoder readings for distance tracking
        initial_encoders = robot.get_encoders()
        print(f"📊 Initial encoder readings: {initial_encoders}")
        
        # Get firmware version
        version = robot.get_version()
        print(f"🔧 Firmware version: v{version}\n")
        
        # Start movement
        print(f"🚀 Moving robot forward for {MOVEMENT_DURATION} seconds at {MOTOR_SPEED}% speed...")
        print("   Target distance: 5 feet\n")
        
        # Set all 4 motors to move forward at same speed
        # Motor configuration for omni wheels moving forward:
        # All motors same direction and speed
        robot.set_motor(MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED)
        
        # Track movement
        start_time = time.time()
        while time.time() - start_time < MOVEMENT_DURATION:
            elapsed = time.time() - start_time
            
            # Get current sensor data every 0.5 seconds
            if int(elapsed * 2) % 1 == 0:
                velocity = robot.get_velocity()
                battery = robot.get_battery_voltage()
                encoders = robot.get_encoders()
                
                # Calculate distance traveled (rough estimate based on encoder deltas)
                encoder_delta = sum(abs(encoders[i] - initial_encoders[i]) for i in range(4)) / 4
                
                print(f"⏱️  Time: {elapsed:.1f}s | Velocity: ({velocity[0]:.2f}, {velocity[1]:.2f}, {velocity[2]:.2f}) m/s | "
                      f"Battery: {battery:.1f}V | Encoder avg: {encoder_delta}")
            
            time.sleep(0.1)
        
        # Stop the robot
        print(f"\n⏸️  Stopping robot...")
        robot.set_motor(0, 0, 0, 0)
        time.sleep(0.5)
        
        # Get final readings
        final_encoders = robot.get_encoders()
        final_velocity = robot.get_velocity()
        final_battery = robot.get_battery_voltage()
        
        print(f"\n📊 Final encoder readings: {final_encoders}")
        print(f"📊 Final velocity: {final_velocity}")
        print(f"📊 Battery voltage: {final_battery:.1f}V")
        
        # Calculate distance (encoder-based)
        encoder_deltas = [final_encoders[i] - initial_encoders[i] for i in range(4)]
        avg_encoder_delta = sum(abs(d) for d in encoder_deltas) / 4
        print(f"\n✅ Movement complete!")
        print(f"   Encoder delta (avg): {avg_encoder_delta:.0f} counts")
        print(f"   All 4 motors: {encoder_deltas}")
        
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
    success = move_robot_forward()
    if success:
        print("\n🎉 Robot movement test successful!")
    else:
        print("\n💥 Robot movement test failed!")
