# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import sys

import zope.interface

from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword
from twisted.application import app,service, strports
from twisted.python import util
from nevow import inevow, rend, loaders, url, tags, appserver, static, guard, athena

from webpages import *

#the stat server

#Richest Player (also by realm)
#Highest Levels Multiclass
#Highest Levels Single Class
#Highest Levels by Class/Race
#Highest Levels by Realm

#strongest, etc

#logs into world and requests stats

#add some stat tracking to world

#most kills, highest level killed

WORLDIP = '72.232.36.210'
WORLDPORT = 2008
STATSERVERPASSWORD = "WHEE"

STATS = {}

#XXX Do this properly
FILTERED_PLAYERS = [
"JRitter","Avannir","magnus","MissL"
]

CACHED = {}

def GotWorldStats(stats,perspective):
    global STATS,CACHED
    STATS = stats
    CACHED = {}
    
    perspective.broker.transport.loseConnection()
    reactor.callLater(60*15,GetWorldStats) #updated every 15 minutes

def GetWorldStatsConnected(perspective):
    perspective.callRemote("StatsAvatar","getStats").addCallbacks(GotWorldStats,GetWorldStatsFailure,(perspective,))
    
def GetWorldStatsFailure(error):
    print error
    
    reactor.callLater(60,GetWorldStats) #try again in one minute

def GetWorldStats():
    
    username="Stats-Stats"
    password=STATSERVERPASSWORD
    
    factory = pb.PBClientFactory()
    reactor.connectTCP(WORLDIP,WORLDPORT,factory)
    #the pb.Root() is a bit of a hack, I don't know how to get host address on server without
    #sending it, and I don't want to take the time to figure it out at the moment
    from md5 import md5
    password = md5(password).digest()

    factory.login(UsernamePassword(username, password),pb.Root()).addCallbacks(GetWorldStatsConnected, GetWorldStatsFailure)
    

import os
class StatSite(rend.Page):
    addSlash = True ## This is a directory-like resource
    docFactory = loaders.htmlstr(TEMPLATE%INDEX_HTML)
    #child_sources = static.File('./mud/statserver/website/', defaultType='text/plain')
    #child_sources.processors['.py'] = Sources
    #child_sources.contentTypes = {}
    #child_cssfile = static.File(os.path.abspath('.')+'/mud/statserver/website/prairiegames.css')
    
    def child_index(self,ctx):
        return TEMPLATE%INDEX_HTML
    
    def child_richestfol(self, ctx):
        r = CACHED.get("richestfol",None)
        if r:
            return r
        rank = 1
        html = """<p class="smallheader">Richest FoL Players</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Platinum</th>
            <th>Gold</th>
            <th>Silver</th>
            <th>Copper</th>
            <th>Tin</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("folrichest",None)
        text = ""
        if highest:
            for playerName,tin,copper,silver,gold,platinum in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                text+=str("""<tr><td>%i. %s</td> <td>%i</td> <td>%i</td> <td>%i</td> <td>%i</td> <td>%i</td> </tr>"""%(rank,playerName,platinum,gold,silver,copper,tin))
                rank+=1
                
        
        r=CACHED["richestfol"]=TEMPLATE%(html%text)
        return r

    def child_richestmod(self, ctx):
        
        r = CACHED.get("richestmod",None)
        if r:
            return r
        
        rank = 1

        html = """<p class="smallheader">Richest MoD Players</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Platinum</th>
            <th>Gold</th>
            <th>Silver</th>
            <th>Copper</th>
            <th>Tin</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("modrichest",None)
        text = ""
        if highest:
            for playerName,tin,copper,silver,gold,platinum in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                text+=str("""<tr><td>%i. %s</td> <td>%i</td> <td>%i</td> <td>%i</td> <td>%i</td> <td>%i</td> </tr>"""%(rank,playerName,platinum,gold,silver,copper,tin))
                rank+=1
                
        
        r=CACHED["richestmod"]=TEMPLATE%(html%text)
        return r


    def child_highestpresence(self, ctx):
        r = CACHED.get("highestpresence",None)
        if r:
            return r

        rank = 1
        html = """<p class="smallheader">Characters by Highest Presence</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Presence</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            <th>Realm</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("presence",None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm,presence in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                if realm == 1:
                    realm = "FoL"
                else:
                    realm = "MoD"
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td><td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s</td></tr>"""%(rank,playerName,name,presence,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel,realm))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td><td>%s (%s)</td> <td>%s (%s)</td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,presence,pclassInternal,plevel,sclassInternal,slevel,realm))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td><td>%s (%s)</td> <td></td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,presence,pclassInternal,plevel,realm))
                rank+=1
                
            
        
        r=CACHED["highestpresence"]=TEMPLATE%(html%text)
        return r

        

    def child_highestprimary(self, ctx):
        
        r = CACHED.get("highestprimary",None)
        if r:
            return r

        rank =1
        html = """<p class="smallheader">Characters by Highest Primary Level</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            <th>Realm</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("levels",None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                if realm == 1:
                    realm = "FoL"
                else:
                    realm = "MoD"
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel,realm))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel,realm))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td></td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,realm))
                rank+=1
                
            
        
        r=CACHED["highestprimary"]=TEMPLATE%(html%text)
        return r


    def child_highestcombined(self, ctx):
        
        r = CACHED.get("highestcombined",None)
        if r:
            return r
        rank = 1
        html = """<p class="smallheader">Characters by Highest Combined Level</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Combined</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            <th>Realm</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("totallevels",None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                
                combined = int(plevel)+int(slevel)+int(tlevel)
                if realm == 1:
                    realm = "FoL"
                else:
                    realm = "MoD"
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s</td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel,realm))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td>%s (%s)</td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel,sclassInternal,slevel,realm))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td></td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel,realm))
                rank+=1
            
        r=CACHED["highestcombined"]=TEMPLATE%(html%text)
        return r

        
    
    def highestprimaryrealm(self, ctx,realm):
        if realm == "fol":
            r = "FoL"
        else:
            r= "MoD"
            
        rank = 1
        html = """<p class="smallheader">Characters by Highest Primary Level - %s</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("%slevels"%realm,None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td></td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td></td> <td></td> </tr>"""%(rank,playerName,name,pclassInternal,plevel))
                rank+=1
        
        return TEMPLATE%(html%(r,text))
    
    def child_highestprimaryfol(self, ctx):
        r = CACHED.get("highestprimaryfol",None)
        if r:
            return r
        r=CACHED["highestprimaryfol"]=self.highestprimaryrealm(ctx,"fol")
        return r

    
    def child_highestprimarymod(self, ctx):
        r = CACHED.get("highestprimarymod",None)
        if r:
            return r
        r=CACHED["highestprimarymod"]=self.highestprimaryrealm(ctx,"mod")
        return r

    def highestcombinedrealm(self, ctx,realm):
        if realm == "fol":
            r = "FoL"
        else:
            r= "MoD"

        rank = 1
        html = """<p class="smallheader">Characters by Highest Combined Level - %s</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Combined</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            </tr>
            %s
            </table>
            """
        
        highest = STATS.get("%stotallevels"%realm,None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                
                combined = int(plevel)+int(slevel)+int(tlevel)
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td>%s (%s)</td> <td></td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel,sclassInternal,slevel))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%i</td> <td>%s (%s)</td> <td></td> <td></td></tr>"""%(rank,playerName,name,combined,pclassInternal,plevel))
                rank+=1
            
        
        return TEMPLATE%(html%(r,text))


    def child_highestcombinedfol(self, ctx):
        r = CACHED.get("highestcombinedfol",None)
        if r:
            return r
        r=CACHED["highestcombinedfol"]=self.highestcombinedrealm(ctx,"fol")
        return r


    def child_highestcombinedmod(self, ctx):
        r = CACHED.get("highestcombinedmod",None)
        if r:
            return r
        r=CACHED["highestcombinedmod"]=self.highestcombinedrealm(ctx,"mod")
        return r
    
    
    def highestprimaryclass(self, ctx,klass):            
        html = """<p class="smallheader">%s by Highest Primary Level</p>
            <a href="index">Back</a><br><br>
            
            <table border="1" class="features">
            <tr>
            <th>Player</th>
            <th>Character</th>
            <th>Primary</th>
            <th>Secondary</th>
            <th>Tertiary</th>
            <th>Realm</th>
            </tr>
            %s
            </table>
            """
        
        rank=1
        highest = STATS.get("%slevels"%klass.lower(),None)
        text = ""
        if highest:
            for playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm in highest:
                if playerName in FILTERED_PLAYERS:
                    continue
                
                if realm == 1:
                    realm = "FoL"
                else:
                    realm = "MoD"
                if sclassInternal and tclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s (%s)</td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel,realm))
                elif sclassInternal:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td>%s (%s)</td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,sclassInternal,slevel,realm))
                else:
                    text+=str("""<tr><td>%i. %s</td> <td>%s</td> <td>%s (%s)</td> <td></td> <td></td> <td>%s</td></tr>"""%(rank,playerName,name,pclassInternal,plevel,realm))
                rank+=1
        
        return TEMPLATE%(html%(klass,text))
    
    def child_highestpaladin(self, ctx):
        r = CACHED.get("highestpaladin",None)
        if r:
            return r
        r=CACHED["highestpaladin"]=self.highestprimaryclass(ctx,"Paladin")
        return r
    def child_highestwizard(self, ctx):
        r = CACHED.get("highestwizard",None)
        if r:
            return r
        r=CACHED["highestwizard"]=self.highestprimaryclass(ctx,"Wizard")
        return r
    def child_highestdruid(self, ctx):
        r = CACHED.get("highestdruid",None)
        if r:
            return r
        r=CACHED["highestdruid"]=self.highestprimaryclass(ctx,"Druid")
        return r
    def child_highestnecromancer(self, ctx):
        r = CACHED.get("highestnecromancer",None)
        if r:
            return r
        r=CACHED["highestnecromancer"]=self.highestprimaryclass(ctx,"Necromancer")
        return r
    def child_highesttempest(self, ctx):
        r = CACHED.get("highesttempest",None)
        if r:
            return r
        r=CACHED["highesttempest"]=self.highestprimaryclass(ctx,"Tempest")
        return r
    def child_highestwarrior(self, ctx):
        r = CACHED.get("highestwarrior",None)
        if r:
            return r
        r=CACHED["highestwarrior"]=self.highestprimaryclass(ctx,"Warrior")
        return r
    def child_highestbarbarian(self, ctx):
        r = CACHED.get("highestbarbarian",None)
        if r:
            return r
        r=CACHED["highestbarbarian"]=self.highestprimaryclass(ctx,"Barbarian")
        return r
    def child_highestranger(self, ctx):
        r = CACHED.get("highestranger",None)
        if r:
            return r
        r=CACHED["highestranger"]=self.highestprimaryclass(ctx,"Ranger")
        return r
    def child_highestbard(self, ctx):
        r = CACHED.get("highestbard",None)
        if r:
            return r
        r=CACHED["highestbard"]=self.highestprimaryclass(ctx,"Bard")
        return r
    def child_highestrevealer(self, ctx):
        r = CACHED.get("highestrevealer",None)
        if r:
            return r
        r=CACHED["highestrevealer"]=self.highestprimaryclass(ctx,"Revealer")
        return r
    def child_highestcleric(self, ctx):
        r = CACHED.get("highestcleric",None)
        if r:
            return r
        r=CACHED["highestcleric"]=self.highestprimaryclass(ctx,"Cleric")
        return r
    def child_highestassassin(self, ctx):
        r = CACHED.get("highestassassin",None)
        if r:
            return r
        r=CACHED["highestassassin"]=self.highestprimaryclass(ctx,"Assassin")
        return r
    def child_highestthief(self, ctx):
        r = CACHED.get("highestthief",None)
        if r:
            return r
        r=CACHED["highestthief"]=self.highestprimaryclass(ctx,"Thief")
        return r
    def child_highestshaman(self, ctx):
        r = CACHED.get("highestshaman",None)
        if r:
            return r
        r=CACHED["highestshaman"]=self.highestprimaryclass(ctx,"Shaman")
        return r
    def child_highestmonk(self, ctx):
        r = CACHED.get("highestmonk",None)
        if r:
            return r
        r=CACHED["highestmonk"]=self.highestprimaryclass(ctx,"Monk")
        return r
    def child_highestdoomknight(self, ctx):
        r = CACHED.get("highestdoomknight",None)
        if r:
            return r
        r=CACHED["highestdoomknight"]=self.highestprimaryclass(ctx,"Doom Knight")
        return r


reactor.callLater(0,GetWorldStats)

application = service.Application("StatSite")
strports.service("8000", appserver.NevowSite(StatSite())).setServiceParent(application)
app.startApplication(application,None)
reactor.run()