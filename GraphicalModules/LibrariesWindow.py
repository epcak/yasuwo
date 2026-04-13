from InterfaceLayout.ui_LibrariesWindow import Ui_LibrariesWindow_UI
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QUrl


class LibrariesWindow(QDialog):
    """Class containing functionality for Used Libraries Window"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_LibrariesWindow_UI()
        self.ui.setupUi(self)
        self.ui.Libraries_CloseButton.clicked.connect(self.close)
        self.__loadtext()

    def __loadtext(self):
        """Loads text from used libraries file"""
        url = QUrl.fromLocalFile("UsedLibraries.md")
        self.ui.Libraries_LibrariesTextbrowser.setSource(url)
        self.ui.Libraries_LibrariesTextbrowser.setOpenExternalLinks(True)
