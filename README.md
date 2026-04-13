# YASUWO - Screenshot utility with OCR
YASUWO is screenshot utility with OCR image text recognition.
You can set up multiple screenshot areas and manage your screenshots in projects and groups.

**Features**:
- Taking screenshots
- Organizing screenshots to projects and groups
- Multi-platform
- Annotation of screenshots
- Multiple screenshot areas
- Advanced search (including text inside screenshot)
- And many more


## How to use
Complete how to is located in this repo [wiki page](https://github.com/epcak/yasuwo/wiki).

## Installation
YASUWO needs Tesseract for OCR functionality. You can learn how to install Tesseract [here](https://tesseract-ocr.github.io/tessdoc/Installation.html)
You have two options how to run YASUWO, running YASUWO as Python script or downloading prebuild binaries in release tab.
### Running as Python script
Python version 3.11+ is required. It is recommended to install required libraries inside virtual environment (venv).

To install required libraries you can run this command:

`pip install -r requirements.txt`

After that you need to run project initialization:

`pyside6-project build`

To run YASUWO start yasuwo.py:

`python yasuwo.py`

## Building binaries
To create YASUWO as standalone program you need to install nuitka:

`pip install nuitka`

Simplest way to create executables is to run this command:

`nuitka yasuwo.py`

Created program is in yasuwo.dist folder. Copy DefaultTemplates and Languages folder to yasuwo.dist
