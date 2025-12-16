from DatabaseTables import Project, Group, Screenshot, Profile
from Configuration import Configuration

from peewee import SqliteDatabase

class DatabaseData:
    def __init__(self, config: Configuration):
        self.__config = config
        self.__database: SqliteDatabase

    def getprojects(self) -> list[Project]:
        pass

    def getproject(self, projectid: int) -> Project:
        pass

    def getgroups(self) -> list[Group]:
        pass

    def getgroup(self, groupid: int) -> Group:
        pass

    def getscreenshots(self) -> list[Screenshot]:
        pass

    def getscreenshot(self, name: str) -> Screenshot:
        pass

    def getprofiles(self) -> list[Profile]:
        pass

    def getprofile(self, profileid: int) -> Profile:
        pass

    def createproject(self, name: str, description: str) -> Project:
        pass

    def creategroup(self, name: str, profile: Profile, color: str) -> Group:
        pass

    def createscreenshot(self, name: str, project: Project, group: Group) -> Screenshot:
        pass

    def createprofile(self, name: str) -> Profile:
        pass
