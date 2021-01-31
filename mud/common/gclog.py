# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import gc, marshal, cPickle
from types import InstanceType

from twisted.python import log

PREVD = {}


def gc_check(verbose=False):
    global PREVD
    
    log.msg('Number collected: %s' % gc.collect())
    log.msg('Length of garbage: %s' % len(gc.garbage))
    O = gc.get_objects()
    log.msg('Number of objects: %s' % len(O))
    D = {}
    L = {}
    M = {}
    P = {}
    for o in O:
        t = type(o)
        if t is InstanceType:
            name = '<class %s>' % o.__class__.__name__
            if not D.has_key(name): D[name] = 1
            else: D[name] += 1
        else:
            name = t.__name__
            if not D.has_key(name): D[name] = 1
            else: D[name] += 1
        try:
            L[name] = L.get(name,0)+len(o)
        except:
            pass
        try:
            if verbose == True:
                M[name] = M.get(name,0)+len(marshal.dumps(o))
        except:
            pass
        try:
            if verbose == True:
                P[name] = P.get(name,0)+len(cPickle.dumps(o))
        except:
            pass
    log.msg('Objects:')
    log.msg('    %-30s %10s %10s %10s %10s' % ("Class Name:", "Count", 
    "List Len", "Mshl Size", "Pick Size"))
    for k in sorted(D.iterkeys()):
        try:
            if PREVD[k] >= D[k]:
                continue
        except:
            pass
        
        log.msg('    %-30s: %10s %10s %10s %10s' % (k, D[k], 
    L.get(k,'?'), M.get(k,'?'), P.get(k,'?')))
    
    PREVD = D
    
