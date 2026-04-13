import copy
import json
import os
from datetime import datetime
from math import sqrt
from typing import Any

from PIL import ImageDraw, ImageFont
from PySide6.QtCore import QByteArray
from peewee import CharField, IntegerField, ForeignKeyField, TextField, Model, SqliteDatabase
from playhouse.sqlite_ext import JSONField, AutoIncrementField
import pytesseract
from PIL import Image
from os import path
from enum import Enum
from DataModules.Constants import DB_FILE_PATH


class AnnotationType(Enum):
    """Enum that defines types of annotation tools"""
    LINE = 1
    SQUARE = 2
    CIRCLE = 3
    TEXT = 4

class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(DB_FILE_PATH)

class Project(BaseModel):
    id = AutoIncrementField()
    name = CharField()
    description = CharField()
    archived = IntegerField()

class Group(BaseModel):
    id = AutoIncrementField()
    name = CharField()
    project = ForeignKeyField(Project)
    color = CharField()

class Profile(BaseModel):
    id = AutoIncrementField()
    name = CharField()
    configuration = JSONField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__config: dict = json.loads(self.configuration)

    def getconfig(self, name: str) -> Any | None:
        """Gets defined profile configuration

        :param name: name of requested configuration
        :returns: found configuration or ``None``
        """
        if name in self.__config.keys():
            return self.__config[name]
        else:
            return None

    def setconfig(self, name: str, config: Any):
        """Sets specified configuration

        Configuration is set only in memory - need to run ``saveconfig()`` to add it to database

        :param name: name of specified configuration
        :param config: Something to be set to config
        """
        self.__config[name] = config

    def saveconfig(self):
        """Saves configuration to database"""
        self.configuration = json.dumps(self.__config)
        self.save()

class Screenshot(BaseModel):
    name = CharField()
    annotation = JSONField()
    notes = TextField()
    imagetext = TextField()
    project = ForeignKeyField(Project)
    group = ForeignKeyField(Group)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__sessionannotation: list = []
        self.__sessionpointer: int = -1
        self.__image = None
        self.__annotatedImage: Image.Image | None = None

    def __renderline(self, data: dict):
        start = data["start"]
        end = data["end"]
        color = data["color"]
        size = data["size"]
        draw = ImageDraw.Draw(self.__annotatedImage)
        draw.line(list(start) + list(end), fill=color, width=size)

    def __rendersquare(self, data: dict):
        start = data["start"]
        end = data["end"]
        color = data["color"]
        size = data["size"]
        draw = ImageDraw.Draw(self.__annotatedImage)
        if data["fill"]:
            draw.rectangle(list(start) + list(end), fill=color, width=size)
        else:
            draw.rectangle(list(start) + list(end), outline=color, width=size)

    def __rendercircle(self, data: dict):
        start = data["start"]
        end = data["end"]
        color = data["color"]
        size = data["size"]
        draw = ImageDraw.Draw(self.__annotatedImage)
        radius = sqrt(pow(start[0] - end[0], 2) + pow(start[1] - end[1], 2))/2
        if data["fill"]:
            draw.circle(((start[0] + end[0])/2, (start[1] + end[1])/2), fill=color, width=size, radius=radius)
        else:
            draw.circle(((start[0] + end[0]) / 2, (start[1] + end[1]) / 2), outline=color, width=size, radius=radius)

    def __rendertext(self, data: dict):
        start = data["start"]
        color = data["color"]
        size = data["size"]
        text = data["text"]
        font = ImageFont.load_default(size * 2)
        draw = ImageDraw.Draw(self.__annotatedImage)
        draw.text(start, text, color, font)

    def __renderannotation(self, onlylast = False):
        if self.__annotatedImage is None or not onlylast:
            self.__annotatedImage = copy.deepcopy(self.getimage())
        if onlylast:
            if len(self.__sessionannotation) != 0:
                data = self.__sessionannotation[-1]
                if data["type"] == "line":
                    self.__renderline(data)
                elif data["type"] == "square":
                    self.__rendersquare(data)
                elif data["type"] == "circle":
                    self.__rendercircle(data)
                elif data["type"] == "text":
                    self.__rendertext(data)
        else:
            if len(self.annotation) < 2:
                return
            annotations = json.loads(self.annotation)
            for annotation in annotations[0]:
                if annotation["type"] == "line":
                    self.__renderline(annotation)
                elif annotation["type"] == "square":
                    self.__rendersquare(annotation)
                elif annotation["type"] == "circle":
                    self.__rendercircle(annotation)
                elif annotation["type"] == "text":
                    self.__rendertext(annotation)
            if self.__sessionpointer < 0: return
            for i in range(self.__sessionpointer):
                annotation = self.__sessionannotation[i]
                if annotation["type"] == "line":
                    self.__renderline(annotation)
                elif annotation["type"] == "square":
                    self.__rendersquare(annotation)
                elif annotation["type"] == "circle":
                    self.__rendercircle(annotation)
                elif annotation["type"] == "text":
                    self.__rendertext(annotation)

    def getfilename(self) -> str:
        """Gets filename with extension"""
        return str(self.name) + ".jpeg"

    def loadimage(self) -> bool:
        """If image is not loaded, loads image

        :returns: ``True`` if image exists, else ``False``
        """
        location = path.join(path.join(path.join(path.expanduser("~"), "Documents"), "yasuwo"), "screenshots")
        if not path.exists(path.join(location, self.getfilename())):
            return False
        if self.__image is None:
            self.__image = Image.open(path.join(location, self.getfilename()))
        return True

    def getimage(self) -> Image.Image:
        """Gets image and if it is not loaded, loads image

        :returns: ``Image`` object from Pillow library
        """
        if self.__image is None:
            self.loadimage()
        return self.__image

    def getannotatedimage(self) -> Image.Image:
        """Gets annotated image with session annotations

        :returns: ``Image`` object from Pillow library with applied annotations
        """
        if self.__annotatedImage is None:
            self.__annotatedImage = copy.deepcopy(self.getimage())
            self.__renderannotation()
        return self.__annotatedImage

    def exportannotatedimage(self, pathtosave: str):
        """Saves annotated image to specified location

        :param pathtosave: location where annotated image is exported
        """
        if self.__annotatedImage is not None:
            self.__annotatedImage.save(pathtosave, format="JPEG")

    def addannotation(self, typeof: AnnotationType, parameters: dict):
        """Adds annotation to image

        :param typeof: Type of annotation
        :param parameters: ``dict`` with annotation parameters
        expected keys: start = (x,y), end = (x,y), color, size
        """
        while self.__sessionpointer + 1 < len(self.__sessionannotation):
            self.__sessionannotation.pop(-1)
        self.__sessionpointer += 1
        data = dict(parameters)
        if typeof is AnnotationType.LINE:
            data["type"] = "line"
        elif typeof is AnnotationType.SQUARE:
            data["type"] = "square"
        elif typeof is AnnotationType.CIRCLE:
            data["type"] = "circle"
        elif typeof is AnnotationType.TEXT:
            data["type"] = "text"
        self.__sessionannotation.append(data)
        self.__renderannotation(onlylast=True)

    def undoannotation(self):
        """Undoes image annotation"""
        if -1 < self.__sessionpointer:
            self.__sessionpointer -= 1
            self.__renderannotation(onlylast=False)

    def redoannotation(self):
        """Redoes image annotation"""
        if self.__sessionpointer < len(self.__sessionannotation) - 1:
            self.__sessionpointer += 1
            self.__renderannotation(onlylast=True)

    def saveannotation(self):
        """Adds session annotations to annotation"""
        tempanno = list()
        if len(self.annotation) > 2:
            tempanno = json.loads(self.annotation)
        tempanno.append(self.__sessionannotation)
        self.annotation = json.dumps(tempanno)
        self.__sessionannotation.clear()
        self.__sessionpointer = -1
        self.save()

    def clearannotation(self):
        """Clears session annotations"""
        self.__sessionpointer = -1
        self.__sessionannotation.clear()
        self.__renderannotation(onlylast=False)

    def getnotes(self) -> str:
        """Gets notes

        :returns: ``str`` with notes text
        """
        return str(self.notes)

    def setnotes(self, text: str):
        """Sets notes to text

        :param text: ``str`` with notes text
        """
        self.notes = text

    def getdatetime(self) -> datetime:
        """Returns datetime of screenshot creation"""
        datetimetext = str(self.name).replace("Screenshot_", "").replace("_", " ")
        created = datetime.strptime(datetimetext, "%Y-%m-%d %H:%M:%S.%f")
        return created

    def getimagetext(self) -> str:
        """Gets text from image

        :returns: ``str`` with text in image
        """
        if self.imagetext is None:
            return ""
        return self.imagetext

    def getimagepdf(self) -> QByteArray | None:
        """Creates and returns PDF representation of the image

        :returns: ``QByteArray`` with PDF bites inside if image is loaded
        """
        location = path.join(path.join(path.join(path.expanduser("~"), "Documents"), "yasuwo"), "screenshots")
        pdf = pytesseract.image_to_pdf_or_hocr(path.join(location, self.getfilename()), extension="pdf")
        return QByteArray(pdf)

    def analyzetext(self, lang: str = "eng"):
        """Analyzes text from the image

        :param lang: ``str`` with language used for ocr
        """
        location = path.join(path.join(path.join(path.expanduser("~"), "Documents"), "yasuwo"), "screenshots")
        if not (self.imagetext is None or self.imagetext == ""): return
        if path.isfile(path.join(location, self.getfilename())):
            text = pytesseract.image_to_string(path.join(location, self.getfilename()), lang=lang)
            self.imagetext = text
            self.save()

    def deleteimage(self):
        """Deletes image file and database row"""
        location = path.join(path.join(path.join(path.join(path.expanduser("~"), "Documents"), "yasuwo"), "screenshots"), self.getfilename())
        if path.isfile(location):
            os.remove(location)
        self.delete_instance()