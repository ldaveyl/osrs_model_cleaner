# https://github.com/luckychris/install_blender_python_modules
import sys
import subprocess
import os
import platform
import bpy


def isWindows():
    return os.name == 'nt'


def isMacOS():
    return os.name == 'posix' and platform.system() == "Darwin"


def isLinux():
    return os.name == 'posix' and platform.system() == "Linux"


def python_exec():

    if isWindows():
        return os.path.join(sys.prefix, 'bin', 'python.exe')
    elif isMacOS():

        try:
            # 2.92 and older
            path = bpy.app.binary_path_python
        except AttributeError:
            # 2.93 and later
            path = sys.executable
        return os.path.abspath(path)
    elif isLinux():
        return os.path.join(sys.prefix, 'sys.prefix/bin', 'python')
    else:
        print("sorry, still not implemented for ",
              os.name, " - ", platform.system)


def installPackage(packageName):
    python_exe = python_exec()
    try:
        subprocess.call([python_exe, "import ", packageName])
    except:
        # Upgrade pip if not latest version in ensurepip
        subprocess.call([python_exe, "-m", "ensurepip", "--user", "--upgrade"])
        # Install required packages
        subprocess.call([python_exe, "-m", "pip", "install", packageName])
