import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))
sys.path.insert(0, os.path.abspath('../mock'))
 
from Gpio import Gpio, InputGpioBus, OutputGpioBus, CounterBasedAddressBus
from RPiGpio import RPiGpio

from MockGpio import MockGpio

#
# Constants
#

# Address output GPIO pins defined in lowbit to highbit order (A0-A14)
# we will have to support addition address lines via manual means such
# as a DIP switch prompt
#AddressPins = (10,9,11,25,8,7,5,6,12,13,19,16,20,21,26)
AddressPins = (10,9,11,25)

# Data input GPIO pins defined in lowbit to highbit order (D0-D7)
DataPins = (14,15,18,17,27,22,23,24)

Width = 4
Freq = 5 # 5hz
ClockPin = 1
ResetPin = 4

def main():
    #gpio = RPiGpio()
    gpio = MockGpio()

    dataBus = InputGpioBus(gpio, DataPins)

    #addressBus = OutputGpioBus(gpio, AddressPins)

    addressBus = CounterBasedAddressBus(gpio, Width, Freq, ClockPin, ResetPin)

    for offset in range(0, addressBus.upperbound):
        addressBus.Write(offset)
        data = dataBus.Read()
        print("{}: {}".format(offset, data))

if __name__ == "__main__":
    main() 
