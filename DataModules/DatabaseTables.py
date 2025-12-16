from peewee import CharField, IntegerField, ForeignKeyField, TextField, Model
from playhouse.sqlite_ext import JSONField, AutoIncrementField
from PIL import Image

from DataModules.Configuration import Configuration


class Project(Model):
    id = AutoIncrementField()
    name = CharField()
    description = CharField()
    archived = IntegerField()

class Group(Model):
    id = AutoIncrementField()
    name = CharField()
    profile = ForeignKeyField(Project)
    color = CharField()

class Profile(Model):
    id = AutoIncrementField()
    name = CharField()
    configuration = JSONField()

class Screenshot(Model):
    name = CharField()
    annotation = JSONField()
    notes = TextField()
    imagetext = JSONField()
    project = ForeignKeyField(Project)
    group = ForeignKeyField(Group)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__sessionannotation: list
        self.__image: Image
        self.__annotatedImage: Image
        self.__config: Configuration

    def getfilename(self) -> str:
        pass

    def loadimage(self) -> bool:
        pass

    def getimage(self) -> Image:
        pass

    def getannotatedimage(self) -> Image:
        pass

    def exportannotatedimage(self):
        pass

    def addannotation(self, type: str, parameters: dict):
        pass

    def undoannotation(self):
        pass

    def redoannotation(self):
        pass

    def saveannotation(self):
        pass

    def getnotes(self) -> str:
        pass

    def setnotes(self, text: str):
        pass

    def gettextbox(self) -> list:
        pass

    def getimagetext(self) -> str:
        pass

    def analyzetext(self):
        pass