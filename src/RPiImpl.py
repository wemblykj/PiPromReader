#!/usr/bin/env python3

# PROM reader for 40-pin Raspberry Pi
# Must use level downshifter between
# PROM data pins and Pi inputs.

import sys
import os

import Hardware

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
 
class GpioInputBus(GpioBus, InputBus):
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
        
class GpioOutputBus(GpioBus, OutputBus):
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
        
