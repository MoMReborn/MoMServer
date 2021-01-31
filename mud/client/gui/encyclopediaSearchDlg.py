# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from encyclopediaWnd import encyclopediaSearch


def OnEncyclopediaSearchDlgSearch():
    searchvalue = TGEObject("ENCYCLOPEDIA_SEARCH").getValue()
    encyclopediaSearch(searchvalue)


def PyExec():
    TGEExport(OnEncyclopediaSearchDlgSearch,"Py","OnEncyclopediaSearchDlgSearch","desc",1,1)
