#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from Core import Disposable
from Gpio import Gpio, State

import RPi.GPIO as GPIO

class RPiGpio(Gpio, Disposable):
    def __init__():
        GPIO.setmode(GPIO.BCM)

    def _OnDispose(self):
        GPIO.cleanup()

    def ConfigureGpio(self, pin, dir):
        GPIO.setup(pin, dir)

    def ReadGpio(self, pin):
        return State.HIGH if GPIO.input(pin) == GPIO.HIGH else State.LOW 

    def WriteGpio(self, pin, state):
        GPIO.output(pin, GPIO.HIGH if state == State.HIGH else GPIO.LOW)
