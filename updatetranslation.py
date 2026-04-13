if __name__ == "__main__":
    import subprocess
    import platform

    LANG_FILE = "yasuwo-sk.ts"
    comm = f'pyside6-lupdate . ./GraphicalModules/AreaPickerDialogs.py  ./GraphicalModules/CheckWindow.py  ./GraphicalModules/MainWindow.py  ./GraphicalModules/ManageProfilesWindow.py  ./GraphicalModules/ManageProjectsWindow.py  ./GraphicalModules/ScreenshotViewWindow.py  ./GraphicalModules/SearchWindow.py  ./GraphicalModules/SettingsWindow.py -ts ./Languages/{LANG_FILE}'
    if platform.system() == "Windows":
        subprocess.Popen(comm.replace("/", "\\"), shell=True)
    else:
        subprocess.Popen(comm, shell=True)