import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from Gpio import Gpio

class MockGpio(Gpio):
    def ConfigureGpio(self, pin, dir):
        print("GPIO: Configure {0} as {1}".format(pin, dir))

    def ReadGpio(self, pin):
        value = pin << 1
        print("GPIO: Read {0} as {1}".format(pin, value))

    def WriteGpio(self, pin, state):
        print("GPIO: Set {0} to {1}".format(pin, state))

