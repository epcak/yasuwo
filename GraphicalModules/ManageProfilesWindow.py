from InterfaceLayout.ManageProfilesWindow_UI import Ui_ManageProfilesWindow_UI
from DataModules.DatabaseTables import Profile, Project, Group
from CoreModules.ScreenshotArea import ScreenshotArea

class ManageProfilesWindow(Ui_ManageProfilesWindow_UI):
    def __init__(self):
        self.__profile: Profile
        self.__project: Project
        self.__group: Group
        self.__areas: list[ScreenshotArea]

    def __profilechangeevent(self):
        pass

    def __addprofileevent(self):
        pass

    def __namechangeevent(self):
        pass

    def __projectselectevent(self):
        pass

    def __groupselectevent(self):
        pass

    def __deleteprofileevent(self):
        pass

    def __addareaevent(self):
        pass

    def __editareaevent(self):
        pass

    def __deleteareaevent(self):
        pass

    def __closeevent(self):
        pass
