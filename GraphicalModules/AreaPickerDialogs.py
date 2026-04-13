from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PIL import ImageGrab
from PIL.ImageQt import ImageQt
from PIL.Image import Image


class ClickableLabel(QLabel):
    """DO NOT USE. Class adding clicking functionality to QLabel - do not use outside this script"""
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        """Redefined mouse press event for grabbing cursor position"""
        pos = event.pos()
        self.clicked(pos)

    def clicked(self, pos):
        """Function sending cursor position to parent function"""
        self.parent().registerpoint(pos)

class AreaPicker(QDialog):
    """Parent class for area picker classes

    :param _firstpoint: position of first picked point
    :param _secondpoint: position of second picked point
    """
    def __init__(self):
        super().__init__()
        self._firstpoint: tuple[int, int] | None = None
        self._secondpoint: tuple[int, int] | None = None

    def getfirstpoint(self) -> tuple[int, int] | None:
        """Gets first selected point

        :returns: position of first point
        """
        return self._firstpoint

    def getsecondpoint(self) -> tuple[int, int] | None:
        """Gets second selected point

        :returns: position of second point
        """
        return self._secondpoint

    def getpickedarea(self) -> tuple[int, int, int, int] | None:
        """Function that calculates bounding box returns it

        :returns: bounding box of selected area
        """
        if self._firstpoint is not None and self._secondpoint is not None:
            bbox = [0, 0, 0, 0]
            if self._firstpoint[0] < self._secondpoint[0]:
                bbox[0] = self._firstpoint[0]
                bbox[2] = self._secondpoint[0]
            else:
                bbox[0] = self._secondpoint[0]
                bbox[2] = self._firstpoint[0]
            if self._firstpoint[1] < self._secondpoint[1]:
                bbox[1] = self._firstpoint[1]
                bbox[3] = self._secondpoint[1]
            else:
                bbox[1] = self._secondpoint[1]
                bbox[3] = self._firstpoint[1]
            return bbox[0], bbox[1], bbox[2], bbox[3]
        else:
            return None

class NonInteractiveAreaPicker(AreaPicker):
    """Class responsible for non-interactive area picker functionality

    :param __screenshotlabel: ``QLabel`` containing screenshot
    :param __screenshotimage: image of screenshot
    :param __scale: scale at which image is displayed
    """
    def __init__(self):
        super().__init__()
        self.__screenshotlabel = ClickableLabel(self)
        self.__screenshotimage = None
        self.__scale = 2
        self.__screenshotlabel.setText("Image not loaded")
        self.setWindowTitle(QCoreApplication.translate("Non-interactive area picker 1. point",
                                                       "Area picker - pick first point"))

    def loadimage(self) -> Image | None:
        """Tries to load image from screen

        :returns: ``Image`` of screen
        """
        if self.__screenshotimage is None:
            taken = ImageGrab.grab()
            reduced = taken.reduce(self.__scale)
            self.__screenshotimage = QPixmap.fromImage(ImageQt(reduced))
            self.__screenshotlabel.setPixmap(self.__screenshotimage)
            self.resize(self.__screenshotimage.width(), self.__screenshotimage.height())
            return taken
        else:
            return None

    def registerpoint(self, pos):
        """Registers selected point

        :param pos: position object of cursor
        """
        if self._firstpoint is None:
            self._firstpoint = (pos.x() * self.__scale, pos.y() * self.__scale)
            self.setWindowTitle(QCoreApplication.translate("Non-interactive area picker 2. point",
                                                          "Area picker - pick second point"))
        elif self._secondpoint is None:
            self._secondpoint = (pos.x() * self.__scale, pos.y() * self.__scale)
            self.close()


class InteractiveAreaPicker(AreaPicker):
    """Class responsible for interactive area picker functionality

    :param __layout: layout of the window
    :param __screenshotlabel: ``QLabel`` containing screenshot"""
    def __init__(self):
        super().__init__()
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__screenshotlabel = ClickableLabel(self)
        self.__screenshotlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(self.__screenshotlabel)
        self.__screenshotlabel.setText(QCoreApplication.translate("Interactive area picker 1. point",
                                                          "Select first point"))
        self.setWindowTitle(QCoreApplication.translate("Interactive area picker", "Area picker"))
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setLayout(self.__layout)
        self.setWindowOpacity(0.6)

    def registerpoint(self, pos):
        """Registers selected point

        :param pos: position object of cursor
        """
        if self._firstpoint is None:
            self._firstpoint = (pos.x(), pos.y())
            self.__screenshotlabel.setText(QCoreApplication.translate("Interactive area picker 2. point",
                                                          "Select second point"))
        elif self._secondpoint is None:
            self._secondpoint = (pos.x(), pos.y())
            self.close()
