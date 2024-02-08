#!/usr/bin/env python3

import os

from abc import ABC, abstractmethod

from Hardware import InputBus, OutputBus

class Gpio(ABC):
    INPUT = 1
    OUTPUT = 0

    @abstractmethod
    def ConfigureGpio(self, pin, dir):
        pass

    @abstractmethod
    def ReadGpio(self, pin):
        pass

    @abstractmethod
    def WriteGpio(self, pin, state):
        pass

class GpioBusBase(ABC):
    def __init__(self, hal, pins, dir):
        self._hal = hal
        self._busWidth = len(pins)
        self._pins = pins
        self._setDirection(dir)
       
    def GetWidth(self):
        return self._busWidth

    def _setDirection(self, dir):
        hal = self._hal
        for pin in self._pins: 
            hal.ConfigureGpio(pin, dir)
 
class InputGpioBus(InputBus, GpioBusBase):
    def __init__(self, hal, pins):
        super().__init__(hal, pins, Gpio.INPUT)
        self.Reset()

    def GetWidth(self):
        return GpioBusBase.GetWidth(self)

    def Reset(self):
        pass
        
    def Read(self):
        bitValue=1
        data = 0
        for bitCounter in range (0, self.width):
            if (self._readBit(bitCounter)):
                data += bitValue
            bitValue=(bitValue<<1)    
        
        return data
        
    def _readBit(self, bit):
        pin = self._pins[bit]
        return self._hal.ReadGpio(pin)
 
class OutputGpioBus(OutputBus, GpioBusBase):
    def __init__(self, hal, pins):
        super().__init__(hal, pins, Gpio.OUTPUT)
        self.Reset()
        
    def GetWidth(self):
        return GpioBusBase.GetWidth(self)

    def Reset(self):
        self._dataLast = None
        self.Write(0)
        
    def Write(self, data):
        bitMask=1
        for bitCounter in range (0,self._busWidth):
            maskedState = data & bitMask
            desiredState = maskedState >> bitCounter
            stateChanged = self._dataLast == None

            if not stateChanged:
                stateChanged = (self._dataLast & bitMask) != maskedState

            if stateChanged:
                self._writeBit(bitCounter, desiredState)

            bitMask=(bitMask<<1)

        self._dataLast = data
       
    def _writeBit(self, bit, state):
        pin = self._pins[bit]
        return self._hal.WriteGpio(pin, state)

class CounterBasedAddressBus(OutputBus):
    def __init__(self, hal, frequency, resetPin, clockPin):
        self._hal = hal
        self.halfPeriod = 0.5 / frequency
        self._hal.ConfigureGpio(resetPin, Gpio.OUTPUT)
        self._hal.ConfigureGpio(clockPin, Gpio.OUTPUT)
        self._hal.ConfigureGpio(loadPin, Gpio.OUTPUT)
        self.Reset()

    def Reset(self):
        self._hal.WriteGpio(resetPin,1)
        self._hal.WriteGpio(clockPin,0)
        self._hal.WriteGpio(loadPin,1)
        self._hal.WriteGpio(resetPin,0)
        self._pulse()
        self._hal.WriteGpio(resetPin,0)
        self.lastValue = 0
    
    def Write(self, value):
        delta = value - self.lastValue
        if (delta > 1):
            self._seek(delta, os.SEEK_CUR)
        else:
            self._seek(value)
        
    def _pulse(self):
        self._hal.WriteGpio(clockPin,1)
        time.sleep(self.halfPeriod)
        self._hal.WriteGpio(clockPin,0)
        time.sleep(self.halfPeriod)
        
    def _step(self):
        self._pulse()
        self.lastValue += 1
        
    def _seek(self, offset, whence = os.SEEK_SET):
        # TODO: support counter load - for now we do things the long way
   
        if whence == os.SEEK_SET:
            value = offset
        elif whence == os.SEEK_CUR:
            value = self.lastValue + offset
        elif whence == os.SEEK_END:
            raise NotImplementedError

        #match whence: 
        #    case os.SEEK_SET:
        #        value = offset
        #    case os.SEEK_CUR:
        #        value = self.lastValue + offset
        #    case os.SEEK_END:
        #        raise NotImplementedError
        
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
        
