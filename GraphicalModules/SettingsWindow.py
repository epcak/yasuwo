from InterfaceLayout.SettingsWindow_UI import Ui_SettingsWindow_UI
from DataModules.Configuration import Configuration

class SettingsWindow(Ui_SettingsWindow_UI):
    def __init__(self):
        self.__config: Configuration
        self.__tesseractversion: str
        self.__tesseractstatus: str

    def __languageevent(self):
        pass

    def __themeevent(self):
        pass

    def __startupcheckevent(self):
        pass

    def __startuptypeevent(self):
        pass

    def __typeareaevent(self):
        pass

    def __annotationeditorevent(self):
        pass

    def __selectpatheditorevent(self):
        pass

    def __enablebackupevent(self):
        pass

    def __backupfrequencyevent(self):
        pass

    def __backupkeepevent(self):
        pass

    def __selectpathbackupevent(self):
        pass

    def __manualbackupevent(self):
        pass

    def __loadbackupevent(self):
        pass

    def __closeevent(self):
        pass

    def __applyevent(self):
        pass

    def __okevent(self):
        pass

    def __testtesseractevent(self):
        pass

    def __tesseracttypeevent(self):
        pass

    def __selectpathtesseractevent(self):
        pass

    def __tesseractlanguageevent(self):
        pass

    def __shortcuteverythingevent(self):
        pass

    def __shortcutselectedareaevent(self):
        pass

    def __selectaraevent(self):
        pass

    def __shortcutscreenshotareaevent(self):
        pass

    def __openmainevent(self):
        pass

    def __openprojectevent(self):
        pass

    def __openscreenshotevent(self):
        pass