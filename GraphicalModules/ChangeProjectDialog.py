from PySide6.QtWidgets import QDialog
from DataModules.DatabaseTables import Screenshot, Project, Group
from InterfaceLayout.ui_ChangeProjectDialog import Ui_ChangeProjectWindow_UI


class ChangeProjectDialog(QDialog):
    """Class responsible for changing screenshot project and group

    :attr __scrshot: `Screenshot` object to change"""
    def __init__(self, scrshot: Screenshot):
        super().__init__()
        self.ui = Ui_ChangeProjectWindow_UI()
        self.ui.setupUi(self)
        self.__scrshot: Screenshot = scrshot
        self.__project: Project = Project.select().where(Project.id == self.__scrshot.project).get()
        self.__group: Group = Group.select().where(Group.id == self.__scrshot.group).get()
        for project in Project.select().where(Project.archived == 0):
            self.ui.ChangeProject_ProjectCombobox.addItem(project.name)
        self.ui.ChangeProject_ProjectCombobox.setCurrentText(self.__project.name)
        for group in Group.select().where(Group.project == self.__project.id):
            self.ui.ChangeProject_GroupCombobox.addItem(group.name)
        self.ui.ChangeProject_GroupCombobox.setCurrentText(self.__group.name)
        self.ui.ChangeProject_ProjectCombobox.currentIndexChanged.connect(self.__changeprojectevent)
        self.ui.ChangeProject_SaveButton.clicked.connect(self.__saveevent)
        self.ui.ChangeProject_CloseButton.clicked.connect(self.close)

    def __changeprojectevent(self):
        """Refreshes groups associated with picked project"""
        self.ui.ChangeProject_GroupCombobox.clear()
        self.__project = Project.select().where(Project.name == self.ui.ChangeProject_ProjectCombobox.currentText()).get()
        for group in Group.select().where(Group.project == self.__project.id):
            self.ui.ChangeProject_GroupCombobox.addItem(group.name)
        self.ui.ChangeProject_GroupCombobox.setCurrentIndex(0)

    def __saveevent(self):
        """Saves changes made to screenshot project and group and closes window"""
        self.__scrshot.project = self.__project
        self.__group = Group.select().where((Group.project == self.__project.id) & (Group.name == self.ui.ChangeProject_GroupCombobox.currentText())).get()
        self.__scrshot.group = self.__group
        self.__scrshot.save()
        self.close()
