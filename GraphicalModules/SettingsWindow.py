import copy
import sys

from InterfaceLayout.ui_SettingsWindow import Ui_SettingsWindow_UI
from DataModules.Configuration import Configuration
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QStyleFactory
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from os import path
import pytesseract
from DataModules.Backup import Backuper

class SettingsWindow(QDialog):
    """Class containing settings window

    :attr __config: Configuration object
    :attr __POSSIBLESETTINGS: ``dict`` of ``dict`` containing settings options that are not defined in ui
    """
    def __init__(self, config: Configuration):
        super().__init__()
        self.__config: Configuration = config
        self.__configcopy: Configuration = copy.deepcopy(self.__config)
        self.ui = Ui_SettingsWindow_UI()
        self.ui.setupUi(self)
        self.__POSSIBLESETTINGS: dict = {
            "Language": {"en": "English", "sk": "Slovenčina"},
            "Theme": {"system": QCoreApplication.translate("System theme", "System theme")},
            "Startup": {"minimized": QCoreApplication.translate("On system startup application minimized", "Minimized"),
                        "opened": QCoreApplication.translate("On system startup application opened", "Opened")},
            "Backups": {1: QCoreApplication.translate("Backup frequency daily", "Daily"),
                        7: QCoreApplication.translate("Backup frequency weekly", "Weekly"),
                        28: QCoreApplication.translate("Backup frequency monthly", "Monthly")}
        }
        self.__loadsettings()
        self.__testtesseract()

    def openshortcuts(self):
        """Changes active tab to shortcuts"""
        self.ui.Settings_SettingsTabwidget.setCurrentIndex(2)

    def __loadsettings(self):
        """Loads settings form configuration and setups connections"""
        # bottom buttons connections
        self.ui.Settings_CloseButton.clicked.connect(self.__closeevent)
        self.ui.Settings_OkButton.clicked.connect(self.__okevent)
        self.ui.Settings_ApplyButton.clicked.connect(self.__applyevent)
        # general tab
        self.ui.Settings_LanguageCombobox.addItems(self.__POSSIBLESETTINGS["Language"].values())
        try:
            self.ui.Settings_LanguageCombobox.setCurrentText(self.__POSSIBLESETTINGS["Language"][self.__config.getconfig("general.language")])
        except KeyError:
            pass
        self.ui.Settings_LanguageCombobox.textActivated.connect(self.__languageevent)
        self.ui.Settings_ThemeCombobox.addItems(self.__POSSIBLESETTINGS["Theme"].values())
        self.ui.Settings_ThemeCombobox.addItems(QStyleFactory.keys())
        try:
            self.ui.Settings_ThemeCombobox.setCurrentText(self.__POSSIBLESETTINGS["Theme"][self.__config.getconfig("general.theme")])
        except KeyError:
            pass
        self.ui.Settings_ThemeCombobox.textActivated.connect(self.__themeevent)
        self.ui.Settings_StartupCheckbox.setChecked(self.__config.getconfig("general.onstartup"))
        self.ui.Settings_StartupCheckbox.checkStateChanged.connect(self.__startupcheckevent)
        self.ui.Settings_StartupCombobox.addItems(self.__POSSIBLESETTINGS["Startup"].values())
        try:
            self.ui.Settings_StartupCombobox.setCurrentText(self.__POSSIBLESETTINGS["Startup"][self.__config.getconfig("general.startuptype")])
        except KeyError:
            pass
        self.ui.Settings_StartupCombobox.textActivated.connect(self.__startuptypeevent)
        if self.__config.getconfig("general.interactiveselect"):
            self.ui.Settings_InteractiveRadiobutton.setChecked(True)
        else:
            self.ui.Settings_FromImageRadiobutton.setChecked(True)
        self.ui.Settings_InteractiveRadiobutton.clicked.connect(self.__typeareaevent)
        self.ui.Settings_FromImageRadiobutton.clicked.connect(self.__typeareaevent)
        # general tab -> annotation
        editortype = self.__config.getconfig("general.annotation.editortype")
        if editortype == "buildin":
            self.ui.Settings_EditorBuiltRadiobutton.setChecked(True)
        elif editortype == "system":
            self.ui.Settings_EditorSystemRadiobutton.setChecked(True)
        elif editortype == "external":
            self.ui.Settings_EditorExternalRadiobutton.setChecked(True)
        self.ui.Settings_EditorBuiltRadiobutton.clicked.connect(self.__annotationeditorevent)
        self.ui.Settings_EditorSystemRadiobutton.clicked.connect(self.__annotationeditorevent)
        self.ui.Settings_EditorExternalRadiobutton.clicked.connect(self.__annotationeditorevent)
        self.ui.Settings_PathEditorLineedit.setText(self.__config.getconfig("general.annotation.editorpath"))
        self.ui.Settings_PathEditorButton.clicked.connect(self.__selectpatheditorevent)
        # general tab -> backup
        self.ui.Settings_AutomaticBackupsCheckbox.setChecked(self.__config.getconfig("general.backup.automatic"))
        self.ui.Settings_AutomaticBackupsCheckbox.clicked.connect(self.__enablebackupevent)
        self.ui.Settings_BackupFrequencyCombobox.addItems(self.__POSSIBLESETTINGS["Backups"].values())
        try:
            self.ui.Settings_BackupFrequencyCombobox.setCurrentText(self.__POSSIBLESETTINGS["Backups"][self.__config.getconfig("general.backup.frequency")])
        except KeyError:
            pass
        self.ui.Settings_BackupFrequencyCombobox.textActivated.connect(self.__backupfrequencyevent)
        self.ui.Settings_BackupKeepSpinbox.setValue(self.__config.getconfig("general.backup.keep"))
        self.ui.Settings_BackupKeepSpinbox.valueChanged.connect(self.__backupkeepevent)
        self.ui.Settings_PathBackupLineedit.setText(self.__config.getconfig("general.backup.path"))
        self.ui.Settings_PathBackupButton.clicked.connect(self.__selectpathbackupevent)
        self.ui.Settings_ManualBackupButton.clicked.connect(self.__manualbackupevent)
        self.ui.Settings_LoadBackupButton.clicked.connect(self.__loadbackupevent)
        # ocr tab
        self.ui.Settings_OcrTestButton.clicked.connect(self.__testtesseractevent)
        selectedocr = self.__config.getconfig("ocr.installation")
        if selectedocr == "system":
            self.ui.Settings_OcrSystemRadiobutton.setChecked(True)
        elif selectedocr == "own":
            self.ui.Settings_OcrOwnRadiobutton.setChecked(True)
        self.ui.Settings_OcrSystemRadiobutton.clicked.connect(self.__tesseracttypeevent)
        self.ui.Settings_OcrOwnRadiobutton.clicked.connect(self.__tesseracttypeevent)
        self.ui.Settings_OcrInstallationPathLineedit.setText(self.__config.getconfig("ocr.path"))
        self.ui.Settings_InstallationPathButton.clicked.connect(self.__selectpathtesseractevent)
        try:
            languages = pytesseract.get_languages()
            self.ui.Settings_OcrLanguageCombobox.addItems(languages)
            self.ui.Settings_OcrLanguageCombobox.setCurrentText(self.__config.getconfig("ocr.language"))
        except pytesseract.TesseractNotFoundError:
            pass
        self.ui.Settings_OcrLanguageCombobox.textActivated.connect(self.__tesseractlanguageevent)
        # shortcuts tab
        self.ui.Settings_ScreenshotEverythingKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.screenshots.everything")))
        self.ui.Settings_ScreenshotEverythingKeysequenceedit.editingFinished.connect(self.__shortcuteverythingevent)
        self.ui.Settings_ScreenshotSelectAreaKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.screenshots.selectedarea")))
        self.ui.Settings_ScreenshotSelectAreaKeysequenceedit.editingFinished.connect(self.__shortcutselectedareaevent)
        self.ui.Settings_SelectAreaKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.screenshots.selectarea")))
        self.ui.Settings_SelectAreaKeysequenceedit.editingFinished.connect(self.__selectaraevent)
        self.ui.Settings_ScreenshotAreaKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.screenshots.area")))
        self.ui.Settings_ScreenshotAreaKeysequenceedit.editingFinished.connect(self.__shortcutscreenshotareaevent)
        self.ui.Settings_OpenMainKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.windows.openmain")))
        self.ui.Settings_OpenMainKeysequenceedit.editingFinished.connect(self.__openmainevent)
        self.ui.Settings_OpenProjectKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.windows.openproject")))
        self.ui.Settings_OpenProjectKeysequenceedit.editingFinished.connect(self.__openprojectevent)
        self.ui.Settings_OpenViewKeysequenceedit.setKeySequence(QKeySequence.fromString(self.__config.getconfig("shortcuts.windows.openview")))
        self.ui.Settings_OpenViewKeysequenceedit.editingFinished.connect(self.__openscreenshotevent)

    def __testtesseract(self):
        """Tests tesseract installation for functionality and version"""
        version: str = "-"
        try:
            version = pytesseract.get_tesseract_version().base_version
            self.ui.Settings_OcrFunctionalLabel.setText(QCoreApplication.translate("SettingsWindow ocr test functional", "Tesseract is functional"))
        except pytesseract.TesseractNotFoundError:
            self.ui.Settings_OcrFunctionalLabel.setText(QCoreApplication.translate("SettingsWindow ocr test not functional", "Tesseract is not functional"))
        self.ui.Settings_OcrVersionLabel.setText(QCoreApplication.translate("SettingsWindow ocr version", "Tesseract version: " + version))

    def __languageevent(self, language: str):
        """Attempts language change and informs user about needed restart"""
        for key in self.__POSSIBLESETTINGS["Language"].keys():
            if language == self.__POSSIBLESETTINGS["Language"][key]:
                if self.__configcopy.getconfig("general.language") != key:
                    self.__configcopy.setconfig("general.language", key)
                    QMessageBox.information(self,
                                            QCoreApplication.translate("Changed lang title", "Language changed"),
                                            QCoreApplication.translate("Changed lang text", "For changes to take effect you need to restart application"))
                break

    def __themeevent(self, theme: str):
        """Attempts theme change and informs user about needed restart"""
        if theme in self.__POSSIBLESETTINGS["Theme"].values():
            for key in self.__POSSIBLESETTINGS["Theme"].keys():
                if theme == self.__POSSIBLESETTINGS["Theme"][key]:
                    if self.__configcopy.getconfig("general.theme") != key:
                        self.__configcopy.setconfig("general.theme", key)
                        QMessageBox.information(self,
                                                QCoreApplication.translate("Changed theme title", "Theme changed"),
                                                QCoreApplication.translate("Changed theme text",
                                                                           "For changes to take effect you need to restart application"))
                    break
        else:
            if theme != self.__configcopy.getconfig("general.theme"):
                self.__configcopy.setconfig("general.theme", theme)
                QMessageBox.information(self,
                                        QCoreApplication.translate("Changed theme title", "Theme changed"),
                                        QCoreApplication.translate("Changed theme text",
                                                                   "For changes to take effect you need to restart application"))

    def __startupcheckevent(self, state: Qt.CheckState):
        """Changes if opening of application on startup is prohibited"""
        self.__configcopy.setconfig("general.onstartup", state == Qt.CheckState.Checked)

    def __startuptypeevent(self, starttype: str):
        """Attempts to change startup type"""
        for key in self.__POSSIBLESETTINGS["Startup"].keys():
            if starttype == self.__POSSIBLESETTINGS["Startup"][key]:
                if self.__configcopy.getconfig("general.startuptype") != starttype:
                    self.__configcopy.setconfig("general.startuptype", key)
                break

    def __typeareaevent(self):
        """Attempts to change screenshot area picker type"""
        if self.ui.Settings_InteractiveRadiobutton.isChecked():
            self.__configcopy.setconfig("general.interactiveselect", True)
        elif self.ui.Settings_FromImageRadiobutton.isChecked():
            self.__configcopy.setconfig("general.interactiveselect", False)

    def __annotationeditorevent(self):
        """Changes annotation editor type"""
        if self.ui.Settings_EditorBuiltRadiobutton.isChecked():
            self.__configcopy.setconfig("general.annotation.editortype", "buildin")
        elif self.ui.Settings_EditorSystemRadiobutton.isChecked():
            self.__configcopy.setconfig("general.annotation.editortype", "system")
        elif self.ui.Settings_EditorExternalRadiobutton.isChecked():
            self.__configcopy.setconfig("general.annotation.editortype", "external")

    def __selectpatheditorevent(self):
        """Selects path for external editor"""
        filename = QFileDialog.getOpenFileName(self,
                                               QCoreApplication.translate("Select editor filepath", "Select editor executable"),
                                               path.curdir)
        if filename and filename[0] != "":
            self.ui.Settings_PathEditorLineedit.setText(filename[0])


    def __enablebackupevent(self):
        """Enables/Disables automatic backups"""
        self.__configcopy.setconfig("general.backup.automatic", self.ui.Settings_AutomaticBackupsCheckbox.isChecked())

    def __backupfrequencyevent(self, frequency: str):
        """Changes backup frequency"""
        numberedfreq: int
        for key in self.__POSSIBLESETTINGS["Backups"].keys():
            if key == frequency:
                numberedfreq = self.__POSSIBLESETTINGS["Backups"][key]
                self.__configcopy.setconfig("general.backup.frequency", numberedfreq)

    def __backupkeepevent(self):
        """Changes number of stored backups"""
        self.__configcopy.setconfig("general.backup.keep", self.ui.Settings_BackupKeepSpinbox.value())

    def __selectpathbackupevent(self):
        """Selects path to directory for backups"""
        backuppath = QFileDialog.getExistingDirectory(self,
                                               QCoreApplication.translate("Select backup filepath",
                                                                          "Select backup directory"),
                                               path.expanduser("~"),)
        if backuppath and backuppath != "":
            self.ui.Settings_PathBackupLineedit.setText(backuppath)

    def __manualbackupevent(self):
        """Grabs archive location from user and creates backup"""
        filename = QFileDialog.getSaveFileUrl(self, QCoreApplication.translate("Settings manual backup filedialog name",
                                                                               "Select backup location"),
                                              dir=path.expanduser("~"),
                                              filter=QCoreApplication.translate("Settings manual backup filetype", "ZIP file (*.zip)"))
        if filename[0].path() == "":
            return
        backuper = Backuper()
        filepath = filename[0].path()
        if not filepath.endswith(".zip"):
            filepath += ".zip"
        isbackuped = backuper.createmanualbackup(filepath, True, True, True)
        if isbackuped:
            QMessageBox().information(self,
                                       QCoreApplication.translate("Manual backup success title", "Backup created"),
                                       QCoreApplication.translate("Manual backup success text", "Backup was successfully created"))
        else:
            QMessageBox().warning(self,
                                  QCoreApplication.translate("Manual backup error title", "Backup error"),
                                  QCoreApplication.translate("Manual backup error text", "Error occurred during backup creation"))

    def __loadbackupevent(self):
        """Grabs backup location from user and applies backup"""
        procedeload = QMessageBox()
        procedeload.setWindowTitle(QCoreApplication.translate("Load confirm title", "Loading backup"))
        procedeload.setInformativeText(QCoreApplication.translate("Load confirm text",
                                                                  "Loading backup will delete all data. Do you want to continue?"))
        procedeload.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        selected = procedeload.exec()
        if not selected == QMessageBox.StandardButton.Yes:
            return
        filename = QFileDialog.getOpenFileName(self, QCoreApplication.translate("Settings load backup filedialog name",
                                                                               "Select backup file"),
                                              dir=path.expanduser("~"),
                                              filter=QCoreApplication.translate("Settings load backup filetype",
                                                                                "ZIP file (*.zip)"))
        if filename[0] == "":
            return
        backuper = Backuper()
        loaded = backuper.loadbackup(filename[0])
        if loaded:
            QMessageBox().information(self,
                                      QCoreApplication.translate("Load backup success title", "Backup loaded"),
                                      QCoreApplication.translate("Load backup success text",
                                                                 "Backup was successfully loaded, app will be closed"))
            sys.exit()
        else:
            QMessageBox().warning(self,
                                  QCoreApplication.translate("Load backup error title", "Backup error"),
                                  QCoreApplication.translate("Load backup error text",
                                                             "Error occurred during loading backup"))

    def __closeevent(self):
        """Closes settings window without saving"""
        self.close()

    def __applyevent(self):
        """Saves configuration without closing settings window"""
        if self.ui.Settings_OcrOwnRadiobutton.isChecked():
            self.__config.setconfig("ocr.installation", "own")
        else:
            self.__config.setconfig("ocr.installation", "system")
        self.__config.setconfig("ocr.path", self.ui.Settings_OcrInstallationPathLineedit.text())
        self.__configcopy.saveconfig()
        self.__config.reloadconfig()

    def __okevent(self):
        """Saves configuration and closes settings window"""
        if self.ui.Settings_OcrOwnRadiobutton.isChecked():
            self.__config.setconfig("ocr.installation", "own")
        else:
            self.__config.setconfig("ocr.installation", "system")
        self.__config.setconfig("ocr.path", self.ui.Settings_OcrInstallationPathLineedit.text())
        self.__configcopy.saveconfig()
        self.__config.reloadconfig()
        self.close()

    def __testtesseractevent(self):
        """Runs tesseract tests"""
        self.__testtesseract()

    def __tesseracttypeevent(self):
        """Changes tesseract installation type"""
        if self.ui.Settings_OcrSystemRadiobutton.isChecked():
            self.__configcopy.setconfig("ocr.installation", "system")
        elif self.ui.Settings_OcrOwnRadiobutton.isChecked():
            self.__configcopy.setconfig("ocr.installation", "own")

    def __selectpathtesseractevent(self):
        """Selects path for external tesseract installation"""
        filename = QFileDialog.getOpenFileName(self,
                                               QCoreApplication.translate("Select ocr filepath",
                                                                          "Select tesseract executable"),
                                               path.curdir)
        if filename and filename[0] != "":
            self.ui.Settings_OcrInstallationPathLineedit.setText(filename[0])

    def __tesseractlanguageevent(self, language: str):
        """Changes tesseract language"""
        self.__configcopy.setconfig("ocr.language", language)

    def __shortcuteverythingevent(self):
        """Changes shortcut for screenshoting everything"""
        self.__configcopy.setconfig("shortcuts.screenshots.everything",
                                    self.ui.Settings_ScreenshotEverythingKeysequenceedit.keySequence().toString())

    def __shortcutselectedareaevent(self):
        """Changes shortcut for screenshoting selected area"""
        self.__configcopy.setconfig("shortcuts.screenshots.selectedarea",
                                    self.ui.Settings_ScreenshotSelectAreaKeysequenceedit.keySequence().toString())

    def __selectaraevent(self):
        """Changes shortcut for selecting area"""
        self.__configcopy.setconfig("shortcuts.screenshots.selectarea",
                                    self.ui.Settings_SelectAreaKeysequenceedit.keySequence().toString())

    def __shortcutscreenshotareaevent(self):
        """Changes shortcut for screenshoting with area select"""
        self.__configcopy.setconfig("shortcuts.screenshots.area",
                                    self.ui.Settings_ScreenshotAreaKeysequenceedit.keySequence().toString())

    def __openmainevent(self):
        """Changes shortcut for opening main window"""
        self.__configcopy.setconfig("shortcuts.windows.openmain",
                                    self.ui.Settings_OpenMainKeysequenceedit.keySequence().toString())

    def __openprojectevent(self):
        """Changes shortcut for opening project window"""
        self.__configcopy.setconfig("shortcuts.windows.openproject",
                                    self.ui.Settings_OpenProjectKeysequenceedit.keySequence().toString())

    def __openscreenshotevent(self):
        """Changes shortcut for opening screenshots view window"""
        self.__configcopy.setconfig("shortcuts.windows.openproject",
                                    self.ui.Settings_OpenViewKeysequenceedit.keySequence().toString())