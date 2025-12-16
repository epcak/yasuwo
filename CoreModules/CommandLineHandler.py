from DataModules.Configuration import Configuration
from DataModules.DatabaseTables import Project, Group
from ScreenshotArea import ScreenshotArea

class CommandLineHandler:
    def __init__(self, config: Configuration):
        self.__config = config

    def __help(self):
        pass

    def __version(self):
        pass

    def __takescreenshot(self, project: Project, group: Group, area: ScreenshotArea):
        pass

    def __areapickscreenshot(self, project: Project, group: Group) -> str:
        pass

    def executeinput(self):
        pass