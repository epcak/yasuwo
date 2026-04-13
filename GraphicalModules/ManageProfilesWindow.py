import json

from PySide6.QtCore import QCoreApplication

from CoreModules.Hotkey import Hotkey
from CoreModules.Screenshoter import Screenshoter
from GraphicalModules.CustomAreaDialog import CustomAreaDialog
from InterfaceLayout.ui_ManageProfilesWindow import Ui_ManageProfilesWindow_UI
from DataModules.DatabaseData import DatabaseData
from DataModules.DatabaseTables import Profile, Project, Group
from DataModules.Configuration import Configuration
from CoreModules.ScreenshotArea import ScreenshotArea
from PySide6.QtWidgets import QDialog, QMessageBox


class ManageProfilesWindow(QDialog):
    def __init__(self, config: Configuration, dbdata: DatabaseData):
        super().__init__()
        self.ui = Ui_ManageProfilesWindow_UI()
        self.ui.setupUi(self)
        self.__config = config
        self.__dbdata = dbdata
        allprofiles = Profile.select()
        for aprofile in allprofiles:
            self.ui.ManageProfiles_SelectedProfileCombobox.addItem(aprofile.name)
        self.__profile: Profile = Profile.select().where(
            Profile.name == self.__config.getconfig("general.selectedprofile")).get()
        self.ui.ManageProfiles_SelectedProfileCombobox.setCurrentText(self.__profile.name)
        self.ui.ManageProfiles_NameProfileLineedit.setText(self.__profile.name)
        self.__project: Project
        if self.__profile.getconfig("project") is None:
            self.__project = Project.select().where(
                Project.name == self.__config.getconfig("general.selectedproject")).get()
        else:
            project = Project.select().where(Project.name == self.__profile.getconfig("project"))
            if len(project) == 0:
                self.__profile.setconfig("project", Project.select().where(Project.archived != 1).first().name)
                self.__profile.saveconfig()
                self.__profile.save()
            self.__project = Project.select().where(Project.name == self.__profile.getconfig("project")).get()
        allprojects = Project.select().where(Project.archived != 1)
        for aproject in allprojects:
            self.ui.ManageProfiles_ProjectOnCombobox.addItem(aproject.name)
        self.ui.ManageProfiles_ProjectOnCombobox.setCurrentText(self.__project.name)

        self.__group: Group
        if self.__profile.getconfig("group") is None:
            self.__group = Group.select().where(
                Group.name == self.__config.getconfig("general.selectedgroup")).get()
        else:
            group = Group.select().where((Group.name == self.__profile.getconfig("group")) & (Group.project == self.__project))
            if len(group) == 0:
                self.__profile.setconfig("group", Group.select().first().name)
                self.__profile.saveconfig()
                self.__profile.save()
            self.__group = Group.select().where((Group.name == self.__profile.getconfig("group")) & (Group.project == self.__project)).get()
        allgroups = Group.select().where(Group.project == self.__project.id)
        for agroup in allgroups:
            self.ui.ManageProfiles_GroupOnCombobox.addItem(agroup.name)
        self.ui.ManageProfiles_GroupOnCombobox.setCurrentText(self.__group.name)

        self.__areas: list[ScreenshotArea] = list()
        self.__scrshoter = Screenshoter(self.__config, self.__project, self.__group, self.__dbdata)
        self.__reloadareas()
        if self.ui.ManageProfiles_SelectedProfileCombobox.currentText() == "default":
            self.ui.ManageProfiles_NameProfileLineedit.setDisabled(True)
            self.ui.ManageProfiles_ProjectOnCombobox.setDisabled(True)
            self.ui.ManageProfiles_GroupOnCombobox.setDisabled(True)
        else:
            self.ui.ManageProfiles_NameProfileLineedit.setEnabled(True)
            self.ui.ManageProfiles_ProjectOnCombobox.setEnabled(True)
            self.ui.ManageProfiles_GroupOnCombobox.setEnabled(True)
        #Connections
        self.ui.ManageProfiles_SelectedProfileCombobox.currentIndexChanged.connect(self.__profilechangeevent)
        self.ui.ManageProfiles_AddProfileButton.clicked.connect(self.__addprofileevent)
        self.ui.ManageProfiles_NameProfileLineedit.editingFinished.connect(self.__namechangeevent)
        self.ui.ManageProfiles_ProjectOnCombobox.currentIndexChanged.connect(self.__projectselectevent)
        self.ui.ManageProfiles_GroupOnCombobox.currentIndexChanged.connect(self.__groupselectevent)
        self.ui.ManageProfiles_DeleteProfileButton.clicked.connect(self.__deleteprofileevent)
        self.ui.ManageProfiles_AddAreaButton.clicked.connect(self.__addareaevent)
        self.ui.ManageProfiles_EditAreaButton.clicked.connect(self.__editareaevent)
        self.ui.ManageProfiles_DeleteAreaButton.clicked.connect(self.__deleteareaevent)
        self.ui.ManageProfiles_CloseButton.clicked.connect(self.__closeevent)

    def __reloadareas(self):
        self.__areas.clear()
        self.ui.ManageProfiles_CustomAreasListWidget.clear()
        areas = self.__profile.getconfig("areas")
        if areas is None:
            return
        for area in areas:
            newsarea = ScreenshotArea(area["name"], area["bbox"], self.__scrshoter, False, area["sequence"], None)
            self.__areas.append(newsarea)
            self.ui.ManageProfiles_CustomAreasListWidget.addItem(area["name"])

    def __profilechangeevent(self):
        if self.__profile.name == self.ui.ManageProfiles_SelectedProfileCombobox.currentText():
            return
        else:
            name = self.ui.ManageProfiles_SelectedProfileCombobox.currentText()
            self.__profile = Profile.select().where(Profile.name == name).get()
        self.__reloadselectedprofile()

    def __addprofileevent(self):
        newname = "NewProfile"
        addnum = ""
        while len(Profile.select().where(Profile.name == f"{newname}{addnum}")) != 0:
            if addnum == "":
                addnum = 1
            else:
                addnum = addnum + 1
        newprofile = Profile(name=f"{newname}{addnum}", configuration=json.dumps({}))
        newprofile.configuration = json.dumps(self.__config.getwholeconfig())
        newprofile.save()
        name = f"{newname}{addnum}"
        self.__profile = newprofile
        self.ui.ManageProfiles_SelectedProfileCombobox.addItem(self.__profile.name)
        self.ui.ManageProfiles_SelectedProfileCombobox.setCurrentText(self.__profile.name)
        self.__reloadselectedprofile()

    def __reloadselectedprofile(self):
        """Unloads previously selected profile data and loads data related to currently selected profile"""
        self.ui.ManageProfiles_ProjectOnCombobox.setEnabled(False)
        self.ui.ManageProfiles_GroupOnCombobox.setEnabled(False)
        self.ui.ManageProfiles_NameProfileLineedit.setText(self.__profile.name)
        if self.__profile.getconfig("project") is None:
            self.__project = Project.select().where(
                Project.name == self.__config.getconfig("general.selectedproject")).get()
        else:
            project = Project.select().where(Project.name == self.__profile.getconfig("project"))
            if len(project) == 0:
                self.__profile.setconfig("project", Project.select().first().name)
                self.__profile.saveconfig()
                self.__profile.save()
            self.__project = Project.select().where(Project.name == self.__profile.getconfig("project")).get()
        self.ui.ManageProfiles_ProjectOnCombobox.clear()
        allprojects = Project.select().where(Project.archived != 1)
        for aproject in allprojects:
            self.ui.ManageProfiles_ProjectOnCombobox.addItem(aproject.name)
        self.ui.ManageProfiles_ProjectOnCombobox.setCurrentText(self.__project.name)
        self.ui.ManageProfiles_GroupOnCombobox.clear()
        if self.__profile.getconfig("group") is None:
            self.__group = Group.select().where(
                Group.name == self.__config.getconfig("general.selectedgroup")).get()
        else:
            group = Group.select().where(
                (Group.name == self.__profile.getconfig("group")) & (Group.project == self.__project))
            if len(group) == 0:
                self.__profile.setconfig("group", Group.select().first().name)
                self.__profile.saveconfig()
                self.__profile.save()
            self.__group = Group.select().where(
                (Group.name == self.__profile.getconfig("group")) & (Group.project == self.__project)).get()
        allgroups = Group.select().where(Group.project == self.__project.id)
        for agroup in allgroups:
            self.ui.ManageProfiles_GroupOnCombobox.addItem(agroup.name)
        self.ui.ManageProfiles_GroupOnCombobox.setCurrentText(self.__group.name)
        self.__reloadareas()
        if self.ui.ManageProfiles_SelectedProfileCombobox.currentText() == "default":
            self.ui.ManageProfiles_NameProfileLineedit.setDisabled(True)
            self.ui.ManageProfiles_ProjectOnCombobox.setDisabled(True)
            self.ui.ManageProfiles_GroupOnCombobox.setDisabled(True)
        else:
            self.ui.ManageProfiles_NameProfileLineedit.setEnabled(True)
            self.ui.ManageProfiles_ProjectOnCombobox.setEnabled(True)
            self.ui.ManageProfiles_GroupOnCombobox.setEnabled(True)

    def __namechangeevent(self):
        """Changes profile name"""
        if self.__profile.name == "default":
            return
        newname = self.ui.ManageProfiles_NameProfileLineedit.text()
        if len(newname) > 2 and len(Profile.select().where(Profile.name == newname)) == 0:
            self.__profile.name = newname
            self.__profile.save()
            self.ui.ManageProfiles_SelectedProfileCombobox.setItemText(
                self.ui.ManageProfiles_SelectedProfileCombobox.currentIndex(), newname)

    def __projectselectevent(self):
        """Changes selected project"""
        if not self.ui.ManageProfiles_ProjectOnCombobox.isEnabled():
            return
        newproject: Project
        found = Project.select().where(Project.name == self.ui.ManageProfiles_ProjectOnCombobox.currentText())
        if len(found) == 0:
            pass
        else:
            newproject = found.get()
            self.__profile.setconfig("project", newproject.name)
            self.__profile.saveconfig()
            self.__profile.save()
        self.__reloadselectedprofile()

    def __groupselectevent(self):
        """Changes selected group"""
        if not self.ui.ManageProfiles_GroupOnCombobox.isEnabled():
            return
        newgroup: Group
        found = Group.select().where((Group.name == self.ui.ManageProfiles_GroupOnCombobox.currentText())
                                     & (Group.project == self.__project.id))
        if len(found) == 0:
            pass
        else:
            newgroup = found.get()
            self.__profile.setconfig("group", newgroup.name)
            self.__profile.saveconfig()
            self.__profile.save()
        self.__reloadselectedprofile()

    def __deleteprofileevent(self):
        """Deletes selected profile"""
        if self.__profile.name == "default":
            return
        answereprofile = QMessageBox.question(self,
         QCoreApplication.translate("Delete profile dialog title",
                                    "Delete profile"),
         QCoreApplication.translate("Delete profile dialog text",
                                    "Do you want to delete this profile"),
         buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
         )
        if answereprofile != answereprofile.Yes:
            return
        self.__profile.delete_instance()
        indexremoved = self.ui.ManageProfiles_SelectedProfileCombobox.currentIndex()
        self.ui.ManageProfiles_SelectedProfileCombobox.removeItem(indexremoved)
        self.__profile = Profile.select().first()
        self.ui.ManageProfiles_SelectedProfileCombobox.setCurrentText(self.__profile.name)
        self.__reloadselectedprofile()

    def __addareaevent(self):
        pass
        current = self.__profile.getconfig("areas")
        if current is None:
            current = []
        newname = "NewArea"
        addnum = ""
        while True:
            found: bool = False
            for area in current:
                if area["name"] == f"{newname}{addnum}":
                    found = True
                    break
            if not found:
                break
            if addnum == "":
                addnum = 1
            else:
                addnum = addnum + 1

        current.append({"name": f"{newname}{addnum}", "bbox": (0, 0, 0, 0), "active": False, "sequence": ""})
        self.__profile.setconfig("areas", current)
        self.__profile.saveconfig()
        self.__profile.save()
        newsarea = ScreenshotArea(f"{newname}{addnum}", (0, 0, 0, 0), self.__scrshoter, False, "", None)
        self.__areas.append(newsarea)
        self.ui.ManageProfiles_CustomAreasListWidget.addItem(f"{newname}{addnum}")

    def __editareaevent(self):
        current = self.ui.ManageProfiles_CustomAreasListWidget.currentIndex().row()
        if current == -1:
            return
        subwindow = CustomAreaDialog(self.__profile, self.ui.ManageProfiles_CustomAreasListWidget.item(current).text(), self.__config)
        subwindow.exec()
        self.__reloadareas()

    def __deleteareaevent(self):
        """Asks user if they want to delete selected area and deletes it"""
        curitem = self.ui.ManageProfiles_CustomAreasListWidget.currentItem()
        if curitem is None:
            return
        todelname = curitem.text()
        for item in self.__areas:
            if item.getname() == todelname:
                answer = QMessageBox.question(self,
                  QCoreApplication.translate("Delete area dialog title",
                                             "Delete area"),
                  QCoreApplication.translate("Delete area dialog text",
                                             "Do you want to delete this area"),
                  buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                  )
                if answer == answer.Yes:
                    delname = curitem.text()
                    for area in self.__areas:
                        if area.getname() == delname:
                            self.__areas.remove(area)
                            confareas = self.__profile.getconfig("areas")
                            for confarea in confareas:
                                if confarea["name"] == delname:
                                    confareas.remove(confarea)
                                    break
                            self.__profile.setconfig("areas", confareas)
                            self.__profile.saveconfig()
                            self.__profile.save()
                            self.__reloadareas()
                            break
                break

    def __closeevent(self):
        """Closes window"""
        self.close()

    def selectprofile(self, profile: Profile):
        """Selects currently viewed profile"""
        profilename = profile.name
        self.ui.ManageProfiles_SelectedProfileCombobox.setCurrentText(profilename)
