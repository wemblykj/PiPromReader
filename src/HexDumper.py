#!/usr/bin/env python3

import sys
import os

from Core import Disposable
from Reader import BytesSink

class HexDumperOptions():
    def __init__(self, columnsPerLine = 16, showAscii = True):
        self.columnsPerLine = columnsPerLine
        self.showAscii = showAscii

    @classmethod
    def fromArgs(cls, args):
        pass

class HexDumper(BytesSink, Disposable):
    def __init__(self, ostream, options : HexDumperOptions = HexDumperOptions()):
        super(HexDumper, self).__init__()
        self.options = options
        self.os = ostream
        self.Reset()

    def Reset(self):
        self._offset = 0
        self._buffer = []
    
    def Write(self, data):
        self._buffer += data

        count = len(self._buffer)
        span = self.options.columnsPerLine
        while count >= span:
            self._WriteLine(self._offset, self._buffer[:span])
            self._buffer = self._buffer[span:]
            self._offset += span
            count -= span

    def _OnDispose(self):
        if len(self._buffer) > 0:
            self._WriteLine(self._offset, self._buffer)

    def _WriteLine(self, offset, data):
        # Convert Address to ASCII hexadecimal
        offsetAsHex="%0.8X"% offset

        # Print line start address
        print(offsetAsHex,"",end=" ", file=self.os)

        #Clear the line buffers
        hexLine=""
        asciiLine="" 

        count = len(data)

        # Output x columns per line
            
        for column in range (0,self.options.columnsPerLine):

            if (column<count):
                byte = data[column]
                dataAsHex="%0.2X "% int(byte)
                hexLine += dataAsHex

                if self.options.showAscii:
                    byteAsInt = int(byte)
                    if (byteAsInt>31 & byteAsInt <128):
                        asciiLine += chr(byteAsInt)
                    # Otherwise just add '.'    
                    else:
                        asciiLine += "."
            else:
                hexLine += "   "

        print(hexLine,end=" ", file=self.os)

        if self.options.showAscii:
            print(asciiLine, file=self.os)
        else:
            print()
