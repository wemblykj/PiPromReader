#!/usr/bin/env python3

import os
import time

from enum import Enum

from abc import ABC, abstractmethod

from Core import Disposable
from Hardware import InputBus, OutputBus

class Direction(Enum):
    INPUT = 1
    OUTPUT = 0

class State(Enum):
    HIGH = 1
    LOW = 0

class Gpio(ABC):

    @abstractmethod
    def ConfigureGpio(self, pin, dir : Direction):
        pass

    @abstractmethod
    def ReadGpio(self, pin):
        pass

    @abstractmethod
    def WriteGpio(self, pin, state : State):
        pass

class GpioBusBase(ABC):
    def __init__(self, hal, pins, dir : Direction):
        self._hal = hal
        self._width = len(pins)
        self._upperbound = 2 ** self._width
        self._pins = pins
        self._setDirection(dir)
       
    def GetWidth(self):
        return self._width

    def GetUpperbound(self):
        return self._upperbound

    def _setDirection(self, dir : Direction):
        hal = self._hal
        for pin in self._pins: 
            hal.ConfigureGpio(pin, dir)
 
class InputGpioBus(InputBus, GpioBusBase):
    def __init__(self, hal, pins):
        super().__init__(hal, pins, Direction.INPUT)
        self.Reset()

    def GetWidth(self):
        return GpioBusBase.GetWidth(self)

    def GetUpperbound(self):
        return GpioBusBase.GetUpperbound(self)

    def Reset(self):
        pass
        
    def Read(self):
        bitValue=1
        data = 0
        for bitCounter in range (0, self.width):
            if self._readBit(bitCounter) == State.HIGH:
                data += bitValue
            bitValue=(bitValue<<1)    
        
        return data
        
    def _readBit(self, bit):
        pin = self._pins[bit]
        return self._hal.ReadGpio(pin)
 
class OutputGpioBus(OutputBus, GpioBusBase, Disposable):
    def __init__(self, hal, pins):
        super().__init__(hal, pins, Direction.OUTPUT)
        self.Reset()
    
    def _OnDispose(self):
        self.Reset()

    def GetWidth(self):
        return GpioBusBase.GetWidth(self)

    def GetUpperbound(self):
        return GpioBusBase.GetUpperbound(self)

    def Reset(self):
        self._dataLast = None
        self.Write(0)
        
    def Write(self, data):
        bitMask=1
        for bitCounter in range (0,self._width):
            maskedState = data & bitMask
            desiredState = maskedState >> bitCounter
            stateChanged = self._dataLast == None

            if not stateChanged:
                stateChanged = (self._dataLast & bitMask) != maskedState

            if stateChanged:
                self._writeBit(bitCounter, State.HIGH if desiredState else State.LOW)

            bitMask=(bitMask<<1)

        self._dataLast = data
       
    def _writeBit(self, bit, state):
        pin = self._pins[bit]
        return self._hal.WriteGpio(pin, state)

class CounterBasedAddressBus(OutputBus, Disposable):
    def __init__(self, hal, width, frequency, resetPin, clockPin, loadPin = None):
        self._hal = hal
        if frequency > 0:
            self._halfPeriod = 0.5 / frequency
        else:
            self._halfPeriod = 0
        self._width = width
        self._upperbound = 2 ** width
        self._end = 1 << width
        self._resetPin = resetPin
        self._clockPin = clockPin
        self._loadPin = loadPin
        self._hal.ConfigureGpio(resetPin, Direction.OUTPUT)
        self._hal.ConfigureGpio(clockPin, Direction.OUTPUT)
        if loadPin != None:
            self._hal.ConfigureGpio(loadPin, Direction.OUTPUT)
        self.Reset()

    def _OnDispose(self):
        self.Reset()

    def GetWidth(self):
        return self._width

    def GetUpperbound(self):
        return self._upperbound

    def Reset(self):
        self._pulseReset()
        self._lastValue = 0
    
    def Write(self, value):
        delta = value - self._lastValue
        if delta > 1:
            self._seek(delta, os.SEEK_CUR)
        else:
            self._seek(value)
        
    def _pulseReset(self):
        self._hal.WriteGpio(self._resetPin,State.LOW)
        self._pulseClock()
        self._hal.WriteGpio(self._resetPin,State.HIGH)

    def _pulseClock(self):
        self._hal.WriteGpio(self._clockPin,State.HIGH)
        if self._halfPeriod > 0:
            time.sleep(self._halfPeriod)
        self._hal.WriteGpio(self._clockPin,State.LOW)
        if self._halfPeriod > 0:
            time.sleep(self._halfPeriod)
        
    def _step(self):
        self._pulseClock()
        self._lastValue += 1
        
    def _seek(self, offset, whence = os.SEEK_SET):
        # TODO: support counter load - for now we do things the long way
   
        if whence == os.SEEK_SET:
            value = offset
        elif whence == os.SEEK_CUR:
            value = self._lastValue + offset
        elif whence == os.SEEK_END:
            raise NotImplementedError

        #match whence: 
        #    case os.SEEK_SET:
        #        value = offset
        #    case os.SEEK_CUR:
        #        value = self.lastValue + offset
        #    case os.SEEK_END:
        #        raise NotImplementedError
        
        if value > self._lastValue:
            steps = value - self._lastValue
        elif value < self._lastValue:
            # Reset the counter
            self._pulseReset()
            # step from zero
            steps = value
        else:
            steps = 0
            
        #print("current: {}".format(self._lastValue))
        #print("value: {}".format(value))
        #print("steps: {}".format(steps))

        # Pulse until the value is reached
        for s in range(0, steps):
            self._pulseClock()

        self._lastValue = value
        
