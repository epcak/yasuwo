from InterfaceLayout.ProjectGroupDialog_UI import Ui_ProjectGroupDialog_UI
from DataModules.DatabaseTables import Group

class ProjectGroupDialog(Ui_ProjectGroupDialog_UI):
    def __init__(self):
        self.__group: Group
        self.__name: str
        self.__color: str

    def __changenameevent(self):
        pass

    def __pickcolorevent(self):
        pass

    def __cancelevent(self):
        pass

    def __okevent(self):
        pass
