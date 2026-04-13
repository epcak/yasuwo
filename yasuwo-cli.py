import DataModules.Constants as constants
import sys
from CoreModules.Screenshoter import Screenshoter
from DataModules.Configuration import Configuration
from DataModules.DatabaseData import DatabaseData
from DataModules.DatabaseTables import Project, Group, Profile


def helpmenu():
    """Prints out help message"""
    print("\nOptions:")
    print("\t--help\t\t-h\tPrints help message")
    print("\t--version\t-v\tPrints version number")
    print("\t--project\t-p\tTaken screenshot is saved to provided project name")
    print("\t--group\t\t-g\tTaken screenshot is saved to provided group name (project must be given before this argument)")
    print("\t--full\t\t-f\tTakes fullscreen screenshot")
    print("\t--area\t\t-a\tTakes screenshot of default area")
    print("\t--profile\t\tGiven profile name is selected (needed for custom area)")
    print("\t--custom\t\tTakes screenshot of given area name (profile must be given before this argument)")

def parsearguments() -> None | dict:
    """Parse command line arguments"""
    arguments = sys.argv
    if len(arguments) == 1:
        print(f"yasuwo cli edition version {constants.APP_VERSION} - no arguments provided, printing help")
        helpmenu()
        return None
    if arguments[1] == "--help" or arguments[1] == "-h":
        print(f"yasuwo cli edition version {constants.APP_VERSION} help")
        helpmenu()
        return None
    if arguments[1] == "--version" or arguments[1] == "-v":
        print(constants.APP_VERSION)
        return None
    parameters = dict()
    i: int = 1
    while i < len(arguments):
        currentargument = arguments[i]
        if currentargument == "--project" or currentargument == "-p":
            if "project" in parameters.keys():
                print("Error: Provided multiple projects", file=sys.stderr)
                return None
            i += 1
            name = arguments[i]
            if len(Project.select().where(Project.name == name)) == 1:
                parameters["project"] = name
            else:
                print("Error: Invalid project name", file=sys.stderr)
                return None
        elif currentargument == "--group" or currentargument == "-g":
            if "group" in parameters.keys():
                print("Error: Provided multiple groups", file=sys.stderr)
                return None
            if not "project" in parameters.keys():
                print("Error: Project not provided", file=sys.stderr)
                return None
            i += 1
            name = arguments[i]
            project = Project.select().where(Project.name == name).get()
            if len(Group.select().where((Group.name == name) & (Group.project == project.id))) == 1:
                parameters["project"] = name
            else:
                print("Error: Invalid group name", file=sys.stderr)
                return None
        elif currentargument == "--profile":
            if "profile" in parameters.keys():
                print("Error: Provided multiple profiles", file=sys.stderr)
                return None
            i += 1
            name = arguments[i]
            if len(Profile.select().where(Profile.name == name)) == 1:
                parameters["profile"] = name
            else:
                print("Error: Invalid profile name", file=sys.stderr)
                return None
        elif currentargument == "--full" or currentargument == "-f":
            if "type" in parameters.keys():
                print("Error: Provided multiple types of screenshots", file=sys.stderr)
                return None
            parameters["type"] = "full"
        elif currentargument == "--area" or currentargument == "-a":
            if "type" in parameters.keys():
                print("Error: Provided multiple types of screenshots", file=sys.stderr)
                return None
            parameters["type"] = "area"
        elif currentargument == "--custom":
            if "type" in parameters.keys():
                print("Error: Provided multiple types of screenshots", file=sys.stderr)
                return None
            i += 1
            name = arguments[i]
            profile = Profile.select().where(Profile.name == parameters["profile"])
            if len(profile) == 1:
                profile = profile.get()
                found = False
                for area in profile.getconfig("areas"):
                    if area["name"] == name:
                        found = True
                        parameters["custom"] = area["bbox"]
                        break
                if not found:
                    print("Error: Provided invalid area name", file=sys.stderr)
                    return None
                parameters["type"] = "custom"
        i += 1
    if not ("project" in parameters.keys() or "profile" in parameters.keys()):
        print("Error: Project or profile not provided", file=sys.stderr)
        return None
    if not "type" in parameters.keys():
        print("Error: Type of screenshot not provided", file=sys.stderr)
        return None
    return parameters

if __name__ == '__main__':
    config: Configuration = Configuration()
    config.initconfigs()
    dbdata: DatabaseData = DatabaseData(config)
    parameters = parsearguments()
    if parameters is None:
        sys.exit(0)
    project: Project
    group: Group
    profile: Profile
    if "project" in parameters.keys():
        project = Project.select().where(Project.name == parameters["project"]).get()
        if "group" in parameters.keys():
            group = Group.select().where((Group.name == parameters["group"]) & (Group.project == project.id)).get()
        else:
            group = Group.select().where(Group.project == project.id).first()
    else:
        profile = Profile.select().where(Profile.name == parameters["profile"]).get()
        prjct = profile.getconfig("project")
        if prjct is None:
            print("Error: Project undefined in profile", file=sys.stderr)
            sys.exit(0)
        else:
            found = Project.select().where(Project.name == prjct)
            if len(found) == 1:
                project = found.get()
            else:
                print("Error: Invalid project defined in profile", file=sys.stderr)
                sys.exit(0)
        grp = profile.getconfig("group")
        if grp is None:
            group = Group.select().where(Group.project == profile.id).first()
        else:
            foundgroup = Group.select().where((Group.project == project.id) & (Group.name == grp))
            if len(foundgroup) == 1:
                group = foundgroup.get()
            else:
                print("Error: Invalid group defined in profile", file=sys.stderr)
                sys.exit(0)
    screenshoter = Screenshoter(config, project, group, dbdata)
    if parameters["type"] == "full":
        screenshoter.takefullscreenscreenshot()
    elif parameters["type"] == "area":
        selectedarea = config.getconfig("general.selectedarea")
        sarea = []
        for point in selectedarea.split("x"):
            sarea.append(int(point))
        screenshoter.takeareascreenshot(sarea)
    elif parameters["type"] == "custom":
        if parameters["custom"] == "":
            print("Error: Invalid area", file=sys.stderr)
        else:
            sarea = []
            for point in parameters["custom"].split("x"):
                sarea.append(int(point))
            screenshoter.takeareascreenshot(tuple(sarea))
