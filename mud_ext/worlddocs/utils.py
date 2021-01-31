# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: mud\worlddocs\utils.pyo
# Compiled at: 2011-10-22 17:42:27
import re
SPECIAL_CHAR = re.compile("[.;:,\\'/\\\\]")

def GetTWikiName(name):
    if not name:
        return ''
    name = SPECIAL_CHAR.sub('', name)
    name = ('').join(n[0].upper() + n[1:] for n in name.split(' ') if n)
    return name