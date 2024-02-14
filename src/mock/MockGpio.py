import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from Gpio import Gpio

class MockGpio(Gpio):
    def __init__(self, os = sys.stdout):
        self._os = os

    def ConfigureGpio(self, pin, dir):
        print("GPIO: Configure {0} as {1}".format(pin, dir), file=self._os)

    def ReadGpio(self, pin):
        value = pin << 1
        print("GPIO: Read {0} as {1}".format(pin, value), file=self._os)

    def WriteGpio(self, pin, state):
        print("GPIO: Set {0} to {1}".format(pin, state), file=self._os)

