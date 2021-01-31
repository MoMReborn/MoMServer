# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from setuptools import setup
import os
import shutil
import sys


OUTPUT_FOLDER = './GMTool'


if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)


if os.path.exists('./build'):
    shutil.rmtree('./build')


sys.path.append(os.getcwd())


setup(
    app = ['./mud/gmtool/gmtool.py'],
    options = {'py2app' : {
        'iconfile' : './packaging/MinionsOfMirth.icns',
        'includes' : ['mud.gamesettings'],
        'packages' : ['encodings'],
        'compressed' : True,
        'argv_emulation' : True,
        'dist_dir' : OUTPUT_FOLDER,
    }},
    setup_requires = ['py2app'],
)
