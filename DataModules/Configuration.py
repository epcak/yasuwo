from os import path, makedirs
from shutil import copyfile
import tomllib
import tomli_w
from DataModules.Constants import APP_DATA_PATH


class Configuration:
    """Class responsible for configuration stored in configuration file

    :attr __config: dictionary loaded from configuration file
    :attr __configlocation: path to configuration file
    """
    def __init__(self):
        self.__config: dict = {}
        self.__configlocation: str

    def __loadconfig(self, loc: str) -> None:
        """Loads configuration from settings.toml

        :param loc: path to configuration file
        """
        with open(loc, "rb") as f:
            self.__config = tomllib.load(f)
        self.__configlocation = loc

    def __runconfig(self) -> None:
        pass

    def saveconfig(self) -> bool:
        """Saves current configuration to configuration file

        :returns: ``True`` if configuration was saved
        """
        with open(self.__configlocation, "wb") as f:
            tomli_w.dump(self.__config, f)
        return False

    def reloadconfig(self) -> bool:
        """Reloads configuration from configuration file

        :returns: ``True`` if configuration was reloaded
        """
        with open(self.__configlocation, "rb") as f:
            self.__config = tomllib.load(f)
            return True

    def getconfig(self, name: str) -> str:
        """Gets specified configuration

        :param name: configuration name to find in format ``section.subsection/item.item``
        :returns: ``str`` with found configuration or text ERR
        """
        tofind = name.split(".")
        if len(tofind) == 2:
            return self.__config[tofind[0]][tofind[1]]
        elif len(tofind) == 3:
            return self.__config[tofind[0]][tofind[1]][tofind[2]]
        return "ERR"

    def setconfig(self, name: str, value) -> bool:
        """Sets specified configuration to new value

        :returns: ``True`` if configuration was changed/found, otherwise ``False``
        """
        tofind = name.split(".")
        if len(tofind) == 2:
            self.__config[tofind[0]][tofind[1]] = value
        elif len(tofind) == 3:
            self.__config[tofind[0]][tofind[1]][tofind[2]] = value
        else:
            return False
        return True

    def resetconfig(self, name: str) -> bool:
        """Resets specified configuration from configuration template

        :param name: configuration name to reset
        :returns: ``True`` if configuration was reset/found, otherwise ``False``
        """
        templateconfig = {}
        with open(self.__configlocation, "rb") as f:
            templateconfig = tomllib.load(f)
        tofind = name.split(".")
        if len(tofind) == 2:
            self.__config[tofind[0]][tofind[1]] = templateconfig[tofind[0]][tofind[1]]
        elif len(tofind) == 3:
            self.__config[tofind[0]][tofind[1]][tofind[2]] = templateconfig[tofind[0]][tofind[1]][tofind[2]]
        else:
            return False
        return True

    def initconfigs(self) -> bool:
        """Creates folder for app data and loads configuration

        :returns: ``True`` if configuration was created
        """
        appdir = APP_DATA_PATH
        if not path.exists(appdir):
            makedirs(appdir)
        created = False
        if not path.isfile(path.join(appdir, "settings.toml")):
            copyfile(path.join(path.curdir, "DefaultTemplates", "settingstemplate.toml"), path.join(appdir, "settings.toml"))
            created = True
        self.__loadconfig(path.join(appdir, "settings.toml"))
        return created

    def getwholeconfig(self) -> dict:
        """Gets whole configuration dictionary

        :returns: ``dict`` with current configuration
        """
        return self.__config
