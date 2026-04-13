from PySide6.QtGui import QColor
from DataModules.DatabaseTables import Screenshot, AnnotationType
from InterfaceLayout.ui_AnnotateWindow import Ui_AnnotateWindow_UI
from PySide6.QtWidgets import QDialog, QColorDialog, QLineEdit, QHBoxLayout, QPushButton
from CoreModules.Annotator import Annotator


class TextGrabWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.__layout = QHBoxLayout()
        self.textLineedit: QLineEdit = QLineEdit()
        self.__layout.addWidget(self.textLineedit)
        self.__okbutton: QPushButton = QPushButton("OK")
        self.__okbutton.clicked.connect(self.close)
        self.__layout.addWidget(self.__okbutton)
        self.setLayout(self.__layout)

class AnnotateWindow(QDialog):
    def __init__(self, screenshot: Screenshot):
        super().__init__()
        self.ui = Ui_AnnotateWindow_UI()
        self.ui.setupUi(self)
        self.__screenshot: Screenshot = screenshot
        self.__annotator: Annotator = Annotator(self.__screenshot)
        self.ui.Annotate_ImageLabel.mousePressEvent = lambda event: self.__imageclickevent(event.pos())
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())
        self.ui.Annotate_ColorLineedit.setText(self.__annotator.getcolor())
        self.ui.Annotate_LineButton.setDisabled(True)
        self.ui.Annotate_SizeSpinbox.setValue(8)

        self.ui.Annotate_ZoomInButton.clicked.connect(self.__zoominevent)
        self.ui.Annotate_ZoomOutButton.clicked.connect(self.__zoomoutevent)
        self.ui.Annotate_UndoButton.clicked.connect(self.__undoevent)
        self.ui.Annotate_RedoButton.clicked.connect(self.__redoevent)
        self.ui.Annotate_ColorButton.clicked.connect(self.__pickcolorevent)
        self.ui.Annotate_LineButton.clicked.connect(self.__linetoolevent)
        self.ui.Annotate_SquareButton.clicked.connect(self.__squaretoolevent)
        self.ui.Annotate_CircleButton.clicked.connect(self.__circletoolevent)
        self.ui.Annotate_TextButton.clicked.connect(self.__texttoolevent)
        self.ui.Annotate_SaveButton.clicked.connect(self.__saveevent)
        self.ui.Annotate_CloseButton.clicked.connect(self.__closeevent)
        self.ui.Annotate_SizeSpinbox.textChanged.connect(self.__changesizeevent)
        self.ui.Annotate_ColorLineedit.textChanged.connect(self.__colortextevent)
        self.ui.Annotate_FillCheckbox.clicked.connect(self.__fillevent)

    def __fillevent(self):
        self.__annotator.setfill(self.ui.Annotate_FillCheckbox.isChecked())

    def __colortextevent(self):
        text = self.ui.Annotate_ColorLineedit.text()
        for ch in text.replace("#", ""):
            if not ('a' <= ch <= 'f' or '0' <= ch <= '9'):
                return
        if len(text.replace("#", "")) ==  6:
            self.__annotator.setcolor(text)

    def __changesizeevent(self):
        self.__annotator.setsize(int(self.ui.Annotate_SizeSpinbox.value()))

    def __enabtools(self):
        self.ui.Annotate_LineButton.setEnabled(True)
        self.ui.Annotate_SquareButton.setEnabled(True)
        self.ui.Annotate_CircleButton.setEnabled(True)
        self.ui.Annotate_TextButton.setEnabled(True)

    def __linetoolevent(self):
        self.__annotator.settool(AnnotationType.LINE)
        self.__enabtools()
        self.ui.Annotate_LineButton.setDisabled(True)

    def __squaretoolevent(self):
        self.__annotator.settool(AnnotationType.SQUARE)
        self.__enabtools()
        self.ui.Annotate_SquareButton.setDisabled(True)

    def __circletoolevent(self):
        self.__annotator.settool(AnnotationType.CIRCLE)
        self.__enabtools()
        self.ui.Annotate_CircleButton.setDisabled(True)

    def __texttoolevent(self):
        self.__annotator.settool(AnnotationType.TEXT)
        self.__enabtools()
        self.ui.Annotate_TextButton.setDisabled(True)

    def __sizechangeevent(self):
        size = self.ui.Annotate_SizeSpinbox.value()
        self.__annotator.setsize(size)

    def __pickcolorevent(self):
        """Shows color dialog and grabs color from user"""
        colorstring = str(self.__annotator.getcolor())
        colorarr = [0, 0, 0, 255]
        if len(colorstring) >= 6:
            try:
                colorstring = colorstring.replace("#", "")
                if colorstring == "000":
                    pass
                else:
                    colorarr[0] = int(colorstring[0:2], 16)
                    colorarr[1] = int(colorstring[2:4], 16)
                    colorarr[2] = int(colorstring[4:6], 16)
            except ValueError:
                return
        colorpicker = QColorDialog(parent=self, currentColor=QColor(colorarr[0], colorarr[1], colorarr[2], colorarr[3]))
        colorpicker.exec()
        picked = colorpicker.currentColor().getRgb()
        r, g, b = f"{picked[0]:x}", f"{picked[1]:x}", f"{picked[2]:x}"
        if len(r) == 1: r = "0" + r
        if len(g) == 1: g = "0" + g
        if len(b) == 1: b = "0" + b
        newcolor = f"#{r}{g}{b}"
        self.__annotator.setcolor(newcolor)
        self.ui.Annotate_ColorLineedit.setText(newcolor)

    def __imageclickevent(self, pos):
        point = (pos.x()/ self.__annotator.getzoom(), pos.y() / self.__annotator.getzoom())
        reload = False
        if self.__annotator.gettool() == AnnotationType.TEXT:
            window = TextGrabWindow(self)
            window.exec()
            text = window.textLineedit.text()
            if len(text) == 0:
                return
            reload = True
            self.__annotator.addposition(point, text)
        else:
            reload = self.__annotator.addposition(point)
        if reload:
            pixmap = self.__annotator.getannotatedimage()
            self.ui.Annotate_ImageLabel.setPixmap(pixmap)
            self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __zoominevent(self):
        self.__annotator.zoomin()
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __zoomoutevent(self):
        self.__annotator.zoomout()
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __undoevent(self):
        self.__screenshot.undoannotation()
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __redoevent(self):
        self.__screenshot.redoannotation()
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __saveevent(self):
        self.__screenshot.saveannotation()
        pixmap = self.__annotator.getannotatedimage()
        self.ui.Annotate_ImageLabel.setPixmap(pixmap)
        self.ui.Annotate_ImageLabel.setFixedSize(pixmap.size())

    def __closeevent(self):
        self.__screenshot.clearannotation()
        self.close()
