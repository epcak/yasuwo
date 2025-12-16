class Hotkey:
    def __init__(self, keysequence: str, function, active: bool = False):
        self.__keysequence = keysequence
        self.__function = function
        self.__active = active

    def gethotkey(self) -> str:
        pass

    def sethotkey(self, sequence: str):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass
