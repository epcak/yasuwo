class Translation:
    def __init__(self, lang: str):
        self.__translation: dict = {}
        self.__lang: str = lang

    def gettrans(self, name: str) -> str:
        pass

    def getlang(self) -> str:
        pass