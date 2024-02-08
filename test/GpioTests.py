import sys
import os

sys.path.insert(0, os.path.abspath('../src'))
 
from Gpio import Gpio, InputGpioBus, OutputGpioBus

class MockGpio(Gpio):
    def ConfigureGpio(self, pin, dir):
        print("GPIO: Configure {0} as {1}".format(pin, dir))

    def ReadGpio(self, pin):
        value = pin << 1
        print("GPIO: Read {0} as {1}".format(pin, value))

    def WriteGpio(self, pin, state):
        print("GPIO: Set {0} to {1}".format(pin, state))

def main():
    pins = [1, 4, 8, 9]
    gpio = MockGpio()

    inputBus = InputGpioBus(gpio, pins)
    print("")
    inputBus.Read()
    print("")

    outputBus = OutputGpioBus(gpio, pins)
    print("")
    outputBus.Write(7)
    print("")
    outputBus.Write(5)
    print("")
    outputBus.Write(0)
    print("")
    outputBus.Write(15)

if __name__ == "__main__":
    main() 
