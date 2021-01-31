# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.tgepython.console import *
from twisted.internet import reactor



def ReactorTick():
    if reactor.running:
        reactor.runUntilCurrent()
        reactor.doIteration(0)


def ReactorStart():
    reactor.startRunning()


def ReactorStop():
    if reactor.running:
        reactor.stop()
    while reactor.running:
        ReactorTick()



TGEExport(ReactorTick,"Py","ReactorTick","desc",1,1)
TGEExport(ReactorStart,"Py","ReactorStart","desc",1,1)
TGEExport(ReactorStop,"Py","ReactorStop","desc",1,1)
