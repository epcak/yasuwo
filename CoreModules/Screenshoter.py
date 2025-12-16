from DataModules.Configuration import Configuration
from DataModules.DatabaseTables import Project, Group


class Screenshoter:
    def __init__(self, config: Configuration, project: Project, group: Group):
        self.__config: Configuration = config
        self.__selectedproject: Project = project
        self.__selectedgroup: Group = group

    def takefullscreenscreenshot(self) -> str:
        pass

    def takeareascreenshot(self, area: str) -> str:
        pass

    def onscreenareapicker(self) -> str:
        pass