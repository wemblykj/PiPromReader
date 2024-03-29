#!/usr/bin/env python3

import os

from abc import ABC, abstractmethod

from Core import Disposable
from Ux import ProgressReporter

class BytesSink(ABC):
    @abstractmethod    
    def Reset(self):
        pass
        
    @abstractmethod    
    def Write(self, data):
        pass

class MyBytesSink(BytesSink):
    def Reset(self):
        print("hello")

    def Write(self, value):
        print("there!", value)

class BytesSource(ABC):
    @abstractmethod    
    def Reset(self):
        pass
        
    @abstractmethod    
    def Seek(self, offset, whence = os.SEEK_SET):
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

class BytesReader(Disposable):
    def __init__(self, source : BytesSource, blockSize):
        super().__init__()
        self._source = source
        self._blockSize = blockSize
        self._sinks = []
        self._reporter = None
        self.Reset()

    def _OnDispose(self):
        self.Reset()

    def AddSink(self, sink : BytesSink):
        self._sinks.append(sink)

    def AddProgressReporter(self, reporter : ProgressReporter):
        self._reporter = reporter

    def Reset(self):
        self._source.Reset()
        for sink in self._sinks:
            sink.Reset()
        
    def Seek(self, offset, whence = os.SEEK_SET):
        self._source.Seek(offset, whence)
        
    def Read(self, size):
        progress = 0
        progressIncrement = (100 * size) / self._blockSize

        data = []
        while size > 0:
            count = min(size, self._blockSize)
            block = self._source.Read(count)
            data += block

            for sink in self._sinks:
                sink.Write(block)
            
            if self._reporter:
                self._reporter.Progress(progress)
                progress += progressIncrement

            if self._source.eof:
                break

            size -= count

        return data

    def GetIsEOF(self):
        return self._source.eof

    @property
    def eof(self):
        return self.GetIsEOF()
   
