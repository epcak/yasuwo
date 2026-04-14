from DataModules.Configuration import Configuration
from DataModules.DatabaseData import DatabaseData
from DataModules.DatabaseTables import Project, Group
from PIL import ImageGrab
from datetime import datetime
from os import path, makedirs
import time


class Screenshoter:
    """Class that handles screenshoting"""
    def __init__(self, config: Configuration, project: Project, group: Group, dbdata: DatabaseData):
        self.__config: Configuration = config
        self.__selectedproject: Project = project
        self.__selectedgroup: Group = group
        self.__dbdata: DatabaseData = dbdata
        self.__imageloc: str = path.join(path.join(path.join(path.expanduser('~'), "Documents"), "yasuwo"), "screenshots")
        if not path.exists(self.__imageloc):
            makedirs(self.__imageloc)

    def takefullscreenscreenshot(self) -> str:
        """Takes and saves screenshot of the all screens

        :returns: name of created screenshot
        """
        taken = ImageGrab.grab()
        dt = datetime.now()
        takenrgb = taken.convert("RGB")
        name = "Screenshot_" + str(dt).replace(" ", '_').replace(":", ";")
        takenrgb.save(path.join(self.__imageloc, name + ".jpeg"), "jpeg")
        self.__dbdata.createscreenshot(name=name, project=self.__selectedproject, group=self.__selectedgroup)
        return name

    def takeareascreenshot(self, area: tuple[int, int, int, int]) -> str:
        """Takes and saves screenshot inside selected area

        :param area: ``tuple`` of bounding box
        :returns: name of created screenshot
        """
        taken = ImageGrab.grab(bbox=area)
        dt = datetime.now()
        takenrgb = taken.convert("RGB")
        name = "Screenshot_" + str(dt).replace(" ", '_').replace(":", ";")
        takenrgb.save(path.join(self.__imageloc, name + ".jpeg"), "jpeg")
        self.__dbdata.createscreenshot(name=name, project=self.__selectedproject, group=self.__selectedgroup)
        return name

    def onscreenareapicker(self) -> tuple[int, int, int, int] | None:
        """Opens dialog for picking screenshot area

        :returns: ``tuple`` of bounding box
        """
        from GraphicalModules.AreaPickerDialogs import NonInteractiveAreaPicker, InteractiveAreaPicker
        if self.__config.getconfig("general.interactiveselect"):
            picker = InteractiveAreaPicker()
            picker.exec()
            return picker.getpickedarea()
        else:
            picker = NonInteractiveAreaPicker()
            picker.loadimage()
            picker.exec()
            return picker.getpickedarea()

    def pickandtakeareascreenshot(self) -> str:
        """Shows area picker and takes screenshot

        :returns: name of created screenshot
        """
        from GraphicalModules.AreaPickerDialogs import NonInteractiveAreaPicker, InteractiveAreaPicker
        if self.__config.getconfig("general.interactiveselect"):
            picker = InteractiveAreaPicker()
            picker.exec()
            dt = datetime.now()
            name = "Screenshot_" + str(dt).replace(" ", '_').replace(":", ";")
            time.sleep(0.1)
            taken = ImageGrab.grab(picker.getpickedarea()).convert("RGB")
            taken.save(path.join(self.__imageloc, name + ".jpeg"), "jpeg")
            self.__dbdata.createscreenshot(name=name, project=self.__selectedproject, group=self.__selectedgroup)
            return name
        else:
            picker = NonInteractiveAreaPicker()
            taken = picker.loadimage()
            dt = datetime.now()
            picker.exec()
            cropped = taken.crop(picker.getpickedarea())
            converted = cropped.convert("RGB")
            name = "Screenshot_" + str(dt).replace(" ", '_').replace(":", ";")
            converted.save(path.join(self.__imageloc, name + ".jpeg"), "jpeg")
            self.__dbdata.createscreenshot(name=name, project=self.__selectedproject, group=self.__selectedgroup)
            return name
