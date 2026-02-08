"""Servo configuration and angle mappings for prosthetic arm."""

# Arduino pin assignments (adjust based on your wiring)
SERVO_PINS = {
    'shoulder': 2,      # Shoulder rotation (0-180°)
    'elbow': 3,         # Elbow bend (0-180°)
    'wrist': 4,         # Wrist rotation (0-180°)
    'hand': 5,          # Hand open/close (0-180°)
}

# Min/max angles for each servo to prevent damage
SERVO_LIMITS = {
    'shoulder': (0, 180),
    'elbow': (0, 180),
    'wrist': (0, 180),
    'hand': (0, 180),   # 0 = open, 180 = closed
}

# Default rest position (degrees)
REST_POSITION = {
    'shoulder': 90,
    'elbow': 90,
    'wrist': 90,
    'hand': 0,          # Open
}

# Smoothing factor (0.0-1.0) for servo movement
SMOOTHING_FACTOR = 0.3

# Serial communication
BAUD_RATE = 9600
PORT = 'COM3'  # Change to your Arduino port (COM3, COM4, /dev/ttyUSB0, etc.)

def clamp_angle(angle, servo_name):
    """Clamp angle to servo limits."""
    min_angle, max_angle = SERVO_LIMITS.get(servo_name, (0, 180))
    return max(min_angle, min(max_angle, angle))
