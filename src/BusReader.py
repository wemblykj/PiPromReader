#!/usr/bin/env python3

import sys
import os

from Core import Disposable
from Reader import BytesSource
import Hardware as hw

class BusReader(BytesSource, Disposable):
    def __init__(self, addressBus : hw.OutputBus, dataBus: hw.InputBus):
        super(BusReader, self).__init__()
        self._addressBus = addressBus
        self._dataBus = dataBus
        self._upperBound = 2 ** self._addressBus.width
        self.Reset()
    
    def _OnDispose(self):
        self.Reset()

    def Reset(self):
        self._addressBus.Reset()
        self._dataBus.Reset()
        self._offset = 0
        
    def Seek(self, offset, whence = os.SEEK_SET):
        if whence == os.SEEK_SET:
                self._offset = offset
        elif whence == os.SEEK_CUR:
                self._offset += offset
        elif whence == os.SEEK_END:
                self._offset = self._upperBound - offset

        self._addressBus.Write(self._offset)
        
    def Read(self, size):
        buffer = bytearray()
       
        span = self._upperBound - self._offset
        count = min(span, size)
        
        for index in range (0,count):
            self._addressBus.Write(self._offset)

            # TODO: propagation delay

            data = self._dataBus.Read()

            buffer.append(data)

            self._offset += 1
            
        return buffer

    def Close(self):
        self.Reset()
    
    def GetIsEOF(self):
        return self._offset >= self._upperBound
