# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from twisted.cred import checkers
from twisted.internet import reactor,defer
from twisted.python import components, failure, log
from twisted.web import server, resource
from twisted.web.woven import simpleguard
from twisted.cred.credentials import IUsernamePassword,IUsernameHashedPassword
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred import error, credentials,checkers
from sqlobject import *
from zope import interface
from mud.masterserver.masterdb import *

WINDOWS_DOWNLOAD = "http://www.prairiegames.com/alphabinaries/MoMBetaInstaller.exe"
MAC_DOWNLOAD = "http://www.prairiegames.com/alphabinaries/MoMBeta_OSX.tar.gz"

USERNAME = "tester"
PASSWORD = "FireGiant55"

DOWNLOADPAGE = """
<b><br>Here is the current download information for the Minions of Mirth Beta:</br></br></b>
    
<b>Windows Installer</b>: <a href="%s">%s</a>
<br><br>
<b>OSX Installer</b>: <a href="%s">%s</a><br><br>

<b>Username:</b> %s<br>
<b>Password:</b> %s<br>

"""%(WINDOWS_DOWNLOAD,WINDOWS_DOWNLOAD,MAC_DOWNLOAD,MAC_DOWNLOAD,USERNAME,PASSWORD)

USERPASSFORM = """
<H1 align="center">Minions of Mirth Beta Download Information</H1>

<H3 align="left">Please enter your username and password.</H3>

<FORM action="perspective-init" method="post">
    <P>
    <LABEL for="username">Username: </LABEL>
              <INPUT type="text" name="username"><BR>
    <LABEL for="password">Password: </LABEL>
              <INPUT type="password" name="password"><BR><BR>

    <INPUT type="submit" value="Login">
    </P>
 </FORM>
"""

class SimpleResource(resource.Resource):

    def getChild(self, path, request):
        return self

    def render_GET(self, request):
        auth = request.getComponent(simpleguard.Authenticated)
        if auth:
            return DOWNLOADPAGE
        else:
            return USERPASSFORM
            


class MyChecker:

    interface.implements(ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword)


    def _cbPasswordMatch(self, matched, username):
        if matched:
            return username
        else:
            return failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        
        try:
            acct = Account.byPublicName(credentials.username)
        except SQLObjectNotFound:
            return defer.fail(error.UnauthorizedLogin())
        
        if not acct.hasProduct("MOM"):
            return defer.fail(error.UnauthorizedLogin())
            

        return defer.maybeDeferred(
            credentials.checkPassword,
            acct.password).addCallback(
            self._cbPasswordMatch, str(credentials.username))

def MakeWebServer():

    checker = MyChecker()
    

    reactor.listenTCP(8080, server.Site(
        simpleguard.guardResource(SimpleResource(), [checker])))
