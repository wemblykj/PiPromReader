import sys
import os

sys.path.insert(0, os.path.abspath('../src'))
 
from HexDumper import HexDumper, HexDumperOptions

def TestDumper(options : HexDumperOptions = HexDumperOptions()):
    with HexDumper(sys.stdout, options) as hexDumper:

        for i in range(0, 250):
            hexDumper.Write([i])

def main():
    TestDumper()
    TestDumper(HexDumperOptions(columnsPerLine=32, showAscii=False))

if __name__ == "__main__":
    main() 
