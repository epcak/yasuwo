from os import path

from PySide6.QtGui import QIcon, QPixmap

from DataModules.Configuration import Configuration
from GraphicalModules.ScreenshotViewWindow import ScreenshotViewWindow
from GraphicalModules.SearchWindow import SearchWindow
from InterfaceLayout.ui_ScreenshotsWindow import Ui_ScreenshotsWindow_UI
from DataModules.DatabaseTables import Project, Group, Screenshot
from DataModules.Constants import SCREENSHOTS_PATH, THUMBNAIL_SIZE
from PySide6.QtWidgets import QDialog, QListWidgetItem
from PySide6.QtCore import Qt, QSize


class ScreenshotWindow(QDialog):
    def __init__(self, project: Project, group: Group, config: Configuration):
        super().__init__()
        self.__project: Project = project
        self.__group: Group = group
        self.__config: Configuration = config
        self.__grouplock: bool = False
        self.__loadedscreenshots: list[Screenshot] = []
        self.ui = Ui_ScreenshotsWindow_UI()
        self.ui.setupUi(self)
        for allproject in Project.select().where(Project.archived == 0):
            self.ui.Screenshots_ProjectCombobox.addItem(allproject.name)
        self.ui.Screenshots_ProjectCombobox.setCurrentText(self.__project.name)
        for allgroup in Group.select().where(Group.project == self.__project.id):
            self.ui.Screenshots_GroupCombobox.addItem(allgroup.name)
        self.ui.Screenshots_GroupCombobox.setCurrentText(self.__group.name)
        self.ui.Screenshots_PreviewList.setSpacing(0)
        self.ui.Screenshots_PreviewList.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        self.__reloadscreenshots()
        self.ui.Screenshots_ProjectCombobox.currentIndexChanged.connect(self.__projectevent)
        self.ui.Screenshots_GroupCombobox.currentIndexChanged.connect(self.__groupevent)
        self.ui.Screenshots_PreviewList.clicked.connect(self.__openscreenshotevent)
        self.ui.Screenshots_CloseButton.clicked.connect(self.close)
        self.ui.Screenshots_SearchButton.clicked.connect(self.__searchevent)

    def __projectevent(self):
        self.__grouplock = True
        projectname = self.ui.Screenshots_ProjectCombobox.currentText()
        self.__project = Project.select().where(Project.name == projectname).get()
        self.ui.Screenshots_GroupCombobox.clear()
        for allgroup in Group.select().where(Group.project == self.__project.id):
            self.ui.Screenshots_GroupCombobox.addItem(allgroup.name)
        self.__group = Group.select().where(Group.project == self.__project.id).first()
        self.ui.Screenshots_GroupCombobox.setCurrentText(self.__group.name)
        self.__grouplock = False
        self.__reloadscreenshots()

    def __groupevent(self):
        if self.__grouplock: return
        groupname = self.ui.Screenshots_GroupCombobox.currentText()
        self.__group = Group.select().where((Group.project == self.__project.id) & (Group.name == groupname)).get()
        self.__reloadscreenshots()

    def __openscreenshotevent(self):
        subwindow = ScreenshotViewWindow(self.ui.Screenshots_PreviewList.currentItem().text())
        subwindow.exec()
        self.__reloadscreenshots()

    def __searchevent(self):
        subwindow = SearchWindow(self.__project, self.__group, self.__config)
        subwindow.exec()
        self.__reloadscreenshots()

    def __reloadscreenshots(self):
        self.ui.Screenshots_PreviewList.clear()
        self.__loadedscreenshots.clear()
        screenshots = Screenshot.select().where(
            (Screenshot.project == self.__project.id) & (Screenshot.group == self.__group.id))
        for screenshot in screenshots:
            pixmap = QPixmap(path.join(SCREENSHOTS_PATH, screenshot.getfilename()))
            thumbnail = pixmap.scaled(THUMBNAIL_SIZE*2, THUMBNAIL_SIZE*2,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
            self.__loadedscreenshots.append(screenshot)
            newitem = QListWidgetItem(screenshot.name)
            newitem.setIcon(QIcon(thumbnail))
            self.ui.Screenshots_PreviewList.addItem(newitem)
