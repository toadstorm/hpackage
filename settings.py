# the name of the package file you're configuring.
# this should exist in the same path or in a parent path of the payload.
NAME = "MOPs"

# if you want to embed the plugin files into your executable, provide the path here.
# example: PAYLOAD = "D:/Projects/MOPS"
PAYLOAD = ""

# if you want to build to a different location than the location of this file, provide a path here.
# example: OUTPUT = "D:/Projects/MOPS/hpackage"
OUTPUT = ""

# any vars in this list will be set as env vars with the value being the package root path.
# if this list is empty, the package path will be set for the "hpath" key.
# example: PATH_VARS = ["MOPS", "MOPSPLUS"]
PATH_VARS = []

# any other vars to set via the installer.
# this is a dictionary, i.e. OTHER_VARS = {"HOUDINI_PYTHONWARNINGS: "ignore", "load_package_once": true}
OTHER_VARS = {}

# if your package is version-limited, you can whitelist supported major/minor versions here.
# if it's empty, all found versions of houdini will be available for the package install UI.
# example: SUPPORTED_VERSIONS = ["20.5", "20.0", "19.5"]
SUPPORTED_VERSIONS = []

# window title
TITLE = "MOPs Package Installer"

# intro window graphic. leave blank to exclude.
IMAGE = "mops_logo_01.png"

# intro text
INTRO = """Welcome to the MOPs installation wizard."""

# chooser text
CHOOSER = """Please select a list of compatible Houdini versions to install MOPs to."""

# location text
LOCATION = "Please select the location where you want MOPs extracted to. Do not install MOPs directly into a Houdini " \
           "installation or configuration directory!"

# success text
SUCCESS = "MOPs has been successfully installed!"

# if True, the package won't actually copy any files or create/modify any packages
DEBUG = False

# these are currently nonfunctional
CUSTOM_EXCLUDE_LIST = []
WINDOWS_EXCLUDE_LIST = ['opengl32sw.dll', 'Qt5Network.dll', 'Qt5Pdf.dll', 'Qt5Qml.dll', 'Qt5QmlModels.dll', 'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5VirtualKeyboard.dll', 'Qt5WebSockets.dll']

# probably don't change this
LABELWIDTH = 800