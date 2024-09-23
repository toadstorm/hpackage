hpackage
======

A utility for creating easy Houdini package installers.

HPackage uses PySide2 to create a simple, customizable interface to help users install Houdini package files without getting bogged down in JSON syntax or confusing file locations. 

## Usage
**Note:** To keep executable sizes as small as possible, it's *highly* recommended that you run HPackage in a virtual environment and only include the Python libraries you absolutely need (as defined by `requirements.txt`).

HPackage will automatically create a named JSON package file that adds your package's root directory to `HOUDINI_PATH` and copy it to any user-selected Houdini configuration. If a `[packagename].JSON` file already exists in the package's root directory, `HPackage` will use that package as a template instead and modify path-related variables as specified in `settings.py`.  

HPackage is intended to be used in one of two ways:

### Option 1: Single self-contained executable
HPackage can embed your Houdini package files into the same executable that comprises the UI for simplicity. The files will be extracted to a location chosen by the user at the time of installation.

To embed the payload, edit `settings.py` and provide the root path of your package as the `PAYLOAD` variable.

### Option 2: Sidecar executable
HPackage can also be used as a sidecar file alongside your existing package. Users can still use the executable, placed in the package's root folder, to install the package as normal, or experienced TDs can install by configuring a JSON file the old-fashioned way.

To use the installer as a sidecar, simply leave `PAYLOAD` blank in `settings.py`.

## Creating the executable
After configuring `settings.py`, run `hpackagemaker.py`. PyInstaller will create "build" and "dist" directories in the `[package_root]/hpackage` directory, or in whatever directory you specify with the `LOCATION` variable in `settings.py`.

## Notice:
This software is provided AS-IS, with absolutely no warranty of any kind, express or otherwise. We disclaim any liability for damages resulting from using this software.
