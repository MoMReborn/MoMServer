import os
import sys
from shutil import copytree, copyfile

from mud_ext.characterserver.createdb import ConvertWorldDBToCharacterDB
from mud_ext.masterserver.createdb import main as CreateMasterDB
from mud.gamesettings import GAMEROOT

MOM_INSTALL_DIR = None
if os.path.exists("%s/MinionsOfMirthUW" % os.getenv('LocalAppData')):
    MOM_INSTALL_DIR = "%s/MinionsOfMirthUW" % os.getenv('LocalAppData')
elif os.path.exists("%s/MinionsOfMirthUW" % os.getenv('ProgramFiles(x86)')):
    MOM_INSTALL_DIR = "%s/MinionsOfMirthUW" % os.getenv('ProgramFiles(x86)')
elif os.path.exists("%s/MinionsOfMirthUW" % os.getenv('ProgramFiles')):
    MOM_INSTALL_DIR = "%s/MinionsOfMirthUW" % os.getenv('ProgramFiles')
for arg in sys.argv:
    if arg.startswith("-mom-install-dir="):
        MOM_INSTALL_DIR = arg[len("-mom-install-dir="):]
        break


def install():
    if os.path.realpath(MOM_INSTALL_DIR) == os.path.realpath(os.getcwd()):
        raise Exception("Should run this from server directory, not mom install dir")

    if not os.path.exists("%s/mud_ext" % os.getcwd()):
        raise Exception("Should run this from server directory")

    print "Copying directories..."
    copytree(os.path.join(MOM_INSTALL_DIR, 'common'), './common')
    copytree(os.path.join(MOM_INSTALL_DIR, GAMEROOT), GAMEROOT)
    copyfile(os.path.join(MOM_INSTALL_DIR, 'main.cs.dso'), './main.cs.dso')

    print "Creating Master Database..."
    CreateMasterDB()

    print "Creating Character Database..."
    ConvertWorldDBToCharacterDB()


if __name__ == '__main__':
    install()
