from abc import ABC, abstractmethod

class Bus(ABC):
    @abstractmethod
    def Reset(self):
        pass

    @abstractmethod
    def GetWidth(self):
        pass

    @property
    def width(self):
        return self.GetWidth()

class InputBus(Bus):
    @abstractmethod
    def Read(self):
        pass
        
class OutputBus(Bus):
    @abstractmethod
    def Write(self, data):
        pass
       
class BidirectionalBus(InputBus, OutputBus):
    pass
        
