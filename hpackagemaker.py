import sys, os
import PyInstaller.__main__ as PI
import hpackagelib
import settings
import platform
import subprocess

#TODO: only include data directory if compiling into single self-installing exe.
#TODO: find a way to generate and patch spec file with DLL exclusion list prior to building
#TODO: exclusion list doesn't seem to do anything at all with onefile enabled?

pkgname = "{}_install".format(settings.NAME)

"""
# HPACKAGE OPTIMIZATION
WINDOWS_EXCLUDE_LIST = ['opengl32sw.dll', 'Qt5Network.dll', 'Qt5Pdf.dll', 'Qt5Qml.dll', 'Qt5QmlModels.dll', 'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5VirtualKeyboard.dll', 'Qt5WebSockets.dll']
keep_list = list()
for (dest, source, kind) in a.binaries:
    if os.path.basename(dest) in WINDOWS_EXCLUDE_LIST:
        continue
    keep_list.append((dest, source, kind))
# a.binaries = keep_list
# END HPACKAGE OPTIMIZATION
"""

def do_package(name=pkgname, path=None, embedpayload=True, onefile=True):
    options = ['hpackage_ui.py', '--windowed', '-y', '--name', name]
    if platform.system() == "Windows":
        sep = ';'
    else:
        sep = ':'
    if embedpayload:
        if settings.PAYLOAD:
            options.extend(['--add-data', '{}{}payload'.format(settings.PAYLOAD, sep)])
    # embed the splash image
    options.extend(['--add-data', '{}{}.'.format(settings.IMAGE, sep)])
    if path:
        options.append("--distpath")
        options.append(path)
    if onefile:
        options.append('--onefile')

    PI.run(options)

if __name__ == "__main__":
    # do_package(*sys.argv[1:])
    subprocess.run(["pyinstaller", "MOPs_install.spec"], env=os.environ)
