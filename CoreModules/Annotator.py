from DataModules.DatabaseTables import Screenshot

class Annotator:
    def __init__(self, screenshot: Screenshot):
        self.__screenshot: Screenshot = screenshot
        self.__tool: str
        self.__size: int
        self.__color: str
        self.__zoom: float
        self.__savedposition: str

    def gettool(self) -> str:
        pass

    def settool(self, tool: str):
        pass

    def getsize(self) -> int:
        pass

    def setsize(self, size: int):
        pass

    def getcolor(self) -> str:
        pass

    def setcolor(self, color: str):
        pass

    def getscreenshot(self) -> Screenshot:
        pass

    def getzoom(self) -> float:
        pass

    def getsavedposition(self) -> str:
        pass

    def setsavedposition(self, position: str):
        pass

    def zoomin(self):
        pass

    def zoomout(self):
        pass
