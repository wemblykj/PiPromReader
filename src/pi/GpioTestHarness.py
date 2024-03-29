import sys
import os
import io

sys.path.insert(0, os.path.abspath('../lib'))
sys.path.insert(0, os.path.abspath('../mock'))
 
from Gpio import Gpio, InputGpioBus, OutputGpioBus, CounterBasedAddressBus
from RPiGpio import RPiGpio

from MockGpio import MockGpio

from BusReader import BusReader
from HexDumper import HexDumper

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

#
# Constants
#

# Address output GPIO pins defined in lowbit to highbit order (A0-A14)
# we will have to support addition address lines via manual means such
# as a DIP switch prompt
#AddressPins = (10,9,11,25,8,7,5,6,12,13,19,16,20,21,26)
AddressPins = (10,9,11,25)

# Data input GPIO pins defined in lowbit to highbit order (D0-D7)
#DataPins = (14,15,18,17,27,22,23,24)
DataPins = (17,27,22,11,5,6,13,19)

Width = 20
Freq = 0 #8000 #50 # 5hz
ClockPin = 14 #9
ResetPin = 15

#ChipEnable = 3
#OutputEnable = 4

class MyIO(io.StringIO):
    def __init__(self, win):
        self._win = win

    def write(self, text: str):
        self._win.addstr(text)
        #lines = text.split('\n')
        #for line in lines:
        #    self._win.addstr(line)
        self._win.refresh()

def main(stdscr):
    #screen = stdscr.subwin(23, 79, 0, 0)
    #screen.box()
    #screen.border(2)
    #screen.hline(2, 1, curses.ACS_HLINE, 77)
    #screen.scrollok(1) # enable scrolling
    #screen.refresh() 
    #stdscr.box()
    #editwin = curses.newwin()
    #editwin.refresh()
    gpio = RPiGpio()
    #gpio = MockGpio(MyIO(screen))
    #gpio = MockGpio(sys.stdout)

    dataBus = InputGpioBus(gpio, DataPins)

    #addressBus = OutputGpioBus(gpio, AddressPins)

    addressBus = CounterBasedAddressBus(gpio, Width, Freq, ResetPin, ClockPin)

    busReader = BusReader(addressBus, dataBus)
    hexDumper = HexDumper(sys.stdout)

    blockSize = 16
    upperBound = 1024 #addressBus.upperbound
    offset = 0
    while offset < upperBound:
        block = busReader.Read(blockSize)
        hexDumper.Write(block)
        offset += blockSize


if __name__ == "__main__":
    main(None) 
 
#wrapper(main)
