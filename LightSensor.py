import RPi.GPIO as GPIO
import time
from Singleton import Singleton
channel = 13


class LightSensor(metaclass=Singleton):
    """docstring for ClassName"""
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.IN)

    def getCurrentLightStatus(self):
        if GPIO.input(channel) == GPIO.LOW:
            # This means the enivernment is bright
            print("GPIO 27 Is LOW")
            return 1000
        else:
            # this means the eniverniment is dark
            print("GPIO 27 is HIGH")
            return 1
        