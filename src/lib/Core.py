from abc import ABC, abstractmethod

class Disposable(ABC):
    def __init__(self):
        self._isDisposed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Dispose()

    def Dispose(self):
        if self._isDisposed == False:
            self._isDisposed = True
            self._OnDispose()

    @abstractmethod
    def _OnDispose(self):
        pass
