# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from distutils.core import setup
import py2exe

#setup(windows=[{"script":"mom.py","icon_resources": [(1, "packaging/eye.ico")]}],
#      options = {"py2exe": {"packages": ["encodings"],"dist_dir":"./dist/MinionsOfMirth" }},
#) 
zipfile = None
setup(zipfile = None, console=[{"script":"Genesis.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"dist_dir":"./dist/Genesis", "excludes":["genesis"], "packages": ["encodings"]}}
) 