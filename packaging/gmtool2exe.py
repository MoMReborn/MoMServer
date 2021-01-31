# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from distutils.core import setup
import py2exe
import shutil,string
import sys
import zipfile
import os
import os.path
import getopt
import glob

#python 2.5 change
sys.path.append(os.getcwd())

from mud.world.defines import *

OUTPUT_FOLDER = "gmtool"

if os.path.exists('./build'):
    shutil.rmtree('./build')
    
if os.path.exists('./dist'):
    shutil.rmtree('./dist')


setup(windows=[{"script":".\mud\gmtool\gmtool.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True , "dll_excludes": ["netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
) 

