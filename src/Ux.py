from abc import ABC, abstractmethod

class ProgressReporter(ABC):
    @abstractmethod
    def Progress(self, percent : int):
        pass

    def Status(self, status):
        pass

class NotificationBroker(ABC):
    @abstractmethod
    def Notify(self):
        pass
