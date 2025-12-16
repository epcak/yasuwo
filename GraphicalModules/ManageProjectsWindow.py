from InterfaceLayout.ManageProjectsWindow_UI import Ui_ManageProjectsWindow_UI
from DataModules.DatabaseTables import Project, Group

class ManageProjectsWindow(Ui_ManageProjectsWindow_UI):
    def __init__(self):
        self.__project: Project
        self.__groups: list[Group]

    def __changeprojectevent(self):
        pass

    def __addprojectevent(self):
        pass

    def __namechangeevent(self):
        pass

    def __archivecheckevent(self):
        pass

    def __viewinfolderevent(self):
        pass

    def __deleteprojectevent(self):
        pass

    def __addgroupevent(self):
        pass

    def __editgroupevent(self):
        pass

    def __deletegroupevent(self):
        pass

    def __closeevent(self):
        pass
