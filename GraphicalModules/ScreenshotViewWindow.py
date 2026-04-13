from PySide6.QtGui import QPixmap, QGuiApplication
from GraphicalModules.AnnotateWindow import AnnotateWindow
from GraphicalModules.ChangeProjectDialog import ChangeProjectDialog
from InterfaceLayout.ui_ScreenshotViewWindow import Ui_ScreenshotViewWindow_UI
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from DataModules.DatabaseTables import Screenshot
from PySide6.QtCore import QCoreApplication
from DataModules.Constants import SCREENSHOTS_PATH
from os import path

class ScreenshotViewWindow(QDialog):
    """Class responsible for viewing screenshot in detail"""
    def __init__(self, screenshotname: str):
        super().__init__()
        self.__zoomlevel = 3
        self.__original = False
        self.ui = Ui_ScreenshotViewWindow_UI()
        self.ui.setupUi(self)
        self.__screenshot: Screenshot = Screenshot.select().where(Screenshot.name == screenshotname).get()
        self.ui.ScreenshotView_ProjectLabel.setText(QCoreApplication.translate(
            "Main window current project and group",
            f"Project {self.__screenshot.project.name} Group {self.__screenshot.group.name}"
        ))
        self.__image = self.__screenshot.getannotatedimage().toqpixmap()
        self.__currentsize = self.__image.size()
        self.ui.ScreenshotView_ImageLabel.setPixmap(self.__image)
        self.ui.ScreenshotView_ImageTextGroup.setVisible(False)
        self.ui.ScreenshotView_NotesGroup.setVisible(False)
        self.__advanced = False
        self.ui.ScreenshotView_AdvanceModeCheckbox.checkStateChanged.connect(self.__advancedevent)
        self.__screenshot.analyzetext()
        self.ui.ScreenshotView_ImageTextPlaintextedit.setPlainText(self.__screenshot.getimagetext())
        self.ui.ScreenshotView_NotesPlaintextedit.setPlainText(self.__screenshot.notes)

        self.ui.ScreenshotView_ZoomInButton.clicked.connect(self.__zoominevent)
        self.ui.ScreenshotView_ZoomOutButton.clicked.connect(self.__zoomoutevent)
        self.ui.ScreenshotView_CopyTextButton.clicked.connect(self.__copytextevent)
        self.ui.ScreenshotView_AnnotateButton.clicked.connect(self.__annotateevent)
        self.ui.ScreenshotView_ExportButton.clicked.connect(self.__exportevent)
        self.ui.ScreenshotView_DeleteButton.clicked.connect(self.__deleteevent)
        self.ui.ScreenshotView_ChangeProjectButton.clicked.connect(self.__changeprojectevent)
        self.ui.ScreenshotView_CloseButton.clicked.connect(self.__closeevent)
        self.ui.ScreenshotView_OriginalCheckbox.checkStateChanged.connect(self.__originalcheckevent)

    def __advancedevent(self):
        """Shows/hides image text and notes"""
        self.__advanced = not self.__advanced
        if self.__advanced:
            self.ui.ScreenshotView_ImageTextGroup.setVisible(True)
            self.ui.ScreenshotView_NotesGroup.setVisible(True)
        else:
            self.ui.ScreenshotView_ImageTextGroup.setVisible(False)
            self.ui.ScreenshotView_NotesGroup.setVisible(False)

    def __zoominevent(self):
        """Makes viewed image larger"""
        if self.__zoomlevel == 7: return
        self.__zoomlevel += 1
        self.__currentsize.setWidth(self.__currentsize.width() * 2)
        self.__currentsize.setHeight(self.__currentsize.height() * 2)
        image = self.__image.scaled(self.__currentsize)
        self.ui.ScreenshotView_ImageLabel.setPixmap(image)

    def __zoomoutevent(self):
        """Makes viewed image smaller"""
        if self.__zoomlevel == 1: return
        self.__zoomlevel -= 1
        self.__currentsize.setWidth(self.__currentsize.width() / 2)
        self.__currentsize.setHeight(self.__currentsize.height() / 2)
        image = self.__image.scaled(self.__currentsize)
        self.ui.ScreenshotView_ImageLabel.setPixmap(image)

    def __originalcheckevent(self):
        self.__original = self.ui.ScreenshotView_OriginalCheckbox.isChecked()
        if self.__original:
            self.__image = self.__screenshot.getimage().toqpixmap()
        else:
            self.__image = self.__screenshot.getannotatedimage().toqpixmap()
        self.__currentsize = self.__image.size()
        image = self.__image.scaled(self.__currentsize)
        self.ui.ScreenshotView_ImageLabel.setPixmap(image)

    def __copytextevent(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.__screenshot.getimagetext())

    def __annotateevent(self):
        subwindow = AnnotateWindow(self.__screenshot)
        subwindow.exec()
        self.__screenshot.clearannotation()
        if not self.__original:
            self.__image = self.__screenshot.getannotatedimage().toqpixmap()
            self.__currentsize = self.__image.size()
            image = self.__image.scaled(self.__currentsize)
            self.ui.ScreenshotView_ImageLabel.setPixmap(image)
        self.__screenshot.clearannotation()

    def __changeprojectevent(self):
        subwindow = ChangeProjectDialog(self.__screenshot)
        subwindow.exec()
        self.ui.ScreenshotView_ProjectLabel.setText(QCoreApplication.translate(
            "Main window current project and group",
            f"Project {self.__screenshot.project.name} Group {self.__screenshot.group.name}"
        ))

    def __exportevent(self):
        file = QFileDialog.getSaveFileUrl(self, QCoreApplication.translate("Export annotated image filedialog name",
                                                                               "Select where to export image"),
                                              dir=path.expanduser("~"),
                                              filter=QCoreApplication.translate("Annotated image filetype",
                                                                                "JPG file (*.jpg)"))
        savepath = file[0].path()
        if len(savepath) == 0: return
        savepath += ".jpg"
        self.__screenshot.getannotatedimage().save(savepath, "JPEG")

    def __deleteevent(self):
        """Deletes screenshot"""
        answer = QMessageBox.question(self,
          QCoreApplication.translate("Delete screenshot dialog title",
                                     "Delete screenshot"),
          QCoreApplication.translate("Delete screenshot dialog text",
                                     "Do you want to delete this screenshot"),
          buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
          )
        if answer == answer.Yes:
            self.__screenshot.deleteimage()
            self.close()

    def __closeevent(self):
        """Saves notes and closes window"""
        notes = self.ui.ScreenshotView_NotesPlaintextedit.toPlainText()
        self.__screenshot.notes = notes
        self.__screenshot.save()
        self.close()
