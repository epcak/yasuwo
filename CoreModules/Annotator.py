from PySide6.QtGui import QPixmap

from DataModules.DatabaseTables import Screenshot, AnnotationType

class Annotator:
    def __init__(self, screenshot: Screenshot):
        self.__screenshot: Screenshot = screenshot
        self.__tool: AnnotationType = AnnotationType.LINE
        self.__size: int = 8
        self.__color: str = "#000000"
        self.__zoom: float = 1.0
        self.__fill: bool = False
        self.__savedposition: tuple[int, int] | None = None

    def getfill(self) -> bool:
        return self.__fill

    def setfill(self, fill: bool):
        self.__fill = fill

    def getannotatedimage(self) -> QPixmap:
        image = self.__screenshot.getannotatedimage().toqpixmap()
        size = image.size()
        size.setWidth(size.width() * self.__zoom)
        size.setHeight(size.height() * self.__zoom)
        return image.scaled(size)

    def gettool(self) -> AnnotationType:
        return self.__tool

    def settool(self, tool: AnnotationType):
        self.__tool = tool
        self.__savedposition = None

    def getsize(self) -> int:
        return self.__size

    def setsize(self, size: int):
        self.__size = size

    def getcolor(self) -> str:
        return self.__color

    def setcolor(self, color: str):
        self.__color = color

    def getscreenshot(self) -> Screenshot:
        return self.__screenshot

    def getzoom(self) -> float:
        return self.__zoom

    def getsavedposition(self) -> tuple[int, int] | None:
        return self.__savedposition

    def setsavedposition(self, pos: tuple[int, int] | None):
        self.__savedposition = pos

    def addposition(self, pos: tuple[int, int], text="") -> bool:
        if self.__tool == AnnotationType.TEXT:
            params = {"start": pos, "color": self.__color, "size": self.__size, "text": text}
            self.__screenshot.addannotation(AnnotationType.TEXT, params)
            return True
        elif self.__savedposition is None:
            self.__savedposition = pos
            return False
        else:
            start = []
            end = []
            if self.__tool == AnnotationType.LINE:
                start = self.__savedposition
                end = pos
            else:
                if self.__savedposition[0] > pos[0]:
                    end.append(self.__savedposition[0])
                    start.append(pos[0])
                else:
                    start.append(self.__savedposition[0])
                    end.append(pos[0])
                if self.__savedposition[1] > pos[1]:
                    end.append(self.__savedposition[1])
                    start.append(pos[1])
                else:
                    start.append(self.__savedposition[1])
                    end.append(pos[1])
            params = {"start": start, "end": end, "color": self.__color, "size": self.__size, "fill": self.__fill}
            self.__screenshot.addannotation(self.__tool, params)
            self.__savedposition = None
            return True

    def zoomin(self):
        if self.__zoom >= 2.0: return
        self.__zoom += 0.25

    def zoomout(self):
        if self.__zoom <= 0.25: return
        self.__zoom -= 0.25

    def __colorstringtotuple(self, color: str) -> tuple[int, int, int]:
        color = color.replace("#", "")
        colarr = [0, 0, 0]
        if len(color) == 3:
            colarr[0] = int(color[0])
            colarr[1] = int(color[1])
            colarr[2] = int(color[2])
        elif len(color) == 6:
            colarr[0] = int(color[0:2])
            colarr[1] = int(color[2:4])
            colarr[2] = int(color[4:6])
        return tuple(colarr)
