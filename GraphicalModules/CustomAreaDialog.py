from PySide6.QtGui import QKeySequence
from DataModules.Configuration import Configuration
from DataModules.DatabaseTables import Profile
from GraphicalModules.AreaPickerDialogs import InteractiveAreaPicker, NonInteractiveAreaPicker
from InterfaceLayout.ui_CustomAreaDialog import Ui_CustomAreaDialog_UI
from PySide6.QtWidgets import QDialog

class CustomAreaDialog(QDialog, Ui_CustomAreaDialog_UI):
    """Class responsible for editing custom area data"""
    def __init__(self, profile: Profile, name: str, config: Configuration):
        super().__init__()
        self.ui = Ui_CustomAreaDialog_UI()
        self.ui.setupUi(self)
        self.__config: Configuration = config
        self.__oldname = name
        self.__profile: Profile = profile
        self.__area: dict
        for area in self.__profile.getconfig("areas"):
            if area["name"] == name:
                self.__area = dict(area)
                break
        self.__name: str = name
        self.__shortcut: str = self.__area["sequence"]
        self.__bbox: tuple[int, int, int, int] | None = None
        self.ui.CustomArea_NameLineedit.setText(self.__name)
        self.ui.CustomArea_NameLineedit.editingFinished.connect(self.__changenameevent)
        self.ui.CustomArea_ShortcutKeysequenceedit.setKeySequence(QKeySequence(self.__shortcut))
        self.ui.CustomArea_ShortcutKeysequenceedit.editingFinished.connect(self.__shortcutevent)
        self.ui.CustomArea_SelectAreaButton.clicked.connect(self.__selectareaevent)
        self.ui.CustomArea_EnabledShortcutCheckbox.setChecked(self.__area["active"])
        self.ui.CustomArea_CloseButton.clicked.connect(self.__closeevent)
        self.ui.CustomArea_OkButton.clicked.connect(self.__okevent)

    def __changenameevent(self):
        """Attempts to change the name of the area"""
        newname = self.ui.CustomArea_NameLineedit.text()
        if len(newname) < 3:
            return
        for area in self.__profile.getconfig("areas"):
            if area["name"] == newname:
                return
        self.__area["name"] = newname
        self.__name = newname

    def __shortcutevent(self):
        """Grabs finished key sequence and saves it"""
        self.__area["sequence"] = self.ui.CustomArea_ShortcutKeysequenceedit.keySequence().toString()

    def __selectareaevent(self):
        """Gets area from user and saves it"""
        if self.__config.getconfig("general.interactiveselect"):
            picker = InteractiveAreaPicker()
            picker.exec()
            if picker.getpickedarea() is None:
                return
            self.__bbox = picker.getpickedarea()
        else:
            picker = NonInteractiveAreaPicker()
            picker.loadimage()
            picker.exec()
            if picker.getpickedarea() is None:
                return
            self.__bbox = picker.getpickedarea()

    def __closeevent(self):
        """Closes window without saving"""
        self.close()

    def __okevent(self):
        """Closes window with saving edited data"""
        changes: bool = False
        if self.__name != self.__oldname:
            changes = True
        if self.__shortcut != self.__area["sequence"]:
            changes = True
        if self.__bbox != None:
            self.__area["bbox"] = self.__bbox
        active: bool = self.ui.CustomArea_EnabledShortcutCheckbox.isChecked()
        if active != self.__area["active"]:
            changes = True
            self.__area["active"] = active
        if changes:
            newconfig = self.__profile.getconfig("areas")
            for i in range(len(newconfig)):
                if newconfig[i]["name"] == self.__oldname:
                    newconfig[i] = self.__area
                    self.__profile.setconfig("areas", newconfig)
                    self.__profile.saveconfig()
                    self.__profile.save()
                    break
        self.close()
