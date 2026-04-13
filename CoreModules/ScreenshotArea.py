from typing import Callable
from CoreModules.Hotkey import Hotkey
from CoreModules.Screenshoter import Screenshoter


class ScreenshotArea:
    def __init__(self, name: str, boundingbox: tuple[int, int, int, int] | None, scrshoter: Screenshoter, active: bool, keysequence: str = "", hotkey: Hotkey = None):
        self.__name = name
        self.__bbox = boundingbox
        self.__hotkey = hotkey
        self.__keysequence = keysequence
        self.__scrshoter = scrshoter
        self.__active = active

    @staticmethod
    def fromdict(saved: dict, scrshoter: Screenshoter, listening: bool = False):
        if not "name" in saved.keys():
            return None
        name = saved["name"]
        if not "sequence" in saved.keys():
            return None
        sequence = saved["sequence"]
        if len(sequence) < 5:
            return None
        if not "active" in saved.keys():
            return None
        active = saved["active"]
        if "bbox" in saved.keys():
            bbox = []
            for pos in saved["bbox"]:
                bbox.append(int(pos))
            bbox = tuple(bbox)
        else:
            bbox = None
        sarea = ScreenshotArea(name, bbox, scrshoter, active, sequence)
        if listening:
            hotkeyfunc = sarea.generatefunction()
            if type(hotkeyfunc) is tuple:
                hotkey = Hotkey(Hotkey.specifichotkeysequence(sequence), hotkeyfunc[0], hotkeyfunc[1], active)
                sarea.sethotkey(hotkey)
            else:
                hotkey = Hotkey(Hotkey.specifichotkeysequence(sequence), hotkeyfunc, None, active)
                sarea.sethotkey(hotkey)
        return sarea

    def dictingify(self) -> dict:
        rep = {"name": self.__name}
        if self.__bbox is not None:
            rep["bbox"] = f"{self.__bbox[0]}x{self.__bbox[1]}x{self.__bbox[2]}x{self.__bbox[3]}"
        rep["sequence"] = self.__keysequence
        rep["active"] = str(self.__active)
        return rep

    def gethotkey(self) -> Hotkey | None:
        if self.__hotkey is not None:
            return self.__hotkey
        else:
            return None

    def sethotkey(self, hotkey: Hotkey):
        self.__hotkey = hotkey

    def getkeysequence(self) -> str:
        return self.__keysequence

    def setkeysequence(self, sequence: str):
        self.__keysequence = sequence

    def getbbox(self) -> tuple[int, int, int, int]:
        return self.__bbox

    def setbbox(self, boundingbox: tuple[int, int, int, int]):
        self.__bbox = boundingbox

    def getname(self) -> str:
        return self.__name

    def setname(self, name: str):
        self.__name = name

    def activatehotkey(self):
        self.__active = True
        if self.__hotkey is not None:
            self.__hotkey.activate()

    def deactivatehotkey(self):
        self.__active = False
        if self.__hotkey is not None:
            self.__hotkey.deactivate()

    def generatefunction(self) -> tuple[Callable, tuple] | Callable:
        if self.__bbox is None:
            return self.__scrshoter.takefullscreenscreenshot
        else:
            return self.__scrshoter.takeareascreenshot, self.__bbox
