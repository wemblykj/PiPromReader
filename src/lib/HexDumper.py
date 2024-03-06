#!/usr/bin/env python3

import sys
import os

#from flags import Flags
from enum import Flag

from Core import Disposable
from BytesReader import BytesSink

class Layout(Flag):
    ADDRESS = 1
    HEXDUMP = 2
    ASCII = 4
    NOASCII = 3
    DEFAULT = 7

class Options():
    def __init__(self, columnsPerLine = 16, layoutFlags : Layout = Layout.DEFAULT):
      self.columnsPerLine = columnsPerLine
      self.layoutFlags = layoutFlags

class HexDumper(BytesSink, Disposable):
    def __init__(self, ostream, options : Options = Options()):
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
        if self.options.layoutFlags & Layout.ADDRESS:
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

                if self.options.layoutFlags & Layout.HEXDUMP:
                    dataAsHex="%0.2X "% int(byte)
                    hexLine += dataAsHex

                if self.options.layoutFlags & Layout.ASCII:
                    byteAsInt = int(byte)
                    if (byteAsInt>31 & byteAsInt <128):
                        asciiLine += chr(byteAsInt)
                    # Otherwise just add '.'    
                    else:
                        asciiLine += "."
            else:
                if self.options.layoutFlags & Layout.HEXDUMP:
                    hexLine += "   "

        print(hexLine, end="", file=self.os)

        if self.options.layoutFlags & Layout.ASCII:
            if self.options.layoutFlags & Layout.HEXDUMP:
                print(" ", end="")
            print(asciiLine, end="", file=self.os)
            
        print()
