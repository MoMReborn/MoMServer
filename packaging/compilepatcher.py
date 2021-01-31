# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import sys
from py_compile import compile


if "2.3DEMO" in sys.argv or "2.4DEMO" in sys.argv: 
    RPG_BUILD_DEMO = True
else:
    RPG_BUILD_DEMO = False

OUTPUT_FOLDER = "testing"
if RPG_BUILD_DEMO:
    OUTPUT_FOLDER = "demo"
 
if "2.3" in sys.argv or "2.3DEMO" in sys.argv: 
    compile("./packaging/patcher.py","../%s/mac/MoMPatcher_Py23.pyc"%OUTPUT_FOLDER)
else:
    compile("./packaging/patcher.py","../%s/mac/MoMPatcher_Py24.pyc"%OUTPUT_FOLDER)
    