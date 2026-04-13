from PySide6.QtGui import QColor
from InterfaceLayout.ui_ProjectGroupDialog import Ui_ProjectGroupDialog_UI
from PySide6.QtWidgets import QDialog, QColorDialog
from DataModules.DatabaseTables import Group


class ProjectGroupDialog(QDialog):
    """Class responsible for editing name and color of group

    :attr __group: Group to edit
    :attr __lastcorcol: Last known correct color
    """
    def __init__(self, group: Group):
        super().__init__()
        self.ui = Ui_ProjectGroupDialog_UI()
        self.ui.setupUi(self)
        self.__group: Group = group
        self.__lastcorcol = None
        self.ui.ProjectGroupDialog_NameLineedit.setText(group.name)
        self.ui.ProjectGroupDialog_ColorLineedit.setText(group.color)
        #connections
        self.ui.ProjectGroupDialog_OkButton.clicked.connect(self.__okevent)
        self.ui.ProjectGroupDialog_CancleButton.clicked.connect(self.__cancelevent)
        self.ui.ProjectGroupDialog_ColorLineedit.textChanged.connect(self.__changecolorevent)
        self.ui.ProjectGroupDialog_ColorLineedit.setMaxLength(7)
        self.ui.ProjectGroupDialog_ColorButton.clicked.connect(self.__pickcolorevent)

    def __changecolorevent(self):
        """Checks if user typed correct color and remembers it"""
        colorarr = [0, 0, 0, 255]
        colortext = self.ui.ProjectGroupDialog_ColorLineedit.text()
        if (len(colortext) == 7 and colortext.startswith("#")) or len(colortext) == 6:
            try:
                colortext = colortext.replace("#", "")
                colorarr[0] = int(colortext[0:2], 16)
                colorarr[1] = int(colortext[2:4], 16)
                colorarr[2] = int(colortext[4:6], 16)
            except ValueError:
                return
            self.__lastcorcol = f"#{colortext}"

    def __pickcolorevent(self):
        """Shows color dialog and grabs color from user"""
        colorstring = str(self.__group.color)
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
        self.__lastcorcol = newcolor
        self.ui.ProjectGroupDialog_ColorLineedit.setText(newcolor)

    def __cancelevent(self):
        """Closes window without saving"""
        self.close()

    def __okevent(self):
        """Closes window with saving"""
        groupname = self.ui.ProjectGroupDialog_NameLineedit.text()
        if groupname == "" or groupname == self.__group.name:
            pass
        else:
            addnum = ""
            while len(Group.select().where((Group.name == f"{groupname}{addnum}") & (Group.project == self.__group.project))) != 0:
                if addnum == "":
                    addnum = 1
                else:
                    addnum = addnum + 1
            self.__group.name = f"{groupname}{addnum}"
        if self.__lastcorcol is not None:
            self.__group.color = self.__lastcorcol
        self.__group.save()
        self.close()
