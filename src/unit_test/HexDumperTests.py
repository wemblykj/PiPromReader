import sys
import os

sys.path.insert(0, os.path.abspath('../lib'))
 
from HexDumper import HexDumper, Options, Layout

def TestDumper(options : Options = Options()):
    with HexDumper(sys.stdout, options) as hexDumper:

        for i in range(0, 250):
            hexDumper.Write([i])

def main():
    TestDumper()
    TestDumper(Options(columnsPerLine=32, layoutFlags=Layout.NOASCII))
    TestDumper(Options(columnsPerLine=32, layoutFlags=Layout.ASCII))

if __name__ == "__main__":
    main() 
