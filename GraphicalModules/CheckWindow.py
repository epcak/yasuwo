from peewee import Database

from InterfaceLayout.ui_CheckWindow import Ui_CheckWindow_UI
from GraphicalModules.SettingsWindow import SettingsWindow
from PySide6.QtWidgets import QMainWindow
from CoreModules.StartupChecker import StartupChecker
from DataModules.Configuration import Configuration
from DataModules.DatabaseData import DatabaseData
from PySide6.QtCore import QCoreApplication

class CheckWindow(QMainWindow):
    """Class containing warning and error messages on startup

    :attr __checker: Checker object containing startup status and checker
    :attr __config: Configuration object
    """
    def __init__(self, config: Configuration, dbdata: DatabaseData):
        super().__init__()
        self.ui = Ui_CheckWindow_UI()
        self.ui.setupUi(self)
        self.__dbdata: DatabaseData = dbdata
        self.__checker: StartupChecker = StartupChecker(config, dbdata)
        self.__config: Configuration = config
        self.ui.Check_StartButton.clicked.connect(self.__startevent)
        self.ui.Check_SettingsButton.clicked.connect(self.__settingsevent)
        if not self.__checker.check():
            self.__loadmessages()
            self.show()

    def __loadmessages(self):
        """Loads messages from checker"""
        if self.__checker.getstatus("config"):
            self.ui.Check_ListOfChecksTextbrowser.append(QCoreApplication.translate("CheckWindow new config", "Info: Configuration loaded from default template configuration\n"))
        ocr = self.__checker.getstatus("ocr")
        if ocr == "bad config":
            self.ui.Check_ListOfChecksTextbrowser.append(QCoreApplication.translate("CheckWindow bad ocr type", "Error: Bad type of tesseract installation in configuration\n"))
        elif ocr == "not found":
            self.ui.Check_ListOfChecksTextbrowser.append(QCoreApplication.translate("CheckWindow installation not found", "Error: Installation of tesseract not found\n"))
        if self.__checker.getstatus("db") == "error":
            self.ui.Check_ListOfChecksTextbrowser.append(QCoreApplication.translate("CheckWindow db error", "Error: Database wasn't properly loaded\n"))
        elif self.__checker.getstatus("db") == "new":
            self.ui.Check_ListOfChecksTextbrowser.append(QCoreApplication.translate("CheckWindow db tables", "Info: New database tables were created\n"))

    def __settingsevent(self):
        """Opens Settings window"""
        subwindow = SettingsWindow(self.__config)
        subwindow.exec()

    def __startevent(self):
        """Closes Check startup status window"""
        self.close()
