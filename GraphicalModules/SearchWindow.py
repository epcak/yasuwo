from os import path

from PySide6.QtCore import QDateTime, QSize, Qt, QCoreApplication
from PySide6.QtGui import QPixmap, QIcon

from DataModules.Constants import THUMBNAIL_SIZE, SCREENSHOTS_PATH
from DataModules.Configuration import Configuration
from GraphicalModules.ScreenshotViewWindow import ScreenshotViewWindow
from InterfaceLayout.ui_SearchWindow import Ui_SearchWindow_UI
from PySide6.QtWidgets import QDialog, QListWidgetItem
from DataModules.DatabaseTables import Project, Group, Screenshot

from datetime import datetime

class SearchWindow(QDialog):
    def __init__(self, project: Project, group: Group, config: Configuration):
        super().__init__()
        self.ui = Ui_SearchWindow_UI()
        self.ui.setupUi(self)
        self.__config: Configuration = config
        self.__project: Project = project
        self.__group: Group = group
        currenttime = QDateTime.currentDateTime()
        self.ui.Search_ToDatetimeedit.setDateTime(currenttime)
        self.ui.Search_FromDatetimeedit.setDateTime(currenttime.addMonths(-1))
        for project in Project.select().where(Project.archived == 0):
            self.ui.Search_ProjectCombobox.addItem(project.name)
        self.ui.Search_ProjectCombobox.setCurrentText(self.__project.name)
        for group in Group.select().where(Group.project == self.__project.id):
            self.ui.Search_GroupCombobox.addItem(group.name)
        self.ui.Search_GroupCombobox.setCurrentText(self.__group.name)
        self.ui.Search_PreviewList.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))

        self.ui.Search_ProjectCombobox.currentIndexChanged.connect(self.__projectchangeevent)
        self.ui.Search_CloseButton.clicked.connect(self.close)
        self.ui.Search_SearchButton.clicked.connect(self.__searchevent)
        self.ui.Search_PreviewList.clicked.connect(self.__openscreenshotevent)

    def __searchevent(self):
        self.ui.Search_PreviewList.clear()
        self.ui.Search_PreviewList.addItem(QCoreApplication.translate("Loading search",
                                                   "Loading search results, may take a while"))
        foundscreenshots: list[Screenshot] = []
        searchedtext = self.ui.Search_SearchLineedit.text()
        found = Screenshot.select()
        if self.ui.Search_GroupCheckbox.isChecked():
            project = Project.select().where(Project.name == self.ui.Search_ProjectCombobox.currentText()).get()
            group = Group.select().where((Group.name == self.ui.Search_GroupCombobox.currentText()) & (Group.project == project.id)).get()
            found = found.where((Screenshot.project == project.id) & (Screenshot.group == group.id))
        elif self.ui.Search_ProjectCheckbox.isChecked():
            project = Project.select().where(Project.name == self.ui.Search_ProjectCombobox.currentText()).get()
            found = found.where((Screenshot.project == project.id))
        lang = self.__config.getconfig("ocr.language")
        for screenshot in found:
            screenshot.analyzetext(lang)
        found = found.where((Screenshot.notes.contains(searchedtext)) | (Screenshot.imagetext.contains(searchedtext)))
        fromtime = self.ui.Search_FromDatetimeedit.dateTime().toPython()
        totime = self.ui.Search_ToDatetimeedit.dateTime().toPython()
        for screenshot in found:
            created: datetime = screenshot.getdatetime()
            if self.ui.Search_FromCheckbox.isChecked() and self.ui.Search_ToCheckbox.isChecked():
                if fromtime <= created <= totime:
                    foundscreenshots.append(screenshot)
            elif self.ui.Search_FromCheckbox.isChecked():
                if fromtime <= created:
                    foundscreenshots.append(screenshot)
            elif self.ui.Search_ToCheckbox.isChecked():
                if created <= totime:
                    foundscreenshots.append(screenshot)
            else:
                foundscreenshots.append(screenshot)
        self.ui.Search_PreviewList.clear()
        for screenshot in foundscreenshots:
            pixmap = QPixmap(path.join(SCREENSHOTS_PATH, screenshot.getfilename()))
            thumbnail = pixmap.scaled(THUMBNAIL_SIZE * 2, THUMBNAIL_SIZE * 2,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
            newitem = QListWidgetItem(screenshot.name)
            newitem.setIcon(QIcon(thumbnail))
            self.ui.Search_PreviewList.addItem(newitem)

    def __projectchangeevent(self):
        self.ui.Search_GroupCombobox.clear()
        self.__project = Project.select().where(Project.name == self.ui.Search_ProjectCombobox.currentText()).get()
        for group in Group.select().where(Group.project == self.__project.id):
            self.ui.Search_GroupCombobox.addItem(group.name)
        self.ui.Search_GroupCombobox.setCurrentIndex(0)

    def __openscreenshotevent(self):
        subwindow = ScreenshotViewWindow(self.ui.Search_PreviewList.currentItem().text())
        subwindow.exec()
        self.__searchevent()
