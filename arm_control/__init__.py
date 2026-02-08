"""Prosthetic arm control library."""
from .arduino_serial import ArduinoController
from .servo_config import ServoConfig

__all__ = ['ArduinoController', 'ServoConfig']
