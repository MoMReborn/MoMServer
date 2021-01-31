# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

class ContentInfo(Persistent):
    #all content tables should have an expansion tag, so we can mark where they come from
    #with version #, so we can also make upgrades/patches easier
    source = StringCol()
    version = StringCol()
    copyright = StringCol()