#!/usr/bin/env python3

from Gpio import GpioHal

import RPi.GPIO as GPIO

class RPiGpio(GpioHal):
    def ConfigureGpio(self, pin, dir):
        GPIO.setup(pin, dir)

    @abstractmethod
    def ReadGpio(self, pin):
        return GPIO.input(pin) 

    @abstractmethod
    def WriteGpio(self, pin, state):
        GPIO.output(pin, state)
