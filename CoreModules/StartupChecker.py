from DataModules.Backup import Backuper
from DataModules.Configuration import Configuration
import pytesseract

from DataModules.DatabaseData import DatabaseData


class StartupChecker:
    """Class providing status check on startup

    :attr __status: ``dict`` of statuses
    :attr __config: configuration object
    """
    def __init__(self, config: Configuration, dbdata: DatabaseData):
        self.__status: dict = {}
        self.__config: Configuration = config
        self.__dbdata: DatabaseData = dbdata

    def check(self) -> bool:
        """Checks app functionality

        :returns: ``True`` if app is fully functioning, ``False`` otherwise
        """
        self.__status["config"] = self.__config.initconfigs()
        if self.__config.getconfig("ocr.installation") == "own":
            pytesseract.pytesseract.tesseract_cmd = self.__config.getconfig("ocr.path")
        elif self.__config.getconfig("ocr.installation") != "system":
            self.__status["ocr"] = "bad config"
        try:
            pytesseract.pytesseract.get_tesseract_version()
        except pytesseract.pytesseract.TesseractNotFoundError:
            self.__status["ocr"] = "not found"

        dbtest = self.__dbdata.loaddatabase()
        if dbtest == "err":
            self.__status["db"] = "error"
        elif dbtest == "new":
            self.__status["db"] = "new"

        Backuper().chechautomaticbackups(self.__config)

        if any(self.__status.values()):
            return False
        return True

    def getstatus(self, name: str) -> str:
        """Function to get status of given checked type

        :param name: ``str`` name of checked type
        :returns: ``str`` status of checked type
        """
        if name in self.__status.keys():
            return self.__status[name]
        else:
            return ""
