from InterfaceLayout.MainWindow_UI import Ui_MainWindow_UI
from DataModules.DatabaseTables import Project, Group, Profile
from DataModules.Configuration import Configuration

class MainWindow(Ui_MainWindow_UI):
    def __init__(self):
        self.__project: Project
        self.__group: Group
        self.__profile: Profile
        self.__config: Configuration

    def __screenshoteverythingevent(self):
        pass

    def __screenshotselectedevent(self):
        pass

    def __screenshotareaevent(self):
        pass

    def __manageshortcutsevent(self):
        pass

    def __selectareaevent(self):
        pass

    def __quitevent(self):
        pass

    def __minimizeevent(self):
        pass

    def __settingsevent(self):
        pass

    def __selectprojectevent(self):
        pass

    def __selectgroupevent(self):
        pass

    def __manageprojectsevent(self):
        pass

    def __selectprofileevent(self):
        pass

    def __manageprofilesevent(self):
        pass

    def __aboutapplicationevent(self):
        pass

    def __usedlibrariesevent(self):
        pass

    def __helpevent(self):
        pass
