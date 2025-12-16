from InterfaceLayout.ScreenshotsWindow_UI import Ui_ScreenshotsWindow_UI
from DataModules.DatabaseTables import Project, Group, Screenshot

class ScreenshotWindow(Ui_ScreenshotsWindow_UI):
    def __init__(self):
        self.__project: Project
        self.__group: Group
        self.__loadedscreenshots: list[Screenshot]

    def __projectevent(self):
        pass

    def __groupevent(self):
        pass

    def __openscreenshotevent(self):
        pass

    def __searchevent(self):
        pass
