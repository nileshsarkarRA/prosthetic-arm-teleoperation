"""Hand gesture recognition using MediaPipe."""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple, List, Optional

class GestureRecognizer:
    """Recognize hand pose and extract keypoints using MediaPipe."""
    
    def __init__(self):
        """Initialize MediaPipe hand detector."""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,           # Track one hand
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    
    def detect_hand(self, frame) -> Optional[Dict]:
        """Detect hand landmarks in frame.
        
        Args:
            frame: Input video frame (BGR)
            
        Returns:
            Dictionary with hand keypoints or None if no hand detected
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract keypoints as normalized coordinates (0-1)
            keypoints = []
            for landmark in hand_landmarks.landmark:
                keypoints.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            return {
                'keypoints': keypoints,
                'handedness': results.multi_handedness[0].classification[0].label if results.multi_handedness else 'Unknown',
                'confidence': results.multi_handedness[0].classification[0].score if results.multi_handedness else 0.0
            }
        
        return None
    
    def draw_hand(self, frame, hand_data) -> None:
        """Draw hand landmarks on frame.
        
        Args:
            frame: Input video frame (modified in-place)
            hand_data: Hand detection result from detect_hand()
        """
        if hand_data is None:
            return
        
        # Create dummy hand landmarks object for drawing
        keypoints = hand_data['keypoints']
        frame_h, frame_w = frame.shape[:2]
        
        # Draw circles at keypoints
        for i, kp in enumerate(keypoints):
            x = int(kp['x'] * frame_w)
            y = int(kp['y'] * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
        
        # Draw connections (wrist to fingers)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),      # Index
            (0, 9), (9, 10), (10, 11), (11, 12), # Middle
            (0, 13), (13, 14), (14, 15), (15, 16), # Ring
            (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
        ]
        
        for start, end in connections:
            start_kp = keypoints[start]
            end_kp = keypoints[end]
            start_pos = (int(start_kp['x'] * frame_w), int(start_kp['y'] * frame_h))
            end_pos = (int(end_kp['x'] * frame_w), int(end_kp['y'] * frame_h))
            cv2.line(frame, start_pos, end_pos, (0, 255, 0), 2)
    
    def get_hand_center(self, hand_data) -> Optional[Tuple[float, float]]:
        """Get center of hand (wrist position).
        
        Args:
            hand_data: Hand detection result
            
        Returns:
            (x, y) normalized coordinates or None
        """
        if hand_data is None:
            return None
        
        wrist = hand_data['keypoints'][0]
        return (wrist['x'], wrist['y'])
    
    def get_finger_tips(self, hand_data) -> Optional[Dict[str, Tuple[float, float]]]:
        """Get positions of finger tips.
        
        Args:
            hand_data: Hand detection result
            
        Returns:
            Dictionary with finger tip positions
        """
        if hand_data is None:
            return None
        
        kp = hand_data['keypoints']
        return {
            'thumb': (kp[4]['x'], kp[4]['y']),
            'index': (kp[8]['x'], kp[8]['y']),
            'middle': (kp[12]['x'], kp[12]['y']),
            'ring': (kp[16]['x'], kp[16]['y']),
            'pinky': (kp[20]['x'], kp[20]['y'])
        }
    
    def release(self):
        """Release MediaPipe resources."""
        self.hands.close()
