from InterfaceLayout.ui_AboutWindow import Ui_AboutWindow_UI
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QUrl
from DataModules.Constants import APP_VERSION


class AboutWindow(QDialog):
    """Class containing functionality for About Window"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_AboutWindow_UI()
        self.ui.setupUi(self)
        self.ui.About_NameVersionLabel.setText(f"yasuwo {APP_VERSION}")
        self.ui.About_CloseButton.clicked.connect(self.close)
        self.__loadtext()

    def __loadtext(self):
        """Loads text from license file"""
        url = QUrl.fromLocalFile("LICENSE.md")
        self.ui.About_AboutTextbrowser.setSource(url)
        self.ui.About_AboutTextbrowser.setOpenExternalLinks(True)
