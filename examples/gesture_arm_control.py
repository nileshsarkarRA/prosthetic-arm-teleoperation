"""Main demo: Camera-based gesture control of prosthetic arm."""

import cv2
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from arm_control import ArduinoController
from arm_control.servo_config import PORT, SMOOTHING_FACTOR, REST_POSITION
from vision.gesture_recognition import GestureRecognizer
from vision.pose_mapper import PoseMapper


class ArmGestureController:
    """Orchestrates camera input, gesture recognition, and arm control."""
    
    def __init__(self, com_port=PORT, camera_id=0):
        """Initialize gesture arm controller.
        
        Args:
            com_port: Arduino COM port (e.g., 'COM3')
            camera_id: Camera index (0 for default)
        """
        self.com_port = com_port
        self.camera_id = camera_id
        
        # Initialize components
        self.arduino = ArduinoController(port=com_port)
        self.gesture_recognizer = GestureRecognizer()
        self.pose_mapper = PoseMapper()
        
        # State tracking
        self.current_angles = REST_POSITION.copy()
        self.target_angles = REST_POSITION.copy()
        self.smoothing_factor = SMOOTHING_FACTOR
        self.running = False
        
    def connect_arduino(self) -> bool:
        """Connect to Arduino. Returns True if successful."""
        print(f"Connecting to Arduino on {self.com_port}...")
        if not self.arduino.connect():
            print(f"\n⚠️  Could not connect to Arduino on {self.com_port}")
            print("   - Check the COM port in arm_control/servo_config.py")
            print("   - Ensure Arduino is connected and drivers are installed")
            return False
        return True
    
    def process_frame(self, frame) -> tuple:
        """Process single video frame: detect hand → map to arm angles.
        
        Args:
            frame: Input video frame (BGR)
            
        Returns:
            (processed_frame, angles_dict)
        """
        # Detect hand landmarks
        hand_data = self.gesture_recognizer.detect_hand(frame)
        
        # Draw hand on frame
        if hand_data:
            self.gesture_recognizer.draw_hand(frame, hand_data)
            
            # Get hand center and map to arm angles
            hand_center = self.gesture_recognizer.get_hand_center(hand_data)
            new_angles = self.pose_mapper.hand_position_to_arm(hand_center, hand_data)
            
            # Smooth angles for less jittery movement
            if new_angles:
                for servo, angle in new_angles.items():
                    current = self.target_angles.get(servo, 90)
                    smooth_angle = current + self.smoothing_factor * (angle - current)
                    self.target_angles[servo] = smooth_angle
        
        return frame, self.target_angles
    
    def send_angles_to_arm(self):
        """Send target angles to Arduino with smoothing."""
        if not self.arduino.connected:
            return
        
        # Interpolate current → target
        for servo, target in self.target_angles.items():
            current = self.current_angles.get(servo, 90)
            smooth = current + self.smoothing_factor * (target - current)
            self.current_angles[servo] = smooth
            self.arduino.set_servo(servo, smooth)
    
    def run(self):
        """Main control loop: camera → gesture → arm."""
        if not self.connect_arduino():
            print("\nContinuing without Arduino (dry run mode)...")
        
        print("\n📷 Opening camera...")
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {self.camera_id}")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.running = True
        print("\n✓ Ready! Controls:")
        print("  • Move hand to control arm position")
        print("  • Press 'R' to reset to rest position")
        print("  • Press 'Q' to quit")
        print("\n" + "="*50 + "\n")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Mirror frame for easier gesture control
                frame = cv2.flip(frame, 1)
                
                # Process hand detection and angle mapping
                frame, angles = self.process_frame(frame)
                
                # Send angles to arm
                self.send_angles_to_arm()
                
                # Display current angles on screen
                self._draw_angles_on_frame(frame)
                
                # Show window
                cv2.imshow('Prosthetic Arm Gesture Control', frame)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('r'):
                    print("Resetting to rest position...")
                    self.target_angles = REST_POSITION.copy()
                    self.current_angles = REST_POSITION.copy()
                    self.arduino.reset_to_rest()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.gesture_recognizer.release()
            if self.arduino.connected:
                self.arduino.reset_to_rest()
                self.arduino.disconnect()
            self.running = False
        
        return True
    
    def _draw_angles_on_frame(self, frame):
        """Draw current servo angles on frame."""
        y_offset = 30
        for servo, angle in self.current_angles.items():
            text = f"{servo.capitalize()}: {angle:.1f}°"
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (0, 255, 0), 2)
            y_offset += 25


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gesture-controlled prosthetic arm')
    parser.add_argument('--port', default=PORT, help=f'Arduino COM port (default: {PORT})')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--dry-run', action='store_true', help='Run without Arduino')
    
    args = parser.parse_args()
    
    print("╔════════════════════════════════════════╗")
    print("║   Prosthetic Arm Gesture Control       ║")
    print("╚════════════════════════════════════════╝")
    
    controller = ArmGestureController(com_port=args.port, camera_id=args.camera)
    
    if args.dry_run:
        print("Running in dry-run mode (no Arduino)")
        controller.arduino.connected = False
    
    success = controller.run()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
