# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import re

SPECIAL_CHAR = re.compile(r'[.;:,\'/\\]')

def GetTWikiName(name):
    if not name:
        return ""
    # remove special characters
    name = SPECIAL_CHAR.sub('',name)
    name = ''.join(n[0].upper()+n[1:] for n in name.split(" ") if n)
    
    return name
