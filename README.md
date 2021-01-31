# Minions of Mirth - Private Server

Disclaimer: I have nothing to do with Prairie Games. This was produced using their open source TMMOKit and, by my understanding, this respects the terms of the TMMOKit license.

Unfortunately the Minions of Mirth servers were shutdown permanently some years ago. The repo allows you to run a private server for the Minions of Mirth game.

**IMPORTANT:** This project uses code and libraries written at least 10 years ago, there are probably unpatched security issues in those libraries. Exposing a server running this code probably opens you up to remote code execution and other vulnerabilities...
Ideally you'd only run this with people you trust, over a VPN if you wanted to do so remotely.

## Requirements
* Windows install of Minions of Mirth (Run the game and update it)

Note: I'm looking at a Linux install, but it's non-trivial (requires building Torque Game Engine from source)

## Installation
1. Install MoM and update it
2. Install Python 2.7
3. Install wxPython 2.8.x
4. You probably need to install OpenSSL (32bit?): https://slproweb.com/products/Win32OpenSSL.html 
5. Clone (or Download) this repo, make sure the path you choose does not have any spaces
6. From the cloned folder run:
   ```
   C:\Python27\python.exe -m pip install -r requirements.txt
   ```

## Environment Configuration
1. You'll need to set the following environment variables:
   ```
   MOM_INSTALL=%ProgramFiles(x86)%\MinionsOfMirthUW
   PYTHONPATH=C:\Python27\Lib\site-packages;%MOM_INSTALL%;%MOM_INSTALL%\library.zip;
   ```
   Note: change MOM_INSTALL to point to your Minions of Mirth install directory.

2. Run the Install.py script (It will copy a few things from the MoM install):
   ```
   C:\Python27\python.exe .\Install.py
   ```

## Configuring a server
You can ignore this unless you particularly want to modify the server....

You'll want to take a look at:
```
mud_ext/gamesettings.py
mud_ext/server/serversettings.py
projects/mom.cfg
```
and after you've created a world (Using the WorldManager):
```
serverconfig/<WorldName>.py
```

## Running Server
Make sure that you have the environment variables set first. Then run each of these in a separate window:
```
C:\Python27\python.exe .\MasterServer.py gameconfig=mom.cfg
```
```
C:\Python27\python.exe .\GMServer.py gameconfig=mom.cfg
```
```
C:\Python27\python.exe .\CharacterServer.py gameconfig=mom.cfg
```
```
C:\Python27\python.exe .\WorldManager.py gameconfig=mom.cfg
```
The world manager allows you to create new worlds, to create an account start the client and click register

## Exposing the server to the internet
I thought I already told you, this is probably unsafe....

This is a list of all/most of the ports that I think are necessary (I've never actually exposed this to the internet)

### Ports:
Some of these probably don't need to be exposed to the internet... they'd be for the services to talk to each other.
Master Server: 
```
2002
```
GM Server:
```
2003
```
Character Server: 
```
...?
```
World Servers:
```
2006?
7001
7002
29000->29020?
```

## Connecting To Server

### Running the client
It is possible to run the client from this kit, just run:
```
C:\Python27\python.exe .\Client.pyw
```

You shouldn't need any other changes... If you'd prefer to run the original install MoM client there are a few issues, see below:

### Running the original MoM client

The default Minions of Mirth client is hardcoded to connect to `master.minionsofmirth.net`.<br/>
The default client can only see servers with names beginning `PREMIUM<space>` or `FREE<SPACE>`.

To bypass the `master.minionsofmirth.net` issue, you can edit `C:\Windows\System32\drivers\etc\hosts` to add the line:
 ```
 # swap 127.0.0.1 for the IP of your server
 127.0.0.1 master.minionsofmirth.net
 ```

### Creating an account to login
1. Start the Minions of Mirth Client...
2. Click `Register`
3. Enter some details - the email is not currently used
4. A windows with the account's password will appear

## What's not working?
* Grants - They're not in the TMMOKit, and it's not something I remember from when I used to play... Seems to allow you to be gifted money, monsters... Maybe a GM tool?
* IRC - Maybe it does work? I haven't looked at it

## Really useful stuff:
* Description of the TMMOKit: https://realmcrafter.boards.net/thread/99/started-installing-tmmokit-read-first
* Documentation for the TMMOKit: https://web.archive.org/web/20111210231923/http://www.mmoworkshop.com/trac/mom/wiki/Documentation
* Server Architecture Version 2: https://web.archive.org/web/20111211020107/http://www.mmoworkshop.com/trac/mom/wiki/ServerArchitecture