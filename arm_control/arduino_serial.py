"""Arduino communication module via USB serial."""

import serial
import time
import threading
from collections import deque
from .servo_config import BAUD_RATE, PORT, clamp_angle, REST_POSITION

class ArduinoController:
    """Handles serial communication with Arduino for servo control."""
    
    def __init__(self, port=PORT, baud_rate=BAUD_RATE, timeout=1.0):
        """Initialize Arduino controller.
        
        Args:
            port: COM port (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate: Serial baud rate (default 9600)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.connected = False
        self.current_angles = REST_POSITION.copy()
        self.command_queue = deque()
        self.lock = threading.Lock()
        
    def connect(self):
        """Establish serial connection to Arduino."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1.0
            )
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"✓ Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"✗ Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("✓ Disconnected from Arduino")
    
    def set_servo(self, servo_name, angle):
        """Send command to set servo angle.
        
        Args:
            servo_name: 'shoulder', 'elbow', 'wrist', or 'hand'
            angle: Target angle (0-180 degrees)
        """
        if not self.connected:
            print("Warning: Arduino not connected")
            return False
        
        angle = clamp_angle(angle, servo_name)
        
        with self.lock:
            self.current_angles[servo_name] = angle
        
        # Format: S<servo_id>,<angle>\n
        # Example: S0,90\n for shoulder at 90 degrees
        servo_id = {'shoulder': 0, 'elbow': 1, 'wrist': 2, 'hand': 3}[servo_name]
        command = f"S{servo_id},{int(angle)}\n"
        
        try:
            self.serial.write(command.encode())
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def set_multiple_servos(self, angle_dict):
        """Set multiple servos at once.
        
        Args:
            angle_dict: {'servo_name': angle, ...}
        """
        for servo_name, angle in angle_dict.items():
            self.set_servo(servo_name, angle)
    
    def get_current_angles(self):
        """Get current servo angles."""
        with self.lock:
            return self.current_angles.copy()
    
    def reset_to_rest(self):
        """Move all servos to rest position."""
        self.set_multiple_servos(REST_POSITION)

# Example Arduino sketch to upload to your board:
ARDUINO_SKETCH = """
#include <Servo.h>

// Create servo objects
Servo servos[4];
int servo_pins[4] = {2, 3, 4, 5};  // Pins for shoulder, elbow, wrist, hand
int servo_angles[4] = {90, 90, 90, 0};  // Current angles

void setup() {
  Serial.begin(9600);
  
  // Attach servos to pins
  for (int i = 0; i < 4; i++) {
    servos[i].attach(servo_pins[i]);
    servos[i].write(servo_angles[i]);
  }
  
  Serial.println("Arduino ready");
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\\n');
    command.trim();
    
    // Parse command format: S<servo_id>,<angle>
    if (command.startsWith("S")) {
      int comma_pos = command.indexOf(',');
      int servo_id = command.substring(1, comma_pos).toInt();
      int angle = command.substring(comma_pos + 1).toInt();
      
      if (servo_id >= 0 && servo_id < 4 && angle >= 0 && angle <= 180) {
        servos[servo_id].write(angle);
        servo_angles[servo_id] = angle;
      }
    }
  }
}
"""
