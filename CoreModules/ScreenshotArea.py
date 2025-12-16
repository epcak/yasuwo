from Hotkey import Hotkey

class ScreenshotArea:
    def __init__(self, name: str, startpoint: str, size: str, hotkey: Hotkey = None):
        self.__name = name
        self.__startpoint = startpoint
        self.__size = size
        self.__hotkey = hotkey

    def gethotkey(self) -> str:
        pass

    def sethotkey(self, sequence: str):
        pass

    def getsize(self) -> str:
        pass

    def setsize(self, size: str):
        pass

    def getstart(self) -> str:
        pass

    def setstart(self, start: str):
        pass

    def getname(self) -> str:
        pass

    def setname(self, name: str):
        pass

    def activatehotkey(self):
        pass

    def deactivatehotkey(self):
        pass

    def __generatefunction(self):
        pass
