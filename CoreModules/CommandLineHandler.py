from DataModules.Configuration import Configuration
from DataModules.DatabaseTables import Project, Group
from CoreModules.ScreenshotArea import ScreenshotArea
from DataModules.Constants import APP_VERSION

class CommandLineHandler:
    def __init__(self, config: Configuration):
        self.__config = config

    def __help(self):
        pass

    def __version(self):
        """Prints version string"""
        print("yasuwo version: " + APP_VERSION)

    def __takescreenshot(self, project: Project, group: Group, area: ScreenshotArea):
        pass

    def __areapickscreenshot(self, project: Project, group: Group) -> str:
        pass

    def executeinput(self):
        pass