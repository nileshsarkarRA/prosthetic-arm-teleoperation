"""Example: Test camera and gesture recognition without arm."""

import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vision.gesture_recognition import GestureRecognizer


def main():
    """Test gesture recognition."""
    try:
        print("Opening camera for gesture test...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Failed to open camera")
            return False
        
        print("✓ Camera opened")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("Initializing MediaPipe gesture recognizer...")
        recognizer = GestureRecognizer()
        print("✓ MediaPipe ready")
        
        print("✓ Press 'Q' to quit")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            # Detect hand
            hand_data = recognizer.detect_hand(frame)
            
            if hand_data:
                recognizer.draw_hand(frame, hand_data)
                
                # Display info
                center = recognizer.get_hand_center(hand_data)
                confidence = hand_data['confidence']
                
                text = f"Hand detected | Confidence: {confidence:.2f} | Pos: ({center[0]:.2f}, {center[1]:.2f})"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (0, 0, 255), 2)
            
            cv2.imshow('Gesture Recognition Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(f"Quit. Processed {frame_count} frames")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        recognizer.release()
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
