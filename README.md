# prosthetic-arm-teleoperation

Pure Python + Computer Vision control system for a prosthetic arm running Arduino firmware. Real-time gesture recognition and motor control via USB serial communication.

## Contents
- `arm_control/` — Python library for motor commands and Arduino communication
- `vision/` — Computer vision gesture recognition (MediaPipe, OpenCV)
- `examples/` — Demo scripts and calibration tools
- `arduino/` — Arduino firmware for motor control (optional reference)
- `README.md`, `LICENSE`, `.gitignore` — standard repo files

## Requirements
- Python 3.8+
- OpenCV (`opencv-python`)
- MediaPipe (gesture/pose recognition)
- PySerial (Arduino communication)

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Start
1. Connect Arduino board to USB
2. Update the COM port in `arm_control/serial_config.py` (e.g., `COM3`)
3. Run a demo:

```powershell
python examples/gesture_control.py
```

## Arduino Setup
If using Arduino, upload the firmware in `arduino/` to your board and ensure baud rate matches `serial_config.py` (default 9600).

## Contributing
PRs and issues welcome. Please include usage examples with any new features.

## License
This project is released under the MIT License — see `LICENSE`.
