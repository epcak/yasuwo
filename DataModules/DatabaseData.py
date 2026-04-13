import json
from DataModules.DatabaseTables import Project, Group, Screenshot, Profile
from DataModules.Configuration import Configuration
from DataModules.Constants import DB_FILE_PATH
from peewee import SqliteDatabase

class DatabaseData:
    def __init__(self, config: Configuration):
        self.__config = config
        self.__database = None #SqliteDatabase
        self.__location: str = ""

    def loaddatabase(self) -> str:
        """Tries to load database

        :Returns: ``ok`` if database was successfully loaded, ``new`` if any table needed to be created, ``err`` otherwise
        """
        self.__location = DB_FILE_PATH
        self.__database = SqliteDatabase(self.__location)
        if not self.__database.connect():
            return "err"
        found = Project.table_exists() and Group.table_exists() and Screenshot.table_exists() and Profile.table_exists()
        Project.create_table()
        Group.create_table()
        Screenshot.create_table()
        Profile.create_table()
        if Project.select().where(Project.name == "default").count() == 0:
            self.createproject("default", "Default project")
        if Group.select().where(Group.name == "default").count() == 0:
            self.creategroup("default", Project.select().where(Project.name == "default").get(), color="")
        if Profile.select().where(Profile.name == "default").count() == 0:
            self.createprofile("default")
        self.__database.close()
        if found:
            return "ok"
        else:
            return "new"

    def getprojects(self) -> list[Project]:
        """Gets all projects in database

        :returns: list of all ``Project``
        """
        return Project.select()

    def getproject(self, projectid: int) -> Project:
        """Gets project by its id

        :param projectid: id of requested project
        :returns: found ``Project``
        """
        return Project.select().where(Project.id == projectid).get()

    def getprojectbyname(self, name: str) -> Project:
        """Gets project by its name

        :param name: name of requested project
        :returns: found ``Project``
        """
        return Project.select().where(Project.name == name).get()

    def getgroups(self) -> list[Group]:
        """Gets all groups in database

        :returns: list of ``Group``
        """
        return Group.select()

    def getgroup(self, groupid: int) -> Group:
        """Gets group by its id

        :param groupid: id of requested group
        :returns: found ``Group``
        """
        return Group.select().where(Group.id == groupid).get()

    def getgroupbyname(self, name: str) -> Group:
        """Gets group by its name

        :param name: name of requested group
        :returns: found ``Group``
        """

    def getgroupsforproject(self, project: Project) -> list[Group]:
        """Gets all groups belonging to specified project

        :param project: project from which to get groups
        :returns: list of ``Group`` in project"""
        return Group.select().where(Group.project == project)

    def getscreenshots(self) -> list[Screenshot]:
        """Gets all screenshots in database

        :returns: list of all screenshots
        """
        return Screenshot.select()

    def getscreenshotsforproject(self, project: Project) -> list[Screenshot]:
        """Gets all screenshots belonging to specified project

        :param project: project from which to get screenshots
        :returns: list of ``Screenshot`` in project"""
        return Screenshot.select().where(Screenshot.project == project)

    def getscreenshotsforgroup(self, group: Group) -> list[Screenshot]:
        """Gets all screenshots belonging to specified group

        :param group: group from which to get screenshots
        :returns: list of ``Screenshot`` in group
        """
        return Screenshot.select().where(Screenshot.group == group)

    def searchscreenshotfortext(self, tofind: str) -> list[Screenshot]:
        """Searches screenshot text and notes for text

        :param tofind: text to find in screenshot
        :returns: list of ``Screenshot`` containing requested text
        """
        return Screenshot.select().where((Screenshot.imagetext.contains(tofind)) | (Screenshot.notes.contains(tofind)))

    def getscreenshot(self, name: str) -> Screenshot:
        """Gets screenshot by its name

        :param name: name of screenshot without file extension
        :returns: found ``Screenshot``
        """
        return Screenshot.select().where(Screenshot.name == name).get()

    def getprofiles(self) -> list[Profile]:
        """Gets all profiles in database

        :returns: list of all profiles
        """
        return Profile.select()

    def getprofile(self, profileid: int) -> Profile:
        """Gets profile by its id

        :param profileid: id of requested profile
        :returns: found ``Profile``
        """
        return Profile.select().where(Profile.id == profileid).get()

    def getprofilebyname(self, name: str) -> Profile:
        """Gets profile by its name

        :param name: name of requested profile
        :returns: found ``Profile``
        """
        return Profile.select().where(Profile.name == name).get()

    def createproject(self, name: str, description: str) -> Project:
        """Creates new project

        :param name: Project name
        :param description: Project description
        :returns: new ``Project``
        """
        newproject = Project(name=name, description=description, archived=0)
        newproject.save()
        return newproject

    def creategroup(self, name: str, profile: Profile, color: str) -> Group:
        """Creates new group

        :param name: Group name
        :param profile: Profile to which group belongs to
        :param color: hex formated color for group (#ffffff)
        :returns: new ``Group``
        """
        newgroup = Group(name=name, project=profile.id, color=color)
        newgroup.save()
        return newgroup

    def createscreenshot(self, name: str, project: Project, group: Group) -> Screenshot:
        """Creates new screenshot db entry (not file, only metadata/annotation)

        :param name: Screenshot name without file extension
        :param project: Project to which the screenshot belongs to
        :param group: Group to which the screenshot belongs to
        :returns: new ``Screenshot``
        """
        newscreenshot = Screenshot(name=name, project=project, group=group, annotation="", notes="", imagetext="")
        newscreenshot.save()
        return newscreenshot

    def createprofile(self, name: str) -> Profile:
        """Creates new profile

        :param name: Profile name
        :returns: new ``Profile``
        """
        newprofile = Profile(name=name, configuration=json.dumps({}))
        newprofile.configuration = json.dumps(self.__config.getwholeconfig())
        newprofile.save()
        return newprofile
