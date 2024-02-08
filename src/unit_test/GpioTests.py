import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))
sys.path.insert(0, os.path.abspath('../mock'))
 
from Gpio import Gpio, InputGpioBus, OutputGpioBus, CounterBasedAddressBus
from MockGpio import MockGpio

def main():
    pins = [1, 4, 8, 9]
    gpio = MockGpio()

    print("InputGpioBus")
    inputBus = InputGpioBus(gpio, pins)
    print("")
    inputBus.Read()
    print("")

    print("InputGpioBus")
    outputBus = OutputGpioBus(gpio, pins)
    print("")
    outputBus.Write(7)
    print("")
    outputBus.Write(5)
    print("")
    outputBus.Write(0)
    print("")
    outputBus.Write(15)

    print("CounterBasedAddressBus")
    width = 4
    freq = 5 # 5hz
    clockPin = 1
    resetPin = 4
    addressBus = CounterBasedAddressBus(gpio, width, freq, clockPin, resetPin)

    print("offset 0")
    offset = 0
    addressBus.Write(offset)

    print("offset 1")
    offset = 1
    addressBus.Write(offset)

    print("offset 8")
    offset = 8
    addressBus.Write(offset)

    print("offset 4")
    offset = 4
    addressBus.Write(offset)

    print("reset")
    addressBus.Reset()
if __name__ == "__main__":
    main() 
