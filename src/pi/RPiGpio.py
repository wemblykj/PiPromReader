#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from Gpio import Gpio

import RPi.GPIO as GPIO

class RPiGpio(Gpio):
    def ConfigureGpio(self, pin, dir):
        GPIO.setup(pin, dir)

    def ReadGpio(self, pin):
        return GPIO.input(pin) 

    def WriteGpio(self, pin, state):
        GPIO.output(pin, state)
