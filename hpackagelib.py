import os
import sys
import json
import re
import settings
import shutil
import logging
from pathlib import Path

#TODO: safeguard against installing to existing houdini config or install directories

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s -- %(levelname)s: %(message)s', level=logging.DEBUG, filename=os.path.join(os.path.expanduser("~"), "hpackage.log"), filemode="w", datefmt="%Y/%m/%d %H:%M:%S")

# insane windows things to fetch user's My Documents folder. this isn't always the same as the home folder!!
CSIDL_PERSONAL = 5       # My Documents
SHGFP_TYPE_CURRENT = 0   # Get current, not default value

# regex for parsing houdini major/minor versions from home folders
HOUDINI_VERSION_REGEX = r"(?P<major>[\d]{1,2})\.(?P<minor>[\d]{1,2})"

def get_windows_docs_path():
    import ctypes.wintypes
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value


def get_windows_houdini_paths():
    """
    Return all detected Houdini configuration paths on Windows.
    """
    root = get_windows_docs_path()
    logging.debug("Windows home path: {}".format(root))
    out_dirs = list()
    if os.path.exists(root):
        houdini_dirs = [f for f in os.listdir(root) if f.startswith("houdini")]
        if houdini_dirs:
            for f in houdini_dirs:
                if settings.SUPPORTED_VERSIONS:
                    logging.debug("Testing Houdini configuration path: {}".format(f))
                    # make sure this detected directory fits one of these versions.
                    match = re.match(HOUDINI_VERSION_REGEX, f)
                    version = match.group("major") + "." + match.group("minor")
                    logging.debug("Version parsed: {}".format(version))
                    if version not in settings.SUPPORTED_VERSIONS:
                        logging.debug("\tVersion not compatible.")
                        continue
                full_path = os.path.join(root, f)
                if os.path.isdir(full_path):
                    out_dirs.append(full_path.replace("\\", "/"))
    logging.debug("Houdini configurations found: {}".format(out_dirs))
    return out_dirs


def get_macos_houdini_paths():
    """
    Return all detected Houdini configuration paths on Mac OS.
    """
    home = os.path.expanduser("~/Library/Preferences/Houdini")
    logging.debug("Mac OS home path: {}".format(home))
    out_dirs = list()
    if os.path.exists(home):
        houdini_dirs = [f for f in os.listdir(home) if re.match(HOUDINI_VERSION_REGEX, f)]
        if houdini_dirs:
            for f in houdini_dirs:
                if settings.SUPPORTED_VERSIONS:
                    logging.debug("Testing Houdini configuration path: {}".format(f))
                    # make sure this detected directory fits one of these versions.
                    match = re.match(HOUDINI_VERSION_REGEX, f)
                    version = match.group("major") + "." + match.group("minor")
                    logging.debug("Version parsed: {}".format(version))
                    if version not in settings.SUPPORTED_VERSIONS:
                        logging.debug("\tVersion not compatible.")
                        continue
                full_path = os.path.join(home, f)
                if os.path.isdir(full_path):
                    out_dirs.append(full_path)
    logging.debug("Houdini configurations found: {}".format(out_dirs))
    return out_dirs


def get_linux_houdini_paths():
    """
    Return all detected Houdini configuration paths on Linux.
    """
    home = os.path.expanduser("~")
    logging.debug("Linux home path: {}".format(home))
    out_dirs = list()
    houdini_dirs = [f for f in os.listdir(home) if f.startswith("houdini")]
    if houdini_dirs:
        for f in houdini_dirs:
            if settings.SUPPORTED_VERSIONS:
                # make sure this detected directory fits one of these versions.
                logging.debug("Testing Houdini configuration path: {}".format(f))
                match = re.match(HOUDINI_VERSION_REGEX, f)
                version = match.group("major") + "." + match.group("minor")
                logging.debug("Version parsed: {}".format(version))
                if version not in settings.SUPPORTED_VERSIONS:
                    continue
            full_path = os.path.join(home, f)
            if os.path.isdir(full_path):
                out_dirs.append(full_path)
    logging.debug("Houdini configurations found: {}".format(out_dirs))
    return out_dirs


def get_houdini_prefs_paths():
    if sys.platform == "win32":
        return get_windows_houdini_paths()
    elif sys.platform.lower() == "darwin":
        return get_macos_houdini_paths()
    else:
        return get_linux_houdini_paths()


def find_payload_path():
    """
    Locate the payload. If this is a sidecar file, we can just look in the same directory.
    If this has an embedded payload, we can get it from /payload/.
    """
    try:
        payload_path = os.path.join(sys._MEIPASS, 'payload')
        return payload_path
    except Exception:
        pass
    this_path = os.path.abspath(".")
    logging.debug("Finding payload starting from path: {}".format(this_path))
    iter = 50
    while iter > 0:
        prev_path = this_path
        test = os.path.join(this_path, "otls")
        logging.debug("Testing path: {}".format(test))
        if os.path.exists(test):
            logging.info("Found payload path: {}".format(os.path.dirname(test)))
            return os.path.dirname(test)
        this_path = os.path.dirname(this_path)
        if prev_path == this_path:
            return None
        iter -= 1
    return None


def find_package_path():
    this_path = os.path.abspath(".")
    logging.debug("Finding package JSON starting from path: {}".format(this_path))
    iter = 50
    while iter > 0:
        prev_path = this_path
        test = os.path.join(this_path, settings.NAME) + ".json"
        logging.debug("Testing path: {}".format(test))
        if os.path.exists(test):
            logging.info("Found package path: {}".format(test))
            return test
        this_path = os.path.dirname(this_path)
        if prev_path == this_path:
            return None
        iter -= 1
    return None


def is_valid_install_path(testpath):
    """
    If this is a Houdini installation path or a Houdini configuration path, we don't want to install there.
    """
    config_paths = get_houdini_prefs_paths()
    # check detected configuration paths.
    for test in config_paths:
        root = Path(test)
        this = Path(testpath)
        if root in this.parents or root == this:
            logging.warning("Path {} appears to be within a Houdini preferences path!".format(testpath))
            return False
    # check if this is maybe a Houdini installation.
    if 'Side Effects Software' in testpath.split("/"):
        logging.warning("Path {} appears to be in a Houdini installation directory!".format(testpath))
        return False

    return True

def get_resource(relative_path):
    """
    Get the relative path of a resource. This path can change if PyInstaller is used to create a single file.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def install_package(path_list, package=None, destination=None, payload=None, debug=False):
    """
    Configure the specified package file and copy it to the package path
    in each directory in path_list.
    :param path_list: the list of Houdini pref paths to install to.
    :param package: the JSON file to configure, if one exists.
    :param destination: the location to copy files to. if not specified, uses the existing package path without copying.
    :param payload: the location of the source files. this is typically the same directory or a parent of this script.
    :param debug: doesn't actually save or copy any files and prints a dry run instead.
    """
    data = None
    install_path = None

    if destination:
        install_path = destination
        # copy the contents of the package to this destination.
        if payload is None:
            payload = find_payload_path()

        if not os.path.samefile(payload, destination):
            logging.info("Copying payload at {} to install path: {}".format(payload, destination))
            if not debug:

                shutil.copytree(payload, install_path, dirs_exist_ok=True)
        else:
            logging.info("Using existing payload location as package install path: {}".format(payload))
    else:
        if package:
            if os.path.exists(package):
                install_path = os.path.dirname(package)
        if not install_path and not package:
            # without an install path or a package defined, we have no idea what we're doing
            logging.error("No package path or installation path is defined! Aborting.")
            return
    # handle path-based vars (for HOUDINI_PATH or other generic env stuff)
    install_path = install_path.replace("\\", "/")
    try:
        with open(package, 'r') as f:
            data = json.load(f)
    except:
        # create default name for package file

        data = dict()
        env = []
        data["env"] = env
        data["hpath"] = list()
    # conform path to hpath for forwards compatibility.
    if "path" in data:
        h = data["path"]
        data["hpath"] = h
        data.pop("path")

    found_path_var = False
    if settings.PATH_VARS:
        for var in settings.PATH_VARS:
            if data["env"]:
                if var in data["env"][0].keys():
                    data["env"][0][var] = install_path
                    found_path_var = True
            else:
                d = dict()
                d[var] = install_path
                data["env"].append(d)
                if type(data["hpath"]) is str:
                    data["hpath"] = "${}".format(var)
                else:
                    data["hpath"].append("${}".format(var))
                found_path_var = True
    if not found_path_var:
        data["hpath"] = install_path

    # handle any other specified vars in the settings file
    if settings.OTHER_VARS.keys():
        for k, v in settings.OTHER_VARS.items():
            d = dict()
            d[k] = v
            data["env"].append(d)

    logging.debug("Package contents: {}".format(json.dumps(data, indent=3)))

    for path in path_list:
        # create the package directory and get ready to write the modified JSON file
        # print(path)
        packages_path = os.path.join(path, "packages").replace("\\", "/")
        if not os.path.exists(packages_path):
            logging.info("Created Houdini packages directory: {}".format(packages_path))
            os.makedirs(packages_path)
        else:
            logging.info("Writing package to existing Houdini packages directory: {}".format(packages_path))
        out_path = os.path.join(packages_path, "{}.json".format(settings.NAME)).replace("\\", "/")
        # print(json.dumps(data, indent=3))

        if not debug:
            with open(out_path, 'w') as f:
                logging.info("Wrote Houdini package file: {}".format(out_path))
                json.dump(data, f, indent=3)
        else:
            logging.debug("Package file would be written to: {}".format(out_path))





# install_mops(["D:/Documents/houdini18.5"], "D:/Projects/VFX/MOPS/MOPs.json")