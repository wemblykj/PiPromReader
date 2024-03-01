import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))
 
from Reader import BytesSink, BytesSource, Reader

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
        data = []

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
    sink = MockBytesSink()

    source = MockBytesSource(256)

    with Reader(source, 16) as reader:
        reader.AddSink(sink)

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
