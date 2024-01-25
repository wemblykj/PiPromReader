#!/usr/bin/env python3

from abc import ABC, abstractmethod

class BytesSink(ABC):
    @abstractmethod    
    def Reset(self):
        pass
        
    @abstractmethod    
    def Write(self, data):
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
    def GetIsEOF(self):
        pass

    @property
    def eof(self):
        return self.GetIsEOF()
