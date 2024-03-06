import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from Core import Disposable
from BytesReader import BytesSink, BytesSource, BytesReader
from Ux import ProgressReporter
from HexDumper import HexDumper
from HashGenerator import HashingCollective

class PromReader(Disposable):
    def __init__(self, source : BytesSource):
        super().__init__()
        self._reader = BytesReader(source, 64)

        self._chunkSize = 1024
        
        self._hashGenerator = HashingCollective()
        self._reader.AddSink(HexDumper(sys.stdout))
        self._reader.AddSink(self._hashGenerator)

    def _OnDispose(self):
        self._reader.Dispose()

    def Reset(self):
        self._reader.Reset()

    def Seek(self, offset, whence = os.SEEK_SET):
        self._reader.Seek(offset * self._chunkSize, whence)
        
    def Read(self, chunks):

        while not self._reader.eof:
            self._reader.Read(self._chunkSize)
            if self._reader.eof:
                break

        print(self._hashGenerator)

    def GetIsEOF(self):
        return self._reader.eof

    @property
    def eof(self):
        return self.GetIsEOF()
