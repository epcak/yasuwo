from CoreModules import Screenshoter
from DataModules.Configuration import Configuration
from DataModules.DatabaseData import DatabaseData
from GraphicalModules.ManageProfilesWindow import ManageProfilesWindow
from InterfaceLayout.ui_CustomAreaButtonsWindow import Ui_CustomAreaButtonsWindow_UI
from CoreModules.Screenshoter import Screenshoter
from DataModules.DatabaseTables import Profile
from PySide6.QtWidgets import QDialog

class CustomAreaButtonsWindow(QDialog):
    """Class containing controls for additional screenshot areas
    """
    def __init__(self, profile: Profile, config: Configuration, dbdata: DatabaseData, scrshoter: Screenshoter):
        super().__init__()
        self.__scrshoter: Screenshoter = scrshoter
        self.__profile: Profile = profile
        self.__config: Configuration = config
        self.__dbdata: DatabaseData = dbdata
        self.ui = Ui_CustomAreaButtonsWindow_UI()
        self.ui.setupUi(self)
        self.ui.CustomAreasButtons_CloseButton.clicked.connect(self.__closeevent)
        self.ui.CustomAreasButtons_ManageProfileButton.clicked.connect(self.__manageprofileevent)
        self.ui.CustomAreasButtons_SelectAreaButton.clicked.connect(self.__selectareaevent)
        self.ui.CustomAreasButtons_TakeScreenshotButton.clicked.connect(self.__takescreenshotevent)
        self.ui.CustomAreasButtons_SelectAreaButtonAdd.clicked.connect(self.__selectareaeventadd)
        self.ui.CustomAreasButtons_TakeScreenshotButtonAdd.clicked.connect(self.__takescreenshoteventadd)
        if self.__profile.getconfig("areas") is not None:
            for area in self.__profile.getconfig("areas"):
                self.ui.CustomAreasButtons_AreasListWidget.addItem(area["name"])

    def __selectareaevent(self):
        """Changes default area bounding box"""
        area = self.__scrshoter.onscreenareapicker()
        if area is not None:
            areastring = f"{area[0]}x{area[1]}x{area[2]}x{area[3]}"
            self.__config.setconfig("general.selectedarea", areastring)
            self.__config.saveconfig()

    def __selectareaeventadd(self):
        """Chages selected profile area bounding box"""
        selected = self.ui.CustomAreasButtons_AreasListWidget.currentItem()
        if selected is None:
            return
        area = self.__scrshoter.onscreenareapicker()
        if area is not None:
            areastring = f"{area[0]}x{area[1]}x{area[2]}x{area[3]}"
            for carea in self.__profile.getconfig("areas"):
                if carea["name"] == selected.text():
                    carea["bbox"] = areastring
                    self.__profile.saveconfig()
                    self.__profile.save()
                    return

    def __takescreenshotevent(self):
        """Takes default selected area screenshot"""
        selectedarea = self.__config.getconfig("general.selectedarea")
        if selectedarea == "0x0x0x0":
            self.__scrshoter.takefullscreenscreenshot()
        else:
            sarea = []
            for point in selectedarea.split("x"):
                sarea.append(int(point))
            self.__scrshoter.takeareascreenshot(tuple(sarea))

    def __takescreenshoteventadd(self):
        """Takes screenshot of selected area from profile"""
        selectedarea = ""
        selected = self.ui.CustomAreasButtons_AreasListWidget.currentItem()
        if selected is None:
            return
        for area in self.__profile.getconfig("areas"):
            if area["name"] == selected.text():
                selectedarea = area["bbox"]
                break
        if selectedarea == "0x0x0x0" or selectedarea == "" or selectedarea is None or selectedarea == [0, 0, 0, 0]:
            self.__scrshoter.takefullscreenscreenshot()
        else:
            area = [0 ,0, 0, 0]
            selectedarea = selectedarea.split("x")
            if int(selectedarea[0]) < int(selectedarea[2]):
                area[0] = int(selectedarea[0])
                area[2] = int(selectedarea[2])
            else:
                area[2] = int(selectedarea[0])
                area[0] = int(selectedarea[2])
            if int(selectedarea[1]) < int(selectedarea[3]):
                area[1] = int(selectedarea[1])
                area[3] = int(selectedarea[3])
            else:
                area[3] = int(selectedarea[1])
                area[1] = int(selectedarea[3])
            self.__scrshoter.takeareascreenshot(area)

    def __manageprofileevent(self):
        """Opens window for managing profiles with selected profile"""
        subwindow = ManageProfilesWindow(self.__config, self.__dbdata)
        subwindow.selectprofile(self.__profile)
        subwindow.exec()

    def __closeevent(self):
        """Closes window"""
        self.close()