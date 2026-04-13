#nuitka-project: --mode=standalone
#nuitka-project: --enable-plugin=pyside6
#nuitka-project: --main=yasuwo.py
#nuitka-project: --main=yasuwo-cli.py

import sys
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication, QStyleFactory
from DataModules.DatabaseData import DatabaseData
from GraphicalModules.MainWindow import MainWindow
from GraphicalModules.CheckWindow import CheckWindow
from DataModules.Configuration import Configuration
from os import path


if __name__ == "__main__":
    config: Configuration = Configuration()
    dbdata: DatabaseData = DatabaseData(config)

    app = QApplication(sys.argv)
    startupwindow = CheckWindow(config, dbdata)
    if config.getconfig("general.theme") != "system":
        app.setStyle(QStyleFactory.create(config.getconfig("general.theme")))

    translator = QTranslator()
    if translator.load(path.join(path.curdir, "Languages", f"yasuwo-{config.getconfig("general.language")}.qm")):
        app.installTranslator(translator)

    window = MainWindow(config, dbdata)
    window.show()

    sys.exit(app.exec())