"""Map hand pose to arm joint angles."""

import numpy as np
from typing import Dict, Optional

class PoseMapper:
    """Maps hand gesture/pose to prosthetic arm servo angles."""
    
    def __init__(self):
        """Initialize position mapper with calibration defaults."""
        # Screen boundaries (normalized 0-1)
        self.screen_bounds = {
            'left': 0.2,
            'right': 0.8,
            'top': 0.2,
            'bottom': 0.8
        }
        
        # Servo angle ranges
        self.servo_ranges = {
            'shoulder': (0, 180),    # Left-right rotation
            'elbow': (0, 180),       # Up-down bend
            'wrist': (0, 180),       # Rotation
            'hand': (0, 180)         # Open (0) to Closed (180)
        }
    
    def hand_position_to_arm(self, hand_center: tuple, hand_data: Dict) -> Dict[str, float]:
        """Convert hand position to arm joint angles.
        
        Args:
            hand_center: (x, y) normalized hand center position
            hand_data: Full hand detection data with keypoints
            
        Returns:
            Dictionary with servo angles: {'shoulder': angle, 'elbow': angle, ...}
        """
        if hand_center is None or hand_data is None:
            return {}
        
        x, y = hand_center
        
        # Map hand X position to shoulder rotation (horizontal)
        shoulder_angle = self._map_x_to_shoulder(x)
        
        # Map hand Y position to elbow angle (vertical)
        elbow_angle = self._map_y_to_elbow(y)
        
        # Map hand rotation to wrist angle
        wrist_angle = self._calculate_hand_rotation(hand_data)
        
        # Map hand openness (finger spread) to gripper
        hand_angle = self._calculate_hand_openness(hand_data)
        
        return {
            'shoulder': shoulder_angle,
            'elbow': elbow_angle,
            'wrist': wrist_angle,
            'hand': hand_angle
        }
    
    def _map_x_to_shoulder(self, x: float) -> float:
        """Map hand X position to shoulder rotation.
        
        Left side (x=0) -> 45°, Right side (x=1) -> 135°
        """
        # Clamp to screen bounds
        x = max(self.screen_bounds['left'], min(self.screen_bounds['right'], x))
        
        # Normalize to [0, 1] within bounds
        normalized = (x - self.screen_bounds['left']) / (self.screen_bounds['right'] - self.screen_bounds['left'])
        
        # Map to servo range
        min_angle, max_angle = self.servo_ranges['shoulder']
        return min_angle + normalized * (max_angle - min_angle)
    
    def _map_y_to_elbow(self, y: float) -> float:
        """Map hand Y position to elbow angle.
        
        Top (y=0) -> 30° (extended), Bottom (y=1) -> 150° (bent)
        """
        # Clamp to screen bounds
        y = max(self.screen_bounds['top'], min(self.screen_bounds['bottom'], y))
        
        # Normalize to [0, 1] within bounds
        normalized = (y - self.screen_bounds['top']) / (self.screen_bounds['bottom'] - self.screen_bounds['top'])
        
        # Map to servo range (inverted: top = less bent)
        min_angle, max_angle = self.servo_ranges['elbow']
        return min_angle + normalized * (max_angle - min_angle)
    
    def _calculate_hand_rotation(self, hand_data: Dict) -> float:
        """Estimate hand rotation angle from keypoints.
        
        Uses palm and wrist to estimate rotation.
        """
        kp = hand_data['keypoints']
        
        # Calculate angle between wrist and middle finger
        wrist = np.array([kp[0]['x'], kp[0]['y']])
        middle = np.array([kp[9]['x'], kp[9]['y']])
        
        diff = middle - wrist
        angle_rad = np.arctan2(diff[1], diff[0])
        angle_deg = np.degrees(angle_rad)
        
        # Normalize to [0, 180]
        angle_deg = (angle_deg + 90) % 180
        
        return float(angle_deg)
    
    def _calculate_hand_openness(self, hand_data: Dict) -> float:
        """Estimate hand openness (0=open, 180=closed).
        
        Uses distance between fingers to estimate grip.
        """
        kp = hand_data['keypoints']
        
        # Get finger tips
        finger_tips = np.array([
            [kp[4]['x'], kp[4]['y']],   # Thumb
            [kp[8]['x'], kp[8]['y']],   # Index
            [kp[12]['x'], kp[12]['y']], # Middle
            [kp[16]['x'], kp[16]['y']], # Ring
            [kp[20]['x'], kp[20]['y']]  # Pinky
        ])
        
        # Wrist position
        wrist = np.array([kp[0]['x'], kp[0]['y']])
        
        # Average distance from wrist to finger tips
        distances = np.linalg.norm(finger_tips - wrist, axis=1)
        avg_distance = np.mean(distances)
        
        # Threshold: if fingers far from wrist, hand is open (0°)
        # If fingers close to wrist, hand is closed (180°)
        # Typical range: 0.05 (closed) to 0.3 (open)
        openness = 1.0 - np.clip(avg_distance / 0.4, 0, 1)  # 0 = open, 1 = closed
        
        return float(openness * 180.0)
    
    def set_screen_bounds(self, left: float, right: float, top: float, bottom: float):
        """Set active screen bounds for mapping (normalized 0-1)."""
        self.screen_bounds = {
            'left': left,
            'right': right,
            'top': top,
            'bottom': bottom
        }
