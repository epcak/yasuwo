from InterfaceLayout.SearchWindow_UI import Ui_SearchWindow_UI
from DataModules.DatabaseData import DatabaseData
from DataModules.DatabaseTables import Project, Group, Screenshot

from datetime import datetime

class SearchWindow(Ui_SearchWindow_UI):
    def __init__(self):
        self.__db: DatabaseData
        self.__project: Project
        self.__group: Group
        self.__from: datetime
        self.__to: datetime
        self.__found: list[Screenshot]

    def __searchevent(self):
        pass

    def __projectcheckevent(self):
        pass

    def __projectchangeevent(self):
        pass

    def __groupchackevent(self):
        pass

    def __groupchangeevent(self):
        pass

    def __fromchackevent(self):
        pass

    def __fromchangeevent(self):
        pass

    def __tocheckevent(self):
        pass

    def __tochangeevent(self):
        pass

    def __openscreenshotevent(self):
        pass

    def __closeevent(self):
        pass
