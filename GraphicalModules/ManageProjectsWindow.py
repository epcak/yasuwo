import os
import platform
import subprocess
from os import path
from PySide6.QtCore import QCoreApplication
from DataModules.Constants import SCREENSHOTS_PATH
from DataModules.Configuration import Configuration
from DataModules.DatabaseData import DatabaseData
from GraphicalModules.ProjectGroupDialog import ProjectGroupDialog
from InterfaceLayout.ui_ManageProjectsWindow import Ui_ManageProjectsWindow_UI
from DataModules.DatabaseTables import Project, Group, Screenshot
from PySide6.QtWidgets import QDialog, QMessageBox


class ManageProjectsWindow(QDialog):
    """Class responsible for managing projects window

    :attr __dbdata: database data
    :attr __config: configuration of the app
    :attr __project: currently view project
    :attr __groups: groups associated with current project
    """
    def __init__(self, config: Configuration, dbdata: DatabaseData):
        super().__init__()
        self.ui = Ui_ManageProjectsWindow_UI()
        self.ui.setupUi(self)
        self.__dbdata = dbdata
        self.__config = config
        allprojects = Project.select()
        for aproject in allprojects:
            self.ui.ManageProjects_SelectedProjectCombobox.addItem(aproject.name)
        self.ui.ManageProjects_SelectedProjectCombobox.setCurrentText(self.__config.getconfig("general.selectedproject"))
        self.__project: Project = Project.select().where(Project.name == self.__config.getconfig("general.selectedproject")).get()
        self.__checkdefualtproject()
        self.ui.ManageProjects_NameProjectLineedit.setText(self.__project.name)
        if self.__project.archived == 1:
            self.ui.ManageProjects_Archived.setChecked(True)
        self.__reloadgroups()
        #connections
        self.ui.ManageProjects_SelectedProjectCombobox.currentIndexChanged.connect(self.__changeprojectevent)
        self.ui.ManageProjects_AddProjectButton.clicked.connect(self.__addprojectevent)
        self.ui.ManageProjects_NameProjectLineedit.editingFinished.connect(self.__namechangeevent)
        self.ui.ManageProjects_Archived.checkStateChanged.connect(self.__archivecheckevent)
        self.ui.ManageProjects_ViewInFilesButton.clicked.connect(self.__viewinfolderevent)
        self.ui.ManageProjects_DeleteButton.clicked.connect(self.__deleteprojectevent)
        self.ui.ManageProjects_AddGroupButton.clicked.connect(self.__addgroupevent)
        self.ui.ManageProjects_EditGroupButton.clicked.connect(self.__editgroupevent)
        self.ui.ManageProjects_DeleteGroupButton.clicked.connect(self.__deletegroupevent)
        self.ui.ManageProjects_CloseButton.clicked.connect(self.__closeevent)

    def __reloadgroups(self):
        """Loads groups to group list"""
        self.ui.ManageProjects_GoupsList.clear()
        self.__groups = Group.select().where(Group.project == self.__project.id)
        for agroup in self.__groups:
            self.ui.ManageProjects_GoupsList.addItem(agroup.name)

    def __changeprojectevent(self):
        """Changes currently viewed project"""
        projectname = self.ui.ManageProjects_SelectedProjectCombobox.currentText()
        project = Project.select().where(Project.name == projectname)

        if len(project) != 1:
            return
        project = project.get()
        self.__project = project
        self.__reloadprojectview()

    def __addprojectevent(self):
        """Creates new project"""
        newname = "NewProject"
        addnum = ""
        while len(Project.select().where(Project.name == f"{newname}{addnum}")) != 0:
            if addnum == "":
                addnum = 1
            else:
                addnum = addnum + 1
        newproject = Project(name=f"{newname}{addnum}", description="", archived=0)
        newproject.save()
        Group(name="default", project=newproject.id, color="").save()
        self.__reloadprojects(newproject)

    def __namechangeevent(self):
        """Changes name of selected project"""
        projectname = self.ui.ManageProjects_NameProjectLineedit.text()
        if len(Project.select().where(Project.name == projectname)) == 0:
            self.__project.name = projectname
            self.__project.save()
            self.__reloadprojects(self.__project)

    def __archivecheckevent(self):
        """Archives/de-archives project"""
        isarchived = self.ui.ManageProjects_Archived.isChecked()
        if isarchived:
            self.__project.archived = 1
        else:
            self.__project.archived = 0
        self.__project.save()

    def __viewinfolderevent(self):
        """Opens folder with screenshots"""
        systemos = platform.system()
        if systemos == "Windows":
            subprocess.run(['explorer', SCREENSHOTS_PATH])
        elif systemos == "Darwin":
            subprocess.run(['open', SCREENSHOTS_PATH])
        elif systemos == "Linux":
            subprocess.run(['xdg-open', SCREENSHOTS_PATH])

    def __deleteprojectevent(self):
        """Deletes project and associated screenshots and groups"""
        if self.__project.name == "default":
            return
        answerproject = QMessageBox.question(self,
                      QCoreApplication.translate("Delete project dialog title",
                                                 "Delete project"),
                      QCoreApplication.translate("Delete project dialog text",
                                                 "Do you want to delete this project"),
                      buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                      )
        if answerproject != answerproject.Yes:
            return
        answerscreenshots = QMessageBox.question(self,
                          QCoreApplication.translate("Delete project files dialog title",
                                                     "Delete project"),
                          QCoreApplication.translate("Delete project files dialog text",
                                                     "Do you want to delete screenshot pictures from computer"),
                          buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                          )
        screenshots = Screenshot.select().where(Screenshot.project == self.__project.id)
        if answerscreenshots == answerscreenshots.Yes:
            for screenshot in screenshots:
                scrshotpath = path.join(SCREENSHOTS_PATH, screenshot.getfilename())
                if path.isfile(scrshotpath):
                    os.remove(scrshotpath)
        for screenshot in screenshots:
            screenshot.delete_instance()
        Group.delete().where(Group.project == self.__project.id)
        self.__project.delete_instance()
        self.__reloadprojects()

    def __addgroupevent(self):
        """Creates new group"""
        newname = "NewGroup"
        addnum = ""
        while len(Group.select().where((Group.name == f"{newname}{addnum}") & (Group.project == self.__project.id))) != 0:
            if addnum == "":
                addnum = 1
            else:
                addnum = addnum + 1
        newgroup = Group(name=f"{newname}{addnum}", project=self.__project.id, color="")
        newgroup.save()
        self.__reloadgroups()

    def __editgroupevent(self):
        """Opens window for editing group"""
        curitem = self.ui.ManageProjects_GoupsList.currentItem()
        if curitem is None:
            return
        toeditname = curitem.text()
        toedit: None | Group = None
        for item in self.__groups:
            if item.name == toeditname:
                toedit = item
                break
        if toedit is not None:
            subwindow = ProjectGroupDialog(toedit)
            subwindow.exec()
            self.__reloadgroups()

    def __deletegroupevent(self):
        """Asks user if they want to delete selected group and deletes it"""
        if len(self.__groups) > 1:
            curitem = self.ui.ManageProjects_GoupsList.currentItem()
            if curitem is None:
                return
            todelname = curitem.text()
            for item in self.__groups:
                if item.name == todelname:
                    answer = QMessageBox.question(self,
                                         QCoreApplication.translate("Delete group dialog title",
                                                                    "Delete group"),
                                         QCoreApplication.translate("Delete group dialog text",
                                                                    "Do you want to delete this group"),
                                         buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                         )
                    if answer == answer.Yes:
                        ngroupid = Group.select().where((Group.project == self.__project.id)
                                                        & (Group.id != item.id))[0].id
                        for screenshot in Screenshot.select().where(
                                (Screenshot.group == item.id) &
                                (Screenshot.project == self.__project.id)):
                            screenshot.group = ngroupid
                            screenshot.save()
                        item.delete_instance()
                        self.__reloadgroups()
                    break

    def __closeevent(self):
        """Closes window"""
        self.close()

    def __checkdefualtproject(self):
        """Checks if project is default and disables some settings"""
        if self.__project.name == "default":
            self.ui.ManageProjects_NameProjectLineedit.setDisabled(True)
            self.ui.ManageProjects_DeleteButton.setDisabled(True)
            self.ui.ManageProjects_Archived.setDisabled(True)
        else:
            self.ui.ManageProjects_NameProjectLineedit.setDisabled(False)
            self.ui.ManageProjects_DeleteButton.setDisabled(False)
            self.ui.ManageProjects_Archived.setDisabled(False)

    def __reloadprojects(self, selected: Project | None = None):
        """Reloads projects

        :param selected: Project to be selected in list of projects
        """
        self.ui.ManageProjects_SelectedProjectCombobox.clear()
        for project in Project.select():
            self.ui.ManageProjects_SelectedProjectCombobox.addItem(project.name)
        if selected is None:
            self.__project = Project.select()[0]
        else:
            self.__project = selected
        self.ui.ManageProjects_SelectedProjectCombobox.setCurrentText(self.__project.name)
        self.__reloadprojectview()

    def __reloadprojectview(self):
        """Reloads project view"""
        self.ui.ManageProjects_NameProjectLineedit.setText(self.__project.name)
        self.ui.ManageProjects_Archived.setChecked(self.__project.archived == 1)
        self.__checkdefualtproject()
        self.__reloadgroups()
