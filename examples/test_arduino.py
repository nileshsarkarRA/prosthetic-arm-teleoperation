"""Example: Test Arduino serial communication."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from arm_control import ArduinoController
from arm_control.servo_config import SERVO_PINS, REST_POSITION


def main():
    """Test Arduino connection and servo movement."""
    print("╔════════════════════════════════════════╗")
    print("║     Prosthetic Arm Arduino Test        ║")
    print("╚════════════════════════════════════════╝\n")
    
    # Test servo configuration display
    print("Servo Configuration:")
    for servo, pin in SERVO_PINS.items():
        print(f"  {servo.capitalize():12} → Pin {pin}")
    
    print("\nRest Position:")
    for servo, angle in REST_POSITION.items():
        print(f"  {servo.capitalize():12} → {angle}°")
    
    # Create controller (but don't connect yet)
    controller = ArduinoController()
    
    print("\n" + "="*50)
    print("Attempting to connect to Arduino...")
    print("="*50 + "\n")
    
    if not controller.connect():
        print("\n⚠️  Connection failed. Options:")
        print("  1. Check COM port in arm_control/servo_config.py")
        print("  2. Verify Arduino is connected via USB")
        print("  3. Install CH340 driver if needed (for some Arduino clones)")
        return False
    
    try:
        # Test each servo
        print("\nServo Movement Test:")
        for servo in ['shoulder', 'elbow', 'wrist', 'hand']:
            print(f"\n  Testing {servo.capitalize()}...")
            for angle in [0, 45, 90, 135, 180]:
                print(f"    → {angle}°", end='', flush=True)
                controller.set_servo(servo, angle)
                time.sleep(0.3)
            print()
        
        # Return to rest
        print("\nReturning to rest position...")
        controller.reset_to_rest()
        time.sleep(1)
        
        print("\n✓ All tests completed!")
        
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        controller.disconnect()
    
    return True


if __name__ == '__main__':
    main()
