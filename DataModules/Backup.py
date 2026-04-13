from os import path, listdir, remove
import zipfile

from DataModules.Configuration import Configuration
from datetime import datetime, timedelta


class Backuper:
    """Class responsible for creating, managing and loading backups"""
    def __init__(self):
        documents = path.join(path.join(path.expanduser('~'), "Documents"))
        self.__datafolder = path.join(documents, "yasuwo")
        self.__automaticbackupname = "yasuwobackup:"
        self.__datetimeformat = "%Y-%m-%d %H:%M:%S.%f"

    def __backupdata(self, location: str, incscreenshot: bool, incconfig: bool, incdatabase: bool) -> bool:
        """Creates backup to zipfile

        :param location: location where to create backup
        :param incscreenshot: ``bool`` add screenshots to backups
        :param incconfig: ``bool`` add settings to backups
        :param incdatabase: ``bool`` add database to backups
        :returns: ``True`` if backup was created successfully
        """
        if not (incscreenshot or incconfig or incdatabase) and location == "":
            return False
        try:
            with zipfile.ZipFile(location, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as archive:
                name = "Created " + str(datetime.now()).replace(" ", "_")
                with open(name, "w"):
                    pass
                archive.write(name)
                remove(name)
                if incscreenshot:
                    screenshotspath = path.join(self.__datafolder, "screenshots")
                    if path.exists(screenshotspath) and path.isdir(screenshotspath):
                        for filename in listdir(screenshotspath):
                            archive.write(path.join(screenshotspath, filename), arcname=f"screenshots/{filename}")
                if incconfig:
                    configpath = path.join(self.__datafolder, "settings.toml")
                    if path.exists(configpath) and path.isfile(configpath):
                        archive.write(configpath, arcname="settings.toml")
                if incdatabase:
                    dbpath = path.join(self.__datafolder, "yasuwo.db")
                    if path.exists(dbpath) and path.isfile(dbpath):
                        archive.write(dbpath, arcname="yasuwo.db")
        except zipfile.BadZipFile:
            return False
        return True

    def createmanualbackup(self, location: str, incscreenshot: bool, incconfig: bool, incdatabase: bool) -> bool:
        """Creates manual backup to zipfile at specified location

        :param location: location where to create backup
        :param incscreenshot: ``bool`` add screenshots to backups
        :param incconfig: ``bool`` add settings to backups
        :param incdatabase: ``bool`` add database to backups
        :returns: ``True`` if backup was created successfully
        """
        return self.__backupdata(location, incscreenshot, incconfig, incdatabase)

    def chechautomaticbackups(self, config: Configuration):
        """Check if automatic backup is necessary and manages automatic backups

        :param config: object storing configuration
        """
        if not config.getconfig("general.backup.automatic"):
            return
        backupfolder = config.getconfig("general.backup.path")
        keepnumber = config.getconfig("general.backup.keep")
        backupfrequency = config.getconfig("general.backup.frequency")
        if not path.isdir(backupfolder):
            return
        threshold = datetime.now() - timedelta(days=int(backupfrequency))
        foundrecent = False
        foundlist = []
        for filename in listdir(backupfolder):
            if not (filename.startswith(self.__automaticbackupname) and filename.endswith(".zip")):
                continue
            foundlist.append(filename)
            createdat = datetime.strptime(filename.removeprefix(self.__automaticbackupname).removesuffix(".zip").replace("_", " "), self.__datetimeformat)
            if createdat > threshold:
                foundrecent = True
                break
        if not foundrecent:
            if self.__backupdata(path.join(backupfolder, self.__automaticbackupname + str(datetime.now()).replace(" ", "_") + ".zip"), True, True, True):
                if len(foundlist) >= int(keepnumber):
                    foundlist.sort()
                    foundlist.reverse()
                    toremove = path.join(backupfolder, foundlist[-1])
                    if path.isfile(toremove):
                        remove(toremove)

    def loadbackup(self, location: str) -> bool:
        """Loads backup from selected file

        :param location: where backup file is located
        :returns: ``True`` if backup file was loaded
        """
        if not path.isfile(location):
            return False
        try:
            with zipfile.ZipFile(location, "r") as archive:
                founddata = {"created": False, "screenshot": False, "config": False, "database": False}
                for archiveitem in archive.infolist():
                    filename = archiveitem.filename
                    if filename.startswith("Created "):
                        founddata["created"] = True
                    elif filename.startswith("screenshots/"):
                        founddata["screenshot"] = True
                    elif filename == "settings.toml":
                        founddata["config"] = True
                    elif filename == "yasuwo.db":
                        founddata["database"] = True
                if not founddata["created"]:
                    return False
                if founddata["database"]:
                    archive.extract("yasuwo.db", self.__datafolder)
                if founddata["config"]:
                    archive.extract("settings.toml", self.__datafolder)
                if founddata["screenshot"]:
                    for archiveitem in archive.infolist():
                        if not archiveitem.filename.startswith("screenshots/"):
                            continue
                        archive.extract(archiveitem.filename, self.__datafolder)
        except zipfile.BadZipFile:
            return False
        return True
