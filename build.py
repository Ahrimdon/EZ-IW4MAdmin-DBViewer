import os
import PyInstaller.__main__
from distutils.sysconfig import get_python_lib

site_packages_path = get_python_lib()

NAME = "IW4MAdmin_DB_Parser"
SCRIPT = "combine_db.py"

PyInstaller.__main__.run([
    "{}".format(SCRIPT),
    '--name', f"{NAME}",
    "--noconfirm",
    "--onefile",
    "--windowed",
])

# create symbolic hardlink to main directory
if os.path.exists("combine_db.exe"):
    os.remove("combine_db.exe")
os.link('dist/IW4MAdmin_DB_Parser.exe', 'IW4MAdmin_DB_Parser.exe')