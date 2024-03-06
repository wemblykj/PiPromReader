import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))
 
from BytesReader import BytesSink, BytesSource, BytesReader
from Ux import ProgressReporter

class MockBytesSink(BytesSink):
    def __init__(self):
        self.Reset()

    def Reset(self):
        self._size = 0

    def Write(self, data):
        self._size += len(data)

    def GetSize(self):
        return self._size

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

class MockProgressReporter(ProgressReporter):
    def __init__(self, width = 16):
        self._width = int(100/width)
        self._lastPercent = 0

    def Progress(self, percent : int):
        for i in range(0, int((int(percent) - self._lastPercent)/self._width)):
            print("#", end="")
        self._lastPercent = int(percent)

def main():
    sink = MockBytesSink()
    source = MockBytesSource(256)
    reporter = MockProgressReporter()

    with BytesReader(source, 16) as reader:
        reader.AddSink(sink)
        reader.AddProgressReporter(reporter)

        reader.Seek(64, os.SEEK_END)

        data = reader.Read(48)
        print("data size" , len(data))
        print("reader.eof", reader.eof)

        data = reader.Read(32)
        print("data size" , len(data))
        print("reader.eof", reader.eof)
        print("source.eof", source.eof)
        print("sink.size", sink.GetSize())

    print("source.eof", source.eof)
    print("sink.size", sink.GetSize())

if __name__ == "__main__":
    main() 
