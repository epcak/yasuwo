from os import path

APP_VERSION = "2026.0.0a"
APP_DATA_PATH = path.join(path.join(path.expanduser("~"), "Documents"), "yasuwo")
DB_FILE_PATH = path.join(APP_DATA_PATH, "yasuwo.db")
SCREENSHOTS_PATH = path.join(APP_DATA_PATH, "screenshots")
THUMBNAIL_SIZE = 300