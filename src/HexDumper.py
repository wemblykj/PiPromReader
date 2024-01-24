#!/usr/bin/env python3

import sys
import os

from Reader import BytesSink

class HexDumper(BytesSink):
    def __init__(self, ostream, columnsPerLine = 16):
        self.columnsPerLine = columnsPerLine
        self.os = ostream
        self.offset = 0

    def Seek(self, offset=0):
        self.offset = offset
    
    def Write(self, data):
        count = len(data)
        index = 0
        while index<count:

            address = self.offset + index

            # Convert Address to ASCII hexadecimal
            offsetAsHex="%0.8X"% address

            # Print line start address
            print(offsetAsHex,"",end=" ", file=self.os)

            #Clear the line buffers
            hexLine=""
            asciiLine="" 

            # Output x columns per line
            
            for column in range (0,self.columnsPerLine):

                if (index<count):
                    byte = data[index]
                    dataAsHex="%0.2X "% int(byte)
                    hexLine += dataAsHex

                    byteAsInt = int(byte)
                    if (byteAsInt>31 & byteAsInt <128):
                        asciiLine += chr(byteAsInt)
                    # Otherwise just add '.'    
                    else:
                        asciiLine += "."
                else:
                    hexLine += "   "
                    asciiLine += " "
                    
                index += 1

            print(hexLine,end=" ", file=self.os)
            print(asciiLine, file=self.os)

        self.offset += count
