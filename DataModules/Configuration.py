class Configuration:
    def __init__(self):
        self.__config: dict = {}

    def __loadconfig(self) -> bool:
        pass

    def __runconfig(self) -> None:
        pass

    def saveconfig(self) -> bool:
        pass

    def reloadconfig(self) -> bool:
        pass

    def getconfig(self, name: str) -> str:
        pass

    def setconfig(self, name: str, value) -> bool:
        pass

    def resetconfig(self, name: str) -> bool:
        pass