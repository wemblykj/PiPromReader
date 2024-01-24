import sys
import os

sys.path.insert(0, os.path.abspath('../src'))
 
from Hardware import InputBus, OutputBus
from Reader import BusReader

class MockOutputBus(OutputBus):
    def Reset(self):
        self.data = 0

    def Write(self, data):
        self.data = data

    def GetWidth(self):
        return 4

    def GetData(self):
        return self.data

class MockInputBus(InputBus):
    def __init__(self, outputBus : MockOutputBus):
        self.outputBus = outputBus

    def Reset(self):
        pass

    def Read(self):
        return self.outputBus.GetData()

    def GetWidth(self):
        return 8

def main():
    outBus = MockOutputBus()
    inBus = MockInputBus(outBus)
    reader = BusReader(outBus, inBus)

    while(not reader.eof):
        data = reader.Read(1)
        print('0x{:04x}  0x{:02x}'.format(outBus.GetData(), data[0]))

    data = reader.Read(1)
    print(len(data))

    reader.Reset()

    print("read [oversized] block")
    data = reader.Read(100)
    for i in range(0, len(data)):
        print('0x{:04x}  0x{:02x}'.format(i, data[i]))

    print("seek from end")
    reader.Seek(4, os.SEEK_END)
    while(not reader.eof):
        data = reader.Read(1)
        print('0x{:04x}  0x{:02x}'.format(outBus.GetData(), data[0]))

    print("seek from current")
    reader.Seek(-6, os.SEEK_CUR)
    while(not reader.eof):
        data = reader.Read(1)
        print('0x{:04x}  0x{:02x}'.format(outBus.GetData(), data[0]))

if __name__ == "__main__":
    main() 
