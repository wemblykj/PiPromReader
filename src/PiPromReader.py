#!/usr/bin/env python3

# PROM reader for 40-pin Raspberry Pi
# Must use level downshifter between
# PROM data pins and Pi inputs.

import sys
import os
import binascii
import hashlib
import time
import RPi.GPIO as GPIO

#
# Constants
#

# Address output GPIO pins defined in lowbit to highbit order (A0-A14)
# we will have to support addition address lines via manual means such
# as a DIP switch prompt
AddressPin = (10,9,11,25,8,7,5,6,12,13,19,16,20,21,26)

# Data input GPIO pins defined in lowbit to highbit order (D0-D7)
DataPin = (14,15,18,17,27,22,23,24)

#
# Default settings
#

# Start reading bytes from this initial offset
startingOffset = 0

# Limit the number of bytes read by specifying a logical bus width
busWidthOverride = None

# Limit the number of bytes read by specifying an upper address
addressTopOverride = None

# Write the read PROM image to this file
binaryImageFile = None

# Save metadata, such as CRC values to this file
metadataFilename = None

# The PROM will be read in blocks; this is the default size
blockSize = 1024

#
# Command-line options settings
#

# TODO: Just some example stubs atm.

if (cmdAddressTopOverride):
	addressTopOverride = cmdAddressTopOverride

if (cmdBusWidthOverride):
	busWidthOverride = cmdBusWidthOverride
else if (cmdAddressTopOverride):
	addressTopOverride = cmdAddressTopOverride	

if (cmdBinaryImageFile):
	binaryImageFile = cmdBinaryImageFile
	
if (cmdMetadataFilename):
	metadataFilename = cmdMetadataFilename

if (cmdStartingBlock):
	blockSize = cmdStartingBlock

if (cmdStartingBlock):
	startingOffset = startingBlock * blockSize 
else if (cmdStartingOffset):
	startingOffset = cmdStartingOffset
	
#
# Calculated settings
#

# The bus width of our PROM
logicalAddressBusWidth = addressBus.busWidth
if (busWidthOverride):
	logicalAddressBusWidth = max(logicalAddressBusWidth, busWidthOverride)
	
# The size of our PROM determined from its bus width
logicalAddressTop = 1 << logicalAddressBusWidth 
if (addressTopOverride):
	logicalAddressTop = min(logicalAddressTop, addressTopOverride)
	
#
# Realise our settings
#

addressBus = OutputBus(AddressPin)
dataBus = InputBus(DataPin)

# The bus width of our hardware reader
physicalAddressBusWidth = addressBus.busWidth
if (busWidthOverride):
	physicalAddressBusWidth = min(physicalAddressBusWidth, busWidthOverride)
	
# The number of bytes our hardware can read in a single pass, determined from our physical bus width
physicalAddressTop = 1 << physicalAddressBusWidth
if (addressTopOverride):
	physicalAddressTop = min(physicalAddressTop, addressTopOverride)

addressTop = max(physicalAddressTop, logicalAddressTop)
	
binDumper = None
if binaryImageFile:
    binDumper = BinFileDumper(binaryImageFile)
    
metadataFile = None
if metadataFilename:       
	metadataFile=open(metadataFilename)
	
#
# Display our realised settings
#

print("Lower bound: 0x{:04x}".format(startingOffset))
print("Upper bound: 0x{:04x}".format(addressTop))
print("Byte to read: {}".format(addressTop - startingOffset))

if (binaryImageFile):
	print("Image file: {}".format(binaryImageFile))
	
if (metadataFilename):
	print("Metadata file: {}".format(metadataFilename))


class BytesSink:
    def Reset(self):
        pass
        
    def Write(self, data):
        pass

    def Close(self):
        pass

class Crc32Hasher(BytesSink):
    def __init__(self):
        self.Reset()
    
    def __str__(self):
        return f'crc32: {hex(self.crc32)}'
        
    def Reset(self):
        self.crc32 = 0
            
    def Write(self, data):
        self.crc32 = binascii.crc32(data, self.crc32)
            
class HashlibHasher:
    def __init__(self, name):
        self.name = name
        self.Reset()
    
    def __str__(self):
        return f'{self.name}: {self.hasher.hexdigest()}'  
        
    def Reset(self):
        self.hasher = hashlib.new(self.name)
            
    def Write(self, data):
        self.hasher.update(data)
            
class HashingCollective(BytesSink):
    def __init__(self):
        self.hashers = []
        self.Reset()
    
    def __str__(self):
        s = ''
        for hasher in self.hashers:
            s += f'{hasher}\n'
        
        return s
        
    def Reset(self):
        self.hashers = [
            Crc32Hasher(),
            HashlibHasher('md5'),
            HashlibHasher('sha1'),
            HashlibHasher('sha256')
            ]
            
    def Write(self, data):
        for hasher in self.hashers:
            hasher.Write(data)

class Bus:
    def Reset(self):
        pass
        
class GpioBus(Bus):
     def __init__(self, pins, dir):
        self.busWidth = len(pins)
        self.pins = pins
        self._SetDirection(dir)
        
     def _SetDirection(self, dir):
        for pin in self.pins: 
            GPIO.setup(pin, dir)
 
class GpioInputBus(GpioBus):
    def __init__(self, pins):
        super().__init__(pins, GPIO.IN)
        self.Reset()

    def SetDirection(self): 
        super()._SetDirection(GPIO.IN)
        
    def Reset(self):
        pass
        
    def Read(self):
        data=0
        BitValue=1
        for BitCounter in range (0,self.busWidth):
            if (GPIO.input(self.pins[BitCounter])==1):
                data += BitValue
            BitValue=(BitValue<<1)    
        
        return data
        
class GpioOutputBus(GpioBus):
    def __init__(self, pins):
        super().__init__(pins, GPIO.OUT)
        self.dataLast = 0xffff
        self.Reset()

    def SetDirection(self): 
        super()._SetDirection(GPIO.OUT)
        
    def Reset(self):
        self.Write(0)
        self.dataLast = 0
        
    def Write(self, data):
        BitMask=1
        for BitCounter in range (0,self.busWidth):
            pin = self.pins[BitCounter]
            shouldSet = (data & BitMask) == BitMask
            wasSet = (self.dataLast & BitMask) == BitMask
            if (shouldSet != wasSet):
                #print("pin ", pin, " = ", shouldSet)
                GPIO.output(pin,1 if shouldSet else 0)
            BitMask=(BitMask<<1)
        self.dataLast = data
        #print("")
       
class GpioBidirectionalBus(GpioBus):
    def __init__(self, pins, initialDir=GPIO.OUT):
        self.dir = initialDir
        super().__init__(pins, initialDir)
        self.inputBus = InputBus(pins)
        self.outputBus = OutputBus(pins)
        self.Reset()

    def Reset(self):
        self.inputBus.Reset()
        self.outputBus.Reset()
    
    def SetDirection(self, dir):
        if (dir != self.dir):
            if (dir == GPIO.OUT):
                self.outputBus.SetDirection()
            else:
                self.inputBus.SetDirection()
                
        self.dir = dir
        
    def Read(size):
        self.SetDirection(GPIO.IN)
        return self.inputBus.Read(size)
        
    def Write(data):
        self.Initialise(GPIO.OUT)
        self.outputBus.Write()

class CounterBasedAddressBus(Bus):
    def __init__(self, frequency, resetPin, clockPin):
        self.halfPeriod = 0.5 / frequency
        GPIO.setup(resetPin, GPIO.OUT)
        GPIO.setup(clockPin, GPIO.OUT)
        GPIO.setup(loadPin, GPIO.OUT)
        self.Reset()

    def Reset(self):
        GPIO.output(resetPin,1)
        GPIO.output(clockPin,0)
        GPIO.output(loadPin,1)
        GPIO.output(resetPin,0)
        self._pulse()
        GPIO.output(resetPin,0)
        self.lastValue = 0
    
    def Write(self, value):
        delta = value - self.lastValue
        if (delta > 1):
            self._seek(delta, os.SEEK_CUR)
        else:
            self._seek(value)
        
    def _pulse(self):
        GPIO.output(clockPin,1)
        time.sleep(self.halfPeriod)
        GPIO.output(clockPin,0)
        time.sleep(self.halfPeriod)
        
    def _step(self):
        self._pulse()
        self.lastValue += 1
        
    def _seek(self, offset, whence = os.SEEK_SET):
        # TODO: support counter load - for now we do things the long way
   
        match whence: 
            case os.SEEK_SET:
                value = offset
            case os.SEEK_CUR:
                value = self.lastValue + offset
            case os.SEEK_END:
                raise NotImplementedError
        
        if (value > self.lastValue):
            steps = self.lastValue - value

        else:
            steps = value
            # Reset the counter
            self.Reset()
            
        # Pulse until the value is reached
        for s in range(0, value):
            self._pulse(self)

        self.lastValue = value
        
class BytesSource():
    def Reset(self):
        pass
        
    def Seek(self, offset=0):
        pass
        
    def Read(self, size):
        pass

class BusReader(BytesSource):
    def __init__(self, addressBus, dataBus, propagationDelay=0):
        self.addressBus = addressBus
        self.dataBus = dataBus
        self.propagationDelay = propagationDelay
        self.Reset()
        
    def Reset(self):
        self.offset = 0
        
    def Seek(self, offset):
        self.offset = offset
        
    def Read(self, size):
        buffer = bytearray()
       
        dataLast = 0
        end = 2**self.addressBus.busWidth
        last = end - 1
        count = min(size, end)
        debug = False
        
        for index in range (0,count):
            
            # disable chip select
            #GPIO.output(4,1) # low = inactive
            #time.sleep(0.0005) 
            
            self.addressBus.Write(self.offset)

            #time.sleep(0.005) 
            # enable chip select
            #GPIO.output(4,0) # low = inactive
            #time.sleep(0.0005) 
            
            self.offset += 1
            
            #if (self.propagationDelay>0):
            #    propagationDelayCounter = self.propagationDelay # * 100000
            #    while(propagationDelayCounter > 0):
            #        #print(".", end="")
            #        propagationDelayCounter -= 1
            #    #print(""
            

            data = self.dataBus.Read()
           
            #for i in range(0, 5):
            #    data2 = self.dataBus.Read()
            #    if (data2 != data):
            #        print("{:08x}".format(address), end=" ")
            #        print("[{:015b}]".format(address), end="  ")
            #        print("0x{:02x}".format(data), end=" ")
            #        print("[{:08b}]".format(data), end=" != ")
            #        print("0x{:02x}".format(data2), end=" ")
            #        print("[{:08b}]".format(data2))
            #        #debug = True
            #        break

            while (debug):
                inp = input()
                if (len(inp) == 0):
                    continue
                if (inp[0] == 'r'):
                    data = self.dataBus.Read()
                    print("{:08x}".format(address), end=" ")
                    print("[{:015b}]".format(address), end="  ")
                    print("0x{:02x}".format(data), end=" ")
                    print("[{:08b}]".format(data))

                if (inp[0] == 'n'):
                    break

                if (inp[0] == 'q'):
                    debug = False
            


            buffer.append(data)
            
        return buffer
        
    def Write(self, data):
        end = 2**self.addressBus.busWidth
        count = min(len(data), end)
        
        for index in range (0,count):
            self.addressBus.Write(self.offset)
            self.offset += 1
            
            if (self.propagationDelay):
                propagationDelayCounter = self.propagationDelay
                while(propagationDelayCounter > 0):
                    propagationDelayCounter -= 1
                
            self.dataBus.Write(data[index])
    
    def SetPropagationDelay(self, propagationDelay):
        self.propagationDelay = propagationDelay
        
class Calibrator():
    def __init__(self, reader, propagationDelayMin = 0, propagationDelayMax = 500):
        self.reader = reader
        self.propagationDelayMin = propagationDelayMin
        self.propagationDelayMax = propagationDelayMax

    def Calibrate(self, offset=0, blockSize=256, iterations=5, rounds=50):
        propagationDelayMin = self.propagationDelayMin
        propagationDelayMax = self.propagationDelayMax
        canditatePropagationDelay = propagationDelayMax
    
        for rnd in range(0, rounds):

            print("round:", rnd)
            print("propagationDelay (max):", propagationDelayMax)
            self.reader.SetPropagationDelay(propagationDelayMax)

            errorCount = 0
            lastHash = None
            for index in range(0, iterations):
                self.reader.Seek(offset)
                hasher = hashlib.new("sha256")
                data = self.reader.Read(blockSize)

                hasher.update(data)
                thisHash = hasher.hexdigest()
                #print("last hash:" , lastHash)

                if lastHash == None or thisHash != lastHash:
                    print("hash:" , thisHash)

                if lastHash != None and thisHash != lastHash:
                    print("unstable at max")
                    errorCount += 1
                    break
                
                lastHash = thisHash

            if errorCount > 0:
                temp = propagationDelayMax
                propagationDelayMax = propagationDelayMax + int((propagationDelayMax-propagationDelayMin)*1.15)
                propagationDelayMin = temp
                continue

            canditatePropagationDelay = propagationDelayMax
            
            print("propagationDelay (min):", propagationDelayMin)

            errorCount = 0
            lastHash = None
            self.reader.SetPropagationDelay(propagationDelayMin)
            for index in range(0, iterations):
                self.reader.Seek(offset)
                hasher = hashlib.new("sha256")
                data = self.reader.Read(blockSize)

                hasher.update(data)
                thisHash = hasher.hexdigest()
                #print("last hash:" , lastHash)
                if lastHash == None or thisHash != lastHash:
                    print("hash:" , thisHash)

                if lastHash != None and thisHash != lastHash:
                    print("unstable at min")
                    errorCount += 1
                    break
                
                lastHash = thisHash
                
            if errorCount > 0:
                propagationDelayMax = propagationDelayMin + int((propagationDelayMax-propagationDelayMin)*0.71)
                #propagationDelayMin = int(propagationDelayMin + (propagationDelayMax - propagationDelayMin) / 7)
            else:
                canditatePropagationDelay = propagationDelayMin

                if propagationDelayMax == propagationDelayMin:
                   break
                propagationDelayMax = propagationDelayMin
                #break
            
        return canditatePropagationDelay
  
class BinFileDumper(BytesSink):
    def __init__(self, fileName):
        self.file = open(fileName,"wb")

    def Seek(self, offset=0):
        self.file.seek(offset)
        
    def Write(self, data):
        self.file.write(data)

    def Close(self):
        self.file.close()

class HexDumper(BytesSink):
    def __init__(self, ostream, columnsPerLine = 16):
        self.columnsPerLine = columnsPerLine
        self.os = ostream
        self.offset = 0

    def Seek(self, offset=0):
        self.offset = offset
    
    def Write(self, data):
        count = len(data)
        index = 0
        while index<count:

            address = self.offset + index

            # Convert Address to ASCII hexadecimal
            offsetAsHex="%0.8X"% address

            # Print line start address
            print(offsetAsHex,"",end=" ", file=self.os)

            #Clear the line buffers
            hexLine=""
            asciiLine="" 

            # Output x columns per line
            
            for column in range (0,self.columnsPerLine):

                if (index<count):
                    byte = data[index]
                    dataAsHex="%0.2X "% int(byte)
                    hexLine += dataAsHex

                    byteAsInt = int(byte)
                    if (byteAsInt>31 & byteAsInt <128):
                        asciiLine += chr(byteAsInt)
                    # Otherwise just add '.'    
                    else:
                        asciiLine += "."
                else:
                    hexLine += "   "
                    asciiLine += " "
                    
                index += 1

            print(hexLine,end=" ", file=self.os)
            print(asciiLine, file=self.os)

        self.offset += count

# Use Broadcom GPIO pin numbering scheme
GPIO.setmode(GPIO.BCM)

# CS pins
GPIO.setup (3,GPIO.OUT) # active low CS pin
GPIO.setup (4,GPIO.OUT) # active high CS pin

# Set the chip in standby mode:
GPIO.output(3,1) # high = inactive
GPIO.output(4,0) # low = inactive

busReader = BusReader(addressBus, dataBus)

hexDumper = HexDumper(sys.stdout)
hashingCollective = HashingCollective()

# does not appear to make a difference, I don't think reading frequency is an issue
#calibrator = Calibrator(busReader)
#propagationDelay = 1 # calibrator.Calibrate(blockSize=BlockSize)
#busReader.SetPropagationDelay(propagationDelay)

busReader.Reset()

# Enable PROM data outputs
GPIO.output(3,0) # low = active
GPIO.output(4,1) # high = active

logicalAddress = startingOffset
physicalAddress = startingOffset

while logicalAddress < logicalAddressTop:

	# TODO: Prompt for manual intervention
	if (logicalAddressBusWidth > physicalAddressBusWidth):
		msbs >> physicalAddressBusWidth
		width = logicalAddressBusWidth - physicalAddressBusWidth
		print("Please set the {0} MSB bits of the address bus to [{1:{0}b}]", width, msbs)
	
    busReader.Seek(physicalAddress)
    
	# Iterate over all addresses provided by the physical bus
	while physicalAddress < physicalAddressTop:
	
	    data = busReader.Read(blockSize)
	
	    hexDumper.Write(data)
	    hashingCollective.Write(data)
	    
	    if binDumper:
	        binDumper.Write(data)
	        
	    physicalAddress += blockSize
	    
	logicalAddress += physicalAddressTop 
    
    physicalAddress = 0

print("Done!")

# Disable PROM data outputs
GPIO.output(3,1) # high = inactive
GPIO.output(4,0) # low = inactive

GPIO.cleanup()   
    
if hashingCollective:
     print("")
     print(hashingCollective)

# If file write was enabled, close the file
if binDumper:
	binDumper.Close()
 
if metadataFile==1:
    metadataFile.write(f'{binaryFilename}\n')
    metadataFile.write(str(hashingCollective))
    metadataFile.write("\n")
    metadataFile.close()
    