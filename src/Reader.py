#!/usr/bin/env python3

import sys
import os
import binascii
import hashlib
import time

from abc import ABC, abstractmethod

import Hardware as hw

class BytesSink(ABC):
    def Reset(self):
        pass
        
    @abstractmethod    
    def Write(self, data):
        pass

    @abstractmethod    
    def Close(self):
        pass

class BytesSource(ABC):
    @abstractmethod    
    def Reset(self):
        pass
        
    @abstractmethod    
    def Seek(self, offset=0):
        pass
        
    @abstractmethod    
    def Read(self, size):
        pass

    @abstractmethod    
    def Close(self):
        pass

    @abstractmethod    
    def GetIsEOF(self):
        pass

    @property
    def eof(self):
        return self.GetIsEOF()

class BusReader(BytesSource):
    def __init__(self, addressBus : hw.OutputBus, dataBus: hw.InputBus):
        self._addressBus = addressBus
        self._dataBus = dataBus
        self._upperBound = 2 ** self._addressBus.width
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
