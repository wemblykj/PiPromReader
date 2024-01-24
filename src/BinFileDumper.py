#!/usr/bin/env python3

import sys
import os

from Reader import BytesSink

class BinFileDumper(BytesSink):
    def __init__(self, fileName):
        self.file = open(fileName,"wb")

    def Seek(self, offset=0):
        self.file.seek(offset)
        
    def Write(self, data):
        self.file.write(data)

    def Close(self):
        self.file.close()

