import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))

from PromReader import PromReader
from BytesReader import BytesSink, BytesSource, BytesReader
from Ux import ProgressReporter

class MockBytesSource(BytesSource):
    def __init__(self, upperBound):
        self._upperBound = upperBound
        self.Reset()

    def Reset(self):
        self._offset = 0
        self._eof = False

    def Seek(self, offset, whence = os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._offset = offset
        elif whence == os.SEEK_CUR:
            self._offset += offset
        elif whence == os.SEEK_END:
            self._offset = self._upperBound - offset

    def Read(self, size):
        data = bytearray()

        size = min(size, self._upperBound - self._offset)
        offset = self._offset

        for i in range(0, size):
            data.append(offset % 256)
            offset += 1

        self._offset = offset
        self._eof = offset == self._upperBound
       
        return data

    def GetIsEOF(self):
        return self._eof

def main():
    source = MockBytesSource(256)

    with PromReader(source) as reader:
        #reader.Seek(64, os.SEEK_END)

        reader.Read(48)

if __name__ == "__main__":
    main() 
