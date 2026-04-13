import webbrowser
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction

from CoreModules.Hotkey import Hotkey
from CoreModules.ScreenshotArea import ScreenshotArea
from CoreModules.Screenshoter import Screenshoter
from DataModules.DatabaseData import DatabaseData
from GraphicalModules.CustomAreaButtonsWindow import CustomAreaButtonsWindow
from GraphicalModules.LibrariesWindow import LibrariesWindow
from GraphicalModules.ManageProfilesWindow import ManageProfilesWindow
from GraphicalModules.ManageProjectsWindow import ManageProjectsWindow
from GraphicalModules.AboutWindow import AboutWindow
from GraphicalModules.ScreenshotsWindow import ScreenshotWindow
from GraphicalModules.SettingsWindow import SettingsWindow
from InterfaceLayout.ui_MainWindow import Ui_MainWindow_UI
from DataModules.DatabaseTables import Project, Group, Profile
from DataModules.Configuration import Configuration
from PySide6.QtWidgets import QMainWindow, QMenu


class MainWindow(QMainWindow):
    """Class containing the main window of the application

    :attr __project: Selected project
    :attr __group: Selected group
    :attr __profile: Selected profile
    :attr __config: Current configuration
    :attr __scrshoter: Object taking screenshots
    :attr __groupactions: dictionary of currently available groups menu actions
    """
    def __init__(self, config: Configuration, dbdata: DatabaseData):
        self.__project: Project
        self.__group: Group
        self.__config: Configuration = config
        self.__profileblock: bool = False
        self.__profile: Profile = Profile.select().where(Profile.name == config.getconfig("general.selectedprofile")).get()
        if self.__config.getconfig("general.selectedproject") is None:
            self.__project = Project.select().first()
        else:
            project = Project.select().where(Project.name == self.__config.getconfig("general.selectedproject"))
            if len(project) == 0:
                self.__project = Project.select().where(Project.archived != 1).first()
            else:
                self.__project = project.get()
        if self.__config.getconfig("general.selectedgroup") is None:
            self.__group = Group.select().where(Group.project == self.__project.id).first()
        else:
            group = Group.select().where((Group.project == self.__project.id) & (Group.name == self.__config.getconfig("general.selectedgroup")))
            if len(group) == 0:
                self.__group = Group.select().where(Group.project == self.__project.id).first()
            else:
                self.__group = group.get()
        self.__dbdata: DatabaseData = dbdata
        self.__scrshoter: Screenshoter = Screenshoter(config, self.__project, self.__group, dbdata)
        self.__groupactions = dict()
        self.__globalhotkeys: list[Hotkey] = list()
        self.__profilehotkeys: list[ScreenshotArea] = list()
        self.__reloadprofilehotkeys()
        self.__reloadglobalhotkeys()
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow_UI()
        self.ui.setupUi(self)
        # adding connectors to menus and buttons
        self.ui.MainWindow_AboutApplicationAction.triggered.connect(self.__aboutapplicationevent)
        self.ui.MainWindow_UsedLibrariesAction.triggered.connect(self.__usedlibrariesevent)
        self.ui.MainWindow_SettingsAction.triggered.connect(self.__settingsevent)
        self.ui.MainWindow_QuitAction.triggered.connect(self.__quitevent)
        self.ui.MainWindow_MinimizeAction.triggered.connect(self.__minimizeevent)
        self.ui.MainWindow_ManageProjectsAction.triggered.connect(self.__manageprojectsevent)
        self.ui.MainWindow_ManageProfilesAction.triggered.connect(self.__manageprofilesevent)
        self.ui.MainWindow_ManageShortcutsButton.clicked.connect(self.__manageshortcutsevent)
        self.ui.MainWindow_ViewScreenshotsButton.clicked.connect(self.__viewscreenshotsevent)
        self.ui.MainWindow_CustomScreenshotsButton.clicked.connect(self.__customscreenshotsevent)
        self.ui.MainWindow_HelpAction.triggered.connect(self.__helpevent)
        self.ui.MainWindow_ScreenshotEverythingButton.clicked.connect(self.__screenshoteverythingevent)
        self.ui.MainWindow_ScreenshotSelectedButton.clicked.connect(self.__screenshotselectedevent)
        self.ui.MainWindow_ScreenshotAreaButton.clicked.connect(self.__screenshotareaevent)
        self.ui.MainWindow_SelectAreaButton.clicked.connect(self.__selectareaevent)
        self.__reloadprojects()
        self.__reloadprofiles()

    def __screenshoteverythingevent(self):
        """Takes screenshot of the whole desktop"""
        self.__scrshoter.takefullscreenscreenshot()

    def __screenshotselectedevent(self):
        """Takes screenshot of the selected area"""
        selectedarea = self.__config.getconfig("general.selectedarea")
        if selectedarea == "0x0x0x0":
            self.__scrshoter.takefullscreenscreenshot()
        else:
            sarea = []
            for point in selectedarea.split("x"):
                sarea.append(int(point))
            self.__scrshoter.takeareascreenshot(tuple(sarea))

    def __screenshotareaevent(self):
        """Opens window with area picker for screenshoting"""
        self.__scrshoter.pickandtakeareascreenshot()

    def __manageshortcutsevent(self):
        """Opens Window with shortcuts settings"""
        subwindow = SettingsWindow(self.__config)
        subwindow.openshortcuts()
        subwindow.exec()

    def __viewscreenshotsevent(self):
        """Opens Window with screenshots"""
        subwindow = ScreenshotWindow(self.__project, self.__group, self.__config)
        subwindow.exec()

    def __customscreenshotsevent(self):
        """Opens Window with custom screenshots"""
        subwindow = CustomAreaButtonsWindow(self.__profile, self.__config, self.__dbdata, self.__scrshoter)
        subwindow.exec()
        self.__reloadprofilehotkeys()

    def __selectareaevent(self):
        """Takes area from user and saves it"""
        area = self.__scrshoter.onscreenareapicker()
        if area is not None:
            areastring = f"{area[0]}x{area[1]}x{area[2]}x{area[3]}"
            self.__config.setconfig("general.selectedarea", areastring)
            self.__config.saveconfig()

    def __quitevent(self):
        """Quits the application"""
        self.close()

    def __minimizeevent(self):
        """Minimizes the application"""
        self.showMinimized()

    def __settingsevent(self):
        """Opens Windows with settings"""
        subwindow = SettingsWindow(self.__config)
        subwindow.exec()
        self.__reloadglobalhotkeys()

    def __selectgroupevent(self):
        """Changes currently selected project and group"""
        found = False
        for projectname in self.__groupactions.keys():
            if found: break
            for groupaction in self.__groupactions[projectname]:
                if found: break
                if groupaction.isEnabled() and groupaction.isChecked():
                    found = True
                    self.__config.setconfig("general.selectedproject", projectname)
                    self.__project = Project.select().where(Project.name == projectname).get()
                    self.__config.setconfig("general.selectedgroup", groupaction.text())
                    self.__group = Group.select().where((Group.name == groupaction.text()) & (Group.project == self.__project.id)).get()
                    self.__scrshoter = Screenshoter(self.__config, self.__project, self.__group, self.__dbdata)
        if found:
            self.__reloadprojects()
            self.__config.saveconfig()

    def __manageprojectsevent(self):
        """Opens Window for managing projects"""
        subwindow = ManageProjectsWindow(self.__config, self.__dbdata)
        subwindow.exec()

    def __selectprofileevent(self):
        if self.__profileblock: return
        self.__profileblock = True
        profilename: str = ""
        for action in self.ui.MainWindow_ProfilesMenu.actions():
            if not action.isEnabled() and action.isChecked():
                action.setChecked(False)
                action.setEnabled(True)
            elif action.isEnabled() and action.isChecked():
                profilename = action.text()
                action.setEnabled(False)
                action.setChecked(True)
        self.__profileblock = False
        if profilename != "":
            self.__profile = Profile.select().where(Profile.name == profilename).get()
            self.__reloadprofilehotkeys()
            if self.__profile.getconfig("project") is None:
                return
            else:
                project = Project.select().where(Project.name == self.__profile.getconfig("project"))
                if len(project) == 0:
                    self.__project = Project.select().where(Project.archived != 1).first()
                else:
                    self.__project = project.get()
            if self.__profile.getconfig("group") is None:
                self.__group = Group.select().where(Group.project == self.__project.id).first()
            else:
                group = Group.select().where((Group.project == self.__project.id) & (
                            Group.name == self.__profile.getconfig("group")))
                if len(group) == 0:
                    self.__group = Group.select().where(Group.project == self.__project.id).first()
                else:
                    self.__group = group.get()
            setprojectname = self.__project.name
            setgroupname = self.__group.name
            for projectname in self.__groupactions.keys():
                for groupaction in self.__groupactions[projectname]:
                    if groupaction.text() == setgroupname and projectname == setprojectname:
                        groupaction.setChecked(True)
                        return

    def __manageprofilesevent(self):
        """Opens Window for managing profiles"""
        subwindow = ManageProfilesWindow(self.__config, self.__dbdata)
        subwindow.exec()
        self.__reloadprofiles()
        self.__reloadprofilehotkeys()

    def __aboutapplicationevent(self):
        """Opens Window with information about the application"""
        subwindow = AboutWindow()
        subwindow.exec()

    def __usedlibrariesevent(self):
        """Opens Window with used libraries"""
        subwindow = LibrariesWindow()
        subwindow.exec()

    def __helpevent(self):
        """Opens website with help"""
        webbrowser.open("https://github.com/epcak/yasuwo/wiki")

    def __reloadprojects(self):
        """Reloads available projects and groups"""
        self.ui.MainWindow_ProjectsMenu.clear()
        self.__groupactions.clear()
        selectedproject = self.__config.getconfig("general.selectedproject")
        selectedgroup = self.__config.getconfig("general.selectedgroup")
        for project in Project.select().where(Project.archived != 1):
            projectmenu = QMenu(title=project.name, parent=self.ui.MainWindow_ProjectsMenu)
            self.__groupactions[project.name] = list()
            for group in Group.select().where(Group.project == project.id):
                groupaction = QAction(text=group.name, parent=projectmenu, checkable=True)
                if project.name == selectedproject and group.name == selectedgroup:
                    groupaction.setChecked(True)
                    groupaction.setDisabled(True)
                groupaction.toggled.connect(self.__selectgroupevent)
                projectmenu.addAction(groupaction)
                self.__groupactions[project.name].append(groupaction)
            self.ui.MainWindow_ProjectsMenu.addAction(projectmenu.menuAction())
        self.ui.MainWindow_ProjectsMenu.addSeparator()
        self.ui.MainWindow_ProjectsMenu.addAction(self.ui.MainWindow_ManageProjectsAction)
        self.ui.MainWindow_CurrentLabel.setText(QCoreApplication.translate(
            "Main window current project and group",
            f"Current project is {selectedproject}, group {selectedgroup}"
        ))

    def __reloadprofiles(self):
        """Reloads available profiles"""
        self.ui.MainWindow_ProfilesMenu.clear()
        selectedprofile = self.__config.getconfig("general.selectedprofile")
        for profile in Profile.select():
            profileaction = QAction(text=profile.name, parent=self.ui.MainWindow_ProfilesMenu, checkable=True)
            if profile.name == selectedprofile:
                profileaction.setChecked(True)
                profileaction.setDisabled(True)
            profileaction.toggled.connect(self.__selectprofileevent)
            self.ui.MainWindow_ProfilesMenu.addAction(profileaction)
        self.ui.MainWindow_ProfilesMenu.addSeparator()
        self.ui.MainWindow_ProfilesMenu.addAction(self.ui.MainWindow_ManageProfilesAction)

    def __reloadprofilehotkeys(self):
        for area in self.__profilehotkeys:
            area.deactivatehotkey()
        self.__profilehotkeys.clear()
        if self.__profile.getconfig("areas") is None:
            return
        for area in self.__profile.getconfig("areas"):
            if area["active"]:
                sarea = ScreenshotArea.fromdict(area, self.__scrshoter, True)
                if not sarea is None:
                    self.__profilehotkeys.append(area)

    def __updatearea(self):
        area = self.__scrshoter.onscreenareapicker()
        if area is None:
            return
        self.__config.setconfig("general.selectedarea", f"{area[0]}x{area[1]}x{area[2]}x{area[3]}")
        self.__config.saveconfig()

    def __reloadglobalhotkeys(self):
        for hotkey in self.__globalhotkeys:
            hotkey.deactivate()
        self.__globalhotkeys.clear()
        key = self.__config.getconfig("shortcuts.screenshots.everything")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__scrshoter.takefullscreenscreenshot, None, True))
        key = self.__config.getconfig("shortcuts.screenshots.selectedarea")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__scrshoter.takeareascreenshot, self.__config.getconfig("general.selectedarea").split("x"), True))
        key = self.__config.getconfig("shortcuts.screenshots.selectarea")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__updatearea, None, True))
        key = self.__config.getconfig("shortcuts.screenshots.area")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__scrshoter.takefullscreenscreenshot, None, True))
        key = self.__config.getconfig("shortcuts.windows.openmain")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.show, None, True))
        key = self.__config.getconfig("shortcuts.windows.openproject")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__manageprojectsevent, None, True))
        key = self.__config.getconfig("shortcuts.windows.openview")
        if len(key) > 5:
            self.__globalhotkeys.append(Hotkey(Hotkey.specifichotkeysequence(key), self.__viewscreenshotsevent, None, True))

