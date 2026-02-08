# Prosthetic Arm Gesture Control — Setup Guide

## System Requirements

- **Python 3.12+** (tested with 3.12, 3.13, 3.14)
- **Windows 10/11** (or Linux/Mac with adjustments)
- **Webcam** (USB or built-in)
- **Arduino board** (with servo motors, optional for testing)
- **USB cable** (Arduino to computer)

---

## Installation

### 1. Create Virtual Environment (Python 3.12)

**Using official Python 3.12:**
```powershell
# If you have Python 3.12 installed explicitly
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Or use system Python:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

**What gets installed:**
- `opencv-python` — Camera capture & frame processing
- `mediapipe` — Hand gesture detection (Google's ML model)
- `pyserial` — Arduino communication
- `numpy` — Numerical operations

---

## Testing Before Running

### Test 1: Camera & Hand Detection
```powershell
python examples/test_gesture.py
```

**What to expect:**
- Webcam window opens
- Move your hand in front of camera
- Green skeleton appears on your hand (hand landmarks)
- Bottom left shows: `Hand detected | Confidence: X.XX | Pos: (X.XX, Y.XX)`
- Press **Q** to quit

**Troubleshooting:**
- No hand detected? → Better lighting, keep hand in frame
- Webcam not opening? → Check camera permissions, try `--camera 1`
- Slow detection? → Normal, MediaPipe runs at 20-30 FPS

### Test 2: Arduino Connection (Optional)
```powershell
python examples/test_arduino.py --port COM3
```
Replace `COM3` with your Arduino's port. Servos will move through 0°-180°.

---

## Configuration

### 1. Arduino COM Port
Edit [arm_control/servo_config.py](./arm_control/servo_config.py):
```python
PORT = 'COM3'  # ← Change to your port (COM3, COM4, etc.)
```

**Find your COM port:**
- Windows Device Manager → Ports (COM & LPT)
- Or run: `python -m serial.tools.list_ports`

### 2. Servo Pin Mapping
Edit [arm_control/servo_config.py](./arm_control/servo_config.py):
```python
SERVO_PINS = {
    'shoulder': 2,   # Pin 2 (adjust if different)
    'elbow': 3,
    'wrist': 4,
    'hand': 5
}
```

### 3. Servo Angle Limits
Prevent damage by setting min/max angles:
```python
SERVO_LIMITS = {
    'shoulder': (0, 180),    # Valid range for servo
    'elbow': (0, 180),
    'wrist': (0, 180),
    'hand': (0, 180),
}
```

---

## Arduino Setup

### Upload Firmware

1. **Get Arduino IDE** → https://www.arduino.cc/software
2. **Find the sketch** in [arm_control/arduino_serial.py](./arm_control/arduino_serial.py) (search for `ARDUINO_SKETCH`)
3. **Copy the code:**
   ```cpp
   #include <Servo.h>
   
   Servo servos[4];
   int servo_pins[4] = {2, 3, 4, 5};
   int servo_angles[4] = {90, 90, 90, 0};
   
   void setup() {
     Serial.begin(9600);
     for (int i = 0; i < 4; i++) {
       servos[i].attach(servo_pins[i]);
       servos[i].write(servo_angles[i]);
     }
     Serial.println("Arduino ready");
   }
   
   void loop() {
     if (Serial.available() > 0) {
       String command = Serial.readStringUntil('\n');
       command.trim();
       
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
   ```

4. **Paste into Arduino IDE**
5. **Upload** to your board

### Wiring

| Servo | Arduino Pin | Signal |
|-------|-----------|--------|
| Shoulder | 2 | Signal wire |
| Elbow | 3 | Signal wire |
| Wrist | 4 | Signal wire |
| Hand | 5 | Signal wire |

**Power:** Connect servo `+` to 5V, `-` to GND, signal to declared pin

---

## Running the Full System

Once Arduino is set up and tested:

```powershell
python examples/gesture_arm_control.py --port COM3
```

**Controls:**
- Move hand → Arm follows
- Press **R** → Reset to rest position
- Press **Q** → Quit

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'mediapipe'` | Run `pip install -r requirements.txt` |
| Camera not opening | Check permissions; try `--camera 1` or `--camera 2` |
| Hand not detected | Better lighting; keep hand in frame center |
| Arduino not found | Check COM port; run `python -m serial.tools.list_ports` |
| Servos don't move | Verify wiring; test with `examples/test_arduino.py` |
| Jerky arm movement | Increase `SMOOTHING_FACTOR` in `servo_config.py` |

---

## What's the Vision System?

**MediaPipe Hand Detector** (by Google):
- Pre-trained ML model
- Detects 21 hand landmarks (wrist, fingers, joints)
- Real-time (~30 FPS on modern CPUs)
- No internet needed (runs locally)

**How it maps to arm:**
- Hand X position (left/right) → Shoulder rotation
- Hand Y position (up/down) → Elbow bend  
- Hand rotation → Wrist angle
- Finger spread (distance) → Gripper open/close

---

## File Structure

```
prosthetic-arm/
├── arm_control/
│   ├── arduino_serial.py      # Serial comm with Arduino
│   ├── servo_config.py        # Pin mapping & limits
│   └── __init__.py
├── vision/
│   ├── gesture_recognition.py # MediaPipe hand detection
│   ├── pose_mapper.py         # Hand pose → servo angles
│   └── __init__.py
├── examples/
│   ├── gesture_arm_control.py # ← MAIN: Run this
│   ├── test_gesture.py        # ← Test vision first
│   ├── test_arduino.py        # ← Test Arduino connection
│   └── __init__.py
├── SETUP.md                   # ← You are here
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Test camera: `python examples/test_gesture.py`
3. → Upload Arduino sketch & test: `python examples/test_arduino.py`
4. → Run full system: `python examples/gesture_arm_control.py`

---

**Questions?** Check individual module docstrings:
```powershell
python -c "from arm_control import ArduinoController; help(ArduinoController)"
python -c "from vision import GestureRecognizer; help(GestureRecognizer)"
```
