# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


# TODO: proper error messages


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.gamesettings import *

from twisted.internet import reactor,ssl
from twisted.web.client import HTTPDownloader,_parse
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword

import sys,imp,os
import traceback
from base64 import encodestring
from sha import new as newSHA
from cPickle import loads,load,dump
from zipfile import ZipFile,ZIP_DEFLATED
from shutil import copyfile,rmtree,copytree,copy2 as shutilCopy
from time import time,sleep
from md5 import md5

from masterLoginDlg import DoMasterLogin



if sys.platform[:6] != 'darwin':
    import win32api
    PLATFORM = "windows"
else:
    PLATFORM = "mac"

ABORT = False
HAVE_PATCHED = False

IGNORE = ("manifest.zip", "manifest.sha", "common/manifest.zip", "common/manifest.sha", "common/console.log", "common/logs", "common/%s/client/config.cs"%GAMEROOT, "common/%s/client/prefs.cs"%GAMEROOT, "cache/")



def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze



# Return a list of SHA checksums every 64k of a file,
#  together with the total file size.
def getSHA(filename):
    f = open(filename,'rb')
    data = f.read()
    f.close()
    
    tsize = size = len(data)
    shalist = []
    start = 0
    
    while(size > 0):
        m = newSHA()
        d = data[start : start + 65535]
        m.update(d)
        shalist.append(m.hexdigest())
        size -= 65535
        start += 65535
    
    return tsize,shalist


def dirwalk(directory, ignore, errback=None):
    "walk a directory tree, using a generator"
    
    if not os.path.isdir(directory):
        errorString = "ERROR in dirwalk: %s is not a directory"%directory
        if errback:
            errback(errorString)
        else:
            print errorString
        return
    
    if os.path.islink(directory):
        errorString = "ERROR in dirwalk: %s is a symbolic link"%directory
        if errback:
            errback(errorString)
        else:
            print errorString
        return
    
    try:
        dirlist = os.listdir(directory)
    
    # If an exception occurs, denied permission
    #  is the most likely cause.
    except:
        exception = traceback.format_exc()
        if errback:
            errback(exception)
        else:
            print exception
        return
    
    for path in dirlist:
        if ".SVN" in path.upper():
            continue
        
        fullpath = os.path.join(directory,path)
        fullpath = fullpath.replace("\\","/")
        fullpathUpper = fullpath.upper()
        
        for i in ignore:
            if i in fullpathUpper:
                break
        else:
            if os.path.isdir(fullpath) and not os.path.islink(fullpath):
                # Recurse into subdirectory.
                for x in dirwalk(fullpath,ignore,errback):
                    yield x
            else:
                yield fullpath


# Counts all the files in a directory plus its subdirectories.
def countFiles(path, ignore, errback=None):
    numFiles = 0
    
    if not os.path.isdir(path):
        errorString = "ERROR in countFiles: %s is not a directory"%path
        if errback:
            errback(errorString)
        else:
            print errorString
        return 0
    
    if os.path.islink(path):
        errorString = "ERROR in countFiles: %s is a symbolic link"%path
        if errback:
            errback(errorString)
        else:
            print errorString
        return 0
    
    for elem in dirwalk(path,ignore,errback):
        elem = elem.replace('\\','/')
        if not os.path.isfile(elem):
            continue
        numFiles += 1
    
    return numFiles



class MyHTTPDownloader(HTTPDownloader):
    def __init__(self, url, fileOrName, statusCallback=None, \
                 progressCallback=None, *args, **kwargs):
        self.statusCallback = statusCallback
        self.progressCallback = progressCallback
        
        self.progress = 0
        self.targetSize = 0
        
        HTTPDownloader.__init__(self,url,fileOrName,*args,**kwargs)
    
    
    def gotHeaders(self, headers):
        if ABORT:
            if self.protocol and self.protocol.transport:
                self.protocol.transport.loseConnection()
        
        else:
            if headers.has_key('content-length'):
                self.targetSize = int(headers['content-length'][0])
                if self.statusCallback:
                    self.statusCallback("0/%i kB"%(self.targetSize / 1024))
            else:
                if self.statusCallback:
                    self.statusCallback("file size unknown, progress indicator inaccurate")
                    self.statusCallback = None
        
        return HTTPDownloader.gotHeaders(self,headers)
    
    
    def pagePart(self, data):
        if ABORT:
            if self.protocol and self.protocol.transport:
                self.protocol.transport.loseConnection()
        
        else:
            if self.targetSize:
                self.progress += len(data)
                
                relativeProgress = float(self.progress) / float(self.targetSize)
                
                if self.statusCallback:
                    self.statusCallback("%i/%i kB"%(self.progress / 1024, \
                                                    self.targetSize / 1024))
            
            # Otherwise we don't know the file size, so just increment the
            #  progress counter by an arbitrary amount so user sees something
            #  happening.
            else:
                self.progress += 0.001
                if self.progress > 1.0:
                    self.progress = 0.0
                
                relativeProgress = self.progress
            
            if self.progressCallback:
                self.progressCallback(relativeProgress)
        
        return HTTPDownloader.pagePart(self,data)



def downloadPage(url, file, statusCallback=None, progressCallback=None, \
                 contextFactory=None, *args, **kwargs):
    """Download a web page to a file.
    
    @param file: path to file on filesystem, or file-like object.
    
    See HTTPDownloader to see what extra args can be passed.
    """
    
    scheme,host,port,path = _parse(url)
    
    factory = MyHTTPDownloader(url,file,statusCallback,progressCallback, \
                               *args,**kwargs)
    
    if scheme == 'https':
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host,port,factory,contextFactory)
    else:
        reactor.connectTCP(host,port,factory)
    
    return factory.deferred



class LocalManifest:
    def __init__(self, resultback=None, statusCallback=None, \
                 progressCallback=None, errback=None):
        self.resultback = resultback
        self.statusCallback = statusCallback
        self.progressCallback = progressCallback
        self.errback = errback
        
        self.baseDesc = ""
        self.base = ""
        
        self.manifest = {}
        
        self.generatorTick(self.generate())
    
    
    def load(self):
        try:
            f = file("./cache/%s_manifest.cache"%self.base,'rb')
            cache = load(f)
            f.close()
        except:
            cache = {}
        
        return cache
    
    
    def save(self, cache):
        try:
            f = file("./cache/%s_manifest.cache"%self.base,'wb')
            dump(cache,f)
            f.close()
        except:
            traceback.print_exc()
            print "WARNING in LocalManifest.save: couldn't save manifest cache."
    
    
    def generationError(self, text):
        global ABORT
        ABORT = True
        
        # Return the error.
        if self.errback:
            self.errback(text)
    
    
    def generateManifestPart(self, path, ignore=[], cache={}):
        if ABORT:
            return
        
        ptime = time()
        newCache = {}
        
        if self.statusCallback:
            self.statusCallback("Counting files for %s"%self.baseDesc)
        if self.progressCallback:
            self.progressCallback(0.0)
        
        totalFiles = countFiles(path,ignore,self.generationError)
        if ABORT:
            return
        
        numFiles = 0
        
        if self.statusCallback:
            self.statusCallback("Processing files for %s, 0/%i done"% \
                                (self.baseDesc,totalFiles))
        
        for elem in dirwalk(path,ignore,self.generationError):
            if ABORT:
                return
            
            elem = elem.replace('\\','/')
            if not os.path.isfile(elem):
                continue
            
            if self.base == "common":
                fileDescriptor = elem[elem.find(self.base):]
            elif self.base == "base":
                fileDescriptor = elem[len('./'):]
            
            fsize = os.path.getsize(elem)
            ctime = os.path.getctime(elem)
            mtime = os.path.getmtime(elem)
            curFileVersion = (fsize,ctime,mtime)
            
            if cache.has_key(elem):
                # File present in cache, so check if the version matches.
                fileVersion,fileCache = cache[elem]
                if curFileVersion != fileVersion:
                    # Version doesn't match, update cache entry.
                    del cache[elem]
                    fileCache = getSHA(elem)
                    cache[elem] = (curFileVersion,fileCache)
            else:
                fileCache = getSHA(elem)
                cache[elem] = (curFileVersion,fileCache)
            
            newCache[elem] = (curFileVersion,fileCache)
            
            self.manifest[fileDescriptor.lower()] = fileCache
            
            numFiles += 1
            
            if time() - ptime > 0.1:
                if self.statusCallback:
                    self.statusCallback("Processing files for %s, %i/%i done"% \
                                        (self.baseDesc,numFiles,totalFiles))
                if self.progressCallback:
                    self.progressCallback(float(numFiles) / float(totalFiles))
                ptime = time()
                yield newCache
    
    
    def generatorTick(self, generator):
        global ABORT
        if ABORT:
            return
        
        try:
            generator.next()
            if ABORT:
                return
            reactor.callLater(0.01,self.generatorTick,generator)
        except StopIteration:
            if self.resultback:
                self.resultback(self.manifest)
        except GeneratorExit:
            return
        except:
            ABORT = True
            exception = traceback.format_exc()
            if self.errback:
                self.errback(exception)
            else:
                print exception
    
    
    # Generate local manifests of files.
    def generate(self):
        global ABORT
        if ABORT:
            return
        
        # Dictionary with the components to be treated.
        # Value is a tuple of (base,base description,ignore).
        components = {"./": ("base","Platform Manifest",["./COMMON"]),
                      "common": ("common","Content Manifest",["COMMON/CONSOLE.LOG"])}
        
        for component,args in components.iteritems():
            self.base,self.baseDesc,ignore = args
            
            cache = self.load()
            
            try:
                generator = self.generateManifestPart(component,ignore,cache)
                if ABORT:
                    return
                
                newCache = None
                while 1:
                    try:
                        newCache = generator.next()
                        if ABORT:
                            return
                        yield True
                    except StopIteration:
                        break
                    except GeneratorExit:
                        return
                
                if newCache:
                    self.save(newCache)
            
            except:
                ABORT = True
                exception = traceback.format_exc()
                if self.errback:
                    self.errback(exception)
                else:
                    print exception



PATCHCODE_LIVEUPDATE = 0
PATCHCODE_MULTIPLAYER = 1

PATCHSTATUS_IDLE = 0
PATCHSTATUS_GETLOCALMANIFEST = 1
PATCHSTATUS_GETREMOTEMANIFEST = 2
PATCHSTATUS_COMPAREMANIFESTS = 3
PATCHSTATUS_DOWNLOADPATCH = 4

class Patcher(object):
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not Patcher.instance:
            Patcher.instance = object.__new__(cl, *p, **k)
        return Patcher.instance
    
    
    def __init__(self):
        self.tgeInitialized = False
        
        self.username = ""
        self.cUsername = ""
        self.password = ""
        self.cPassword = ""
        
        self.patchCode = PATCHCODE_LIVEUPDATE
        self.patchServerAddress = ""
        self.cPatchServerAddress = ""
        self.patchTag = ""
        self.version = "testing"
        
        self.reset()
    
    
    def reset(self):
        global ABORT
        ABORT = False
        
        self.localManifest = {}
        self.remoteManifest = {}
        
        self.patchFiles = {}
        self.curPatchSize = 0
        self.patchSize = 0
        self.downloadGenerator = None
        self.firstPatchFileInfo = None
        self.secondPatchFileInfo = None
        
        self.status = PATCHSTATUS_IDLE
        
        self.remoteManifestsReceived = 0
        self.swapBin = False
        
        self.firstProgress = 0.0
        self.secondProgress = 0.0
        
        if self.tgeInitialized:
            self.tgeStatusText.visible = False
            self.tgeFirstText.visible = False
            self.tgeFirstProgress.visible = False
            self.tgeSecondText.visible = False
            self.tgeSecondProgress.visible = False
            self.tgeTotalText.visible = False
            self.tgeTotalProgress.visible = False
            
            self.tgeFirstText.setText("")
            self.tgeFirstProgress.setValue(0.0)
            self.tgeSecondText.setText("")
            self.tgeSecondProgress.setValue(0.0)
            self.tgeTotalText.setText("")
            self.tgeTotalProgress.setValue(0.0)
    
    
    @staticmethod
    def getInstance(self):
        return Patcher.instance
    
    
    def initTGEObjects(self):
        self.tgeStatusText = TGEObject("PATCHER_STATUS_TEXT")
        
        self.tgeFirstText = TGEObject("PATCHER_FIRST_TEXT")
        self.tgeFirstProgress = TGEObject("PATCHER_FIRST_PROGRESS")
        self.tgeSecondText = TGEObject("PATCHER_SECOND_TEXT")
        self.tgeSecondProgress = TGEObject("PATCHER_SECOND_PROGRESS")
        
        self.tgeTotalText = TGEObject("PATCHER_TOTAL_TEXT")
        self.tgeTotalProgress = TGEObject("PATCHER_TOTAL_PROGRESS")
        
        self.tgeInitialized = True
    
    
    def setupPatchInfo(self, demo, patchCode=PATCHCODE_LIVEUPDATE, \
                       live=RPG_BUILD_LIVE):
        self.patchCode = patchCode
        
        self.username = self.cUsername = ""
        self.password = self.cPassword = ""
        
        if GAMEROOT == "minions.of.mirth":
            if demo:
                self.patchServerAddress = \
                    "http://patch.prairiegames.com/svn/mompatch/demo"
                self.cPatchServerAddress = self.patchServerAddress
                self.patchTag = ""
                self.version = "demo"
            else:
                self.patchServerAddress = ""
                
                if live:
                    self.cPatchServerAddress = \
                        "http://patch.prairiegames.com/svn/mompatch/live"
                    self.patchTag = "branches/live"
                else:
                    self.cPatchServerAddress = \
                        "http://patch.prairiegames.com/svn/mompatch/testing"
                    self.patchTag = "trunk"
                
                self.version = "testing"
        
        else:
            self.patchServerAddress = ""
            self.cPatchServerAddress = ""
            self.patchTag = ""
            self.version = "testing"
    
    
    def firstStatusCallback(self, text):
        if self.status == PATCHSTATUS_GETREMOTEMANIFEST:
            text = "Downloading Platform Manifest: %s"%text
        elif self.status == PATCHSTATUS_DOWNLOADPATCH:
            file,version,redownload = self.firstPatchFileInfo
            file = os.path.basename(file)
            if redownload:
                text = "Redownloading %s: %s"%(file,text)
            else:
                text = "Downloading %s: %s"%(file,text)
        
        self.tgeFirstText.setText(text)
    
    
    def firstProgressCallback(self, value):
        self.firstProgress = value
        self.tgeFirstProgress.setValue(value)
        
        if self.status == PATCHSTATUS_GETLOCALMANIFEST:
            # Generating the local manifest shall take 10%
            #  of the total progress fixed.
            self.tgeTotalProgress.setValue(value / 10.0)
        elif self.status == PATCHSTATUS_GETREMOTEMANIFEST:
            # Each of the remote manifests to download shall
            #  take up a fixed 5% on the total progress bar.
            self.tgeTotalProgress.setValue(0.1 + (value + self.secondProgress) / 20.0)
        elif self.status == PATCHSTATUS_DOWNLOADPATCH:
            # Everything before patch takes up 20%.
            firstSize = self.firstPatchFileInfo[1][0]
            
            try:
                secondSize = self.secondPatchFileInfo[1][0]
            except:
                secondSize = 0
            
            self.tgeTotalProgress.setValue(0.2 + \
                 ((value * float(firstSize) + self.secondProgress * \
                   float(secondSize) + float(self.curPatchSize)) / \
                   float(self.patchSize)) * 0.8)
            self.tgeTotalText.setText("%i kB Remaining"%((self.patchSize - \
                 self.curPatchSize - int(value * float(firstSize)) - \
                 int(self.secondProgress * float(secondSize))) / 1024))
    
    
    def secondStatusCallback(self, text):
        if self.status == PATCHSTATUS_GETREMOTEMANIFEST:
            text = "Downloading Content Manifest: %s"%text
        elif self.status == PATCHSTATUS_DOWNLOADPATCH:
            file,version,redownload = self.secondPatchFileInfo
            file = os.path.basename(file)
            if redownload:
                text = "Redownloading %s: %s"%(file,text)
            else:
                text = "Downloading %s: %s"%(file,text)
        
        self.tgeSecondText.setText(text)
    
    
    def secondProgressCallback(self, value):
        self.secondProgress = value
        self.tgeSecondProgress.setValue(value)
        
        if self.status == PATCHSTATUS_GETREMOTEMANIFEST:
            # Each of the remote manifests to download shall
            #  take up a fixed 5% on the total progress bar.
            self.tgeTotalProgress.setValue(0.1 + (value + self.firstProgress) / 20.0)
        elif self.status == PATCHSTATUS_DOWNLOADPATCH:
            # Everything before patch takes up 20%.
            
            try:
                firstSize = self.firstPatchFileInfo[1][0]
            except:
                firstSize = 0
            
            secondSize = self.secondPatchFileInfo[1][0]
            self.tgeTotalProgress.setValue(0.2 + \
                 ((self.firstProgress * float(firstSize) + value * \
                   float(secondSize) + float(self.curPatchSize)) / \
                   float(self.patchSize)) * 0.8)
            self.tgeTotalText.setText("%i kB Remaining"%((self.patchSize - \
                 self.curPatchSize - int(self.firstProgress * \
                 float(firstSize)) - int(value * float(secondSize))) / 1024))
    
    
    def patchDirCleanupErrback(self, errorString):
        global ABORT
        ABORT = True
        
        errorString = 'There was an error cleaning up the patch_files directory:\n%s'% \
                      errorString
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
    
    
    def finalize(self, restart=True):
        global HAVE_PATCHED
        
        # Update GUI elements.
        self.tgeStatusText.setText("Patch completed!")
        self.tgeFirstText.visible = False
        self.tgeFirstProgress.visible = False
        self.tgeSecondText.visible = False
        self.tgeSecondProgress.visible = False
        self.tgeTotalText.setText("Patch completed!")
        self.tgeTotalProgress.setValue(1.0)
        
        # Clean up the restore directory.
        try:
            if os.path.exists("./restore"):
                rmtree("./restore")
        except:
            traceback.print_exc()
        
        # Clean up the patch files directory if needed.
        if not restart:
            try:
                if os.path.exists("./patch_files"):
                    rmtree("./patch_files")
            except:
                traceback.print_exc()
        
        # Mark patch as completed.
        HAVE_PATCHED = True
        self.status = PATCHSTATUS_IDLE
        
        if restart:
            if self.swapBin and PLATFORM == "windows":
                try:
                    if os.path.exists("./tempbin"):
                        rmtree("./tempbin")
                except:
                    traceback.print_exc()
                    TGEEval('MessageBoxOK("Patcher Error","Error removing tempbin folder.","Py::OnPatchError();");')
                    return
                
                try:
                    copytree("./bin","./tempbin")
                    if os.path.exists("./patch_files/bin"):
                        for f in os.listdir("./patch_files/bin"):
                            shutilCopy('./patch_files/bin/%s'%f,'./tempbin/%s'%f)
                except:
                    traceback.print_exc()
                    TGEEval('MessageBoxOK("Patcher Error","Failed to move binary files to tempbin folder.","Py::OnPatchError();");')
                    return
            
            self.tgeStatusText.setText("Restart Needed!")
            TGEEval('MessageBoxOK("Restart Needed","%s has been patched and needs to be restarted.","Py::OnPatchRestart();");'%GAMENAME)
        
        # No restart needed, so continue with what we were doing.
        else:
            os.chdir("./common")
            if self.patchCode == PATCHCODE_MULTIPLAYER:
                DoMasterLogin()
            else:
                TGEEval("canvas.setContent(MainMenuGui);")
                DisplayPatchInfo()
                TGEEval('MessageBoxOK("Live Update","Your game is up to date.");')
    
    
    def fileDownloadGenerator(self):
        for file,version in self.patchFiles.iteritems():
            yield file,version
    
    
    def fileDownloadErrback(self, reason, filename):
        global ABORT
        ABORT = True
        
        errorString = 'An error occurred while downloading patch file "%s":\n%s'% \
                      (filename,reason.getErrorMessage())
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
    
    
    def fileDownloadSuccess(self, result, slot):
        global ABORT
        if ABORT:
            return
        
        #XXX DEBUG!!!! You must not be running WorldManager,
        #               Genesis.exe, etc while patching!
        
        # Get the file information on what should have been downloaded.
        if slot == 1:
            targetFile,targetVersion,redownload = self.firstPatchFileInfo
            self.tgeFirstText.setText("Verifying %s"%targetFile)
        else:
            targetFile,targetVersion,redownload = self.secondPatchFileInfo
            self.tgeSecondText.setText("Verifying %s"%targetFile)
        
        patchFileName = "./patch_files/%s"%targetFile
        
        # Check if the downloaded file matches version requirements.
        try:
            downloadedVersion = getSHA(patchFileName)
        except:
            if ABORT:
                return
            downloadedVersion = None
        if targetVersion != downloadedVersion:
            # Remove the faulty download.
            try:
                os.remove(patchFileName)
            except:
                ABORT = True
                errorString = 'Error removing faulty patch download "%s":\n%s'% \
                              (patchFileName,traceback.format_exc())
                print errorString
                TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
                return
            
            # Try to redownload if this isn't already a redownload.
            if not redownload:
                self.downloadFile(targetFile,targetVersion,slot,True)
            else:
                ABORT = True
                errorString = 'Error: downloaded patch file "%s" still faulty after second download attempt. Aborting patch process.'%patchFileName
                print errorString
                TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
            
            # Downloaded file was faulty, so return early.
            return
        
        # Increment current patch size.
        self.curPatchSize += targetVersion[0]
        
        root,ext = os.path.splitext(targetFile)
        ext = ext.lower()
        if ext in (".pyd",".dll",".exe"):
            self.swapBin = True
        
        # Download the next file if there are files remaining to be downloaded.
        try:
            currFile,currVersion = self.downloadGenerator.next()
            self.downloadFile(currFile,currVersion,slot)
        except StopIteration:
            # Just reset the patchfileinfo for process sychronization,
            #  the other download could still be active.
            if slot == 1:
                self.firstPatchFileInfo = None
            else:
                self.secondPatchFileInfo = None
            # If no more files (first + second) are being downloaded, then finalize.
            if self.firstPatchFileInfo == None and self.secondPatchFileInfo == None:
                self.finalize()
        except:
            ABORT = True
            errorString = 'Error scheduling download of patch file "%s":\n%s'% \
                          (currFile,traceback.format_exc())
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
            return
    
    
    def downloadFile(self, file, version, slot, redownload=False):
        global ABORT
        if ABORT:
            return
        
        if slot == 1:
            if redownload:
                self.tgeFirstText.setText("Redownloading %s"%os.path.basename(file))
            else:
                self.tgeFirstText.setText("Downloading %s"%os.path.basename(file))
            self.tgeFirstProgress.setValue(0.0)
            statusCallback = self.firstStatusCallback
            progressCallback = self.firstProgressCallback
            self.firstPatchFileInfo = file,version,redownload
        else:
            if redownload:
                self.tgeSecondText.setText("Redownloading %s"%os.path.basename(file))
            else:
                self.tgeSecondText.setText("Downloading %s"%os.path.basename(file))
            self.tgeSecondProgress.setValue(0.0)
            statusCallback = self.secondStatusCallback
            progressCallback = self.secondProgressCallback
            self.secondPatchFileInfo = file,version,redownload
        
        patchFileName = "./patch_files/%s"%file
        
        try:
            path = os.path.normpath(os.path.dirname(patchFileName))
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            ABORT = True
            errorString = 'Could not create required directories for "%s":\n%s'% \
                          (patchFileName,traceback.format_exc())
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
            return
        
        webFile = file.replace(' ',r'%20')
        
        if webFile.startswith("common/"):
            username = self.cUsername
            password = self.cPassword
            address = self.cPatchServerAddress
            
            if self.patchTag and not RPG_BUILD_LIVE:
                webFile = "common/%s/%s"%(self.patchTag,webFile[7:])
        
        else:
            username = self.username
            password = self.password
            address = self.patchServerAddress
            
            if self.patchTag:
                webFile = "%s/%s/%s"%(PLATFORM,self.patchTag,webFile)
            else:
                webFile = "%s/%s"%(PLATFORM,webFile)
        
        extraHeaders = {}
        extraHeaders['Authorization'] = 'Basic ' + \
                     encodestring("%s:%s"%(username,password)).strip()
        
        url = "%s/%s"%(address,webFile)
        
        d = downloadPage(url,patchFileName,statusCallback,progressCallback, \
                         headers=extraHeaders)
        d.addCallback(self.fileDownloadSuccess,slot)
        d.addErrback(self.fileDownloadErrback,patchFileName)
    
    
    def compareManifests(self):
        global ABORT
        if ABORT:
            return
        
        # Update status messages.
        self.tgeStatusText.setText("Comparing Manifests (Please Wait)")
        self.tgeFirstText.setText("")
        self.tgeSecondText.setText("")
        self.tgeTotalText.setText("Comparing Manifests")
        
        # Update progress bars.
        self.tgeFirstProgress.setValue(0.0)
        self.tgeFirstProgress.visible = False
        self.tgeSecondProgress.setValue(0.0)
        self.tgeSecondProgress.visible = False
        # After creating and downloading the manifests, we should now be at 20%.
        self.tgeTotalProgress.setValue(0.2)
        
        # Update internal status.
        self.status = PATCHSTATUS_COMPAREMANIFESTS
        
        try:
            patchFilesUsed = []
            
            for file in sorted(self.remoteManifest.iterkeys()):
                if file in IGNORE:
                    continue
                
                remoteVersion = self.remoteManifest[file]
                
                # Case insensitive comparison.
                fileLower = file.lower()
                localVersion = self.localManifest.get(fileLower)
                patchVersion = self.localManifest.get("patch_files/%s"%(fileLower),None)
                
                if localVersion != remoteVersion:
                    # Compare to downloaded file that may be in patch files.
                    if patchVersion != remoteVersion:
                        self.patchFiles[file] = remoteVersion
                        self.patchSize += remoteVersion[0]
                    else:
                        root,ext = os.path.splitext(file)
                        ext = ext.lower()
                        if ext in (".pyd",".dll",".exe"):
                            self.swapBin = True
                        patchFilesUsed.append(file.upper())
                
                # Local file version matches remote file version.
                else:
                    # Check if the file is present in the directory with the
                    #  patch files and remove it if so.
                    if patchVersion:
                        patchFile = "patch_files/%s"%file
                        try:
                            if os.path.exists(patchFile):
                                os.remove(patchFile)
                        except:
                            ABORT = True
                            errorString = 'Error removing patch file "%s":\n%s'% \
                                          (file,traceback.format_exc())
                            print errorString
                            TGECall("MessageBoxOK","Patcher Error",errorString, \
                                    "Py::OnPatchError();")
                            return
            
            # Get rid of all already outdated patch files if any.
            if os.path.exists("patch_files"):
                for elem in dirwalk("patch_files",patchFilesUsed, \
                                    self.patchDirCleanupErrback):
                    if ABORT:
                        return
                    
                    elem = elem.replace('\\','/')
                    
                    # Try to remove the file or link.
                    try:
                        os.remove(elem)
                    except:
                        ABORT = True
                        errorString = 'Error removing patch file "%s":\n%s'% \
                                      (elem,traceback.format_exc())
                        print errorString
                        TGECall("MessageBoxOK","Patcher Error",errorString, \
                                "Py::OnPatchError();")
                        return
            
            # If there are patch files to be downloaded, download them now.
            if len(self.patchFiles):
                # Update GUI elements.
                self.tgeStatusText.setText("Downloading Patch Files...")
                self.tgeTotalText.setText("%i kB Remaining"%(self.patchSize / 1024))
                
                # Kick start downloading.
                self.status = PATCHSTATUS_DOWNLOADPATCH
                self.downloadGenerator = self.fileDownloadGenerator()
                
                # Start downloading the first file.
                currFile,currVersion = self.downloadGenerator.next()
                self.tgeFirstProgress.visible = True
                self.downloadFile(currFile,currVersion,1)
                
                # If there is more than one file, start downloading the second
                #  one as well.
                if len(self.patchFiles) > 1:
                    currFile,currVersion = self.downloadGenerator.next()
                    self.tgeSecondProgress.visible = True
                    self.downloadFile(currFile,currVersion,2)
            
            # No files need to be downloaded, check if some files need
            #  to be moved.
            else:
                # There are some files in the patch file folder that need
                #  to be installed.
                if len(patchFilesUsed):
                    self.finalize()
                
                # No files need to be patched, so finalize.
                else:
                    self.finalize(False)
        
        except:
            ABORT = True
            errorString = 'An error occurred while comparing manifests:\n%s'% \
                          traceback.format_exc()
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
            return
    
    
    def remoteManifestErrback(self, reason):
        global ABORT
        ABORT = True
        
        errorString = 'Unable to retrieve remote manifests:\n%s'% \
                      reason.getErrorMessage()
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
    
    
    def remoteManifestResultback(self, value, page):
        global ABORT
        if ABORT:
            return
        
        try:
            zfile = ZipFile("./cache/%s_manifest.zip"%page,'r')
            manifest = loads(zfile.read('./manifest'))
            zfile.close()
            
            self.remoteManifest.update(manifest)
        except:
            ABORT = True
            errorString = 'Error while analysing remote manifest %s:\n%s'% \
                          (page,traceback.format_exc())
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
            return
        
        self.remoteManifestsReceived += 1
        
        if self.remoteManifestsReceived == 2:
            self.compareManifests()
    
    
    def localManifestErrback(self, errorString):
        global ABORT
        ABORT = True
        
        errorString = 'There was an error building the local manifest:\n%s'% \
                      errorString
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
    
    
    def localManifestResultback(self, manifest):
        if ABORT:
            return
        
        self.localManifest = manifest
        
        # Reset the first substatus.
        self.tgeFirstText.setText("Downloading Platform Manifest")
        self.firstProgress = 0.0
        self.tgeFirstProgress.setValue(0.0)
        
        # Set the total progress counter to 10%.
        # (this is where it should be now, 10% for local manifests)
        self.tgeTotalProgress.setValue(0.1)
        
        # Adjust status text, we're getting the remote manifests next.
        self.tgeStatusText.setText("Retrieving Remote Manifests")
        self.tgeTotalText.setText("Downloading Remote Manifests")
        
        # Initialize second substatus.
        self.tgeSecondText.setText("Downloading Content Manifest")
        self.tgeSecondText.visible = True
        self.tgeSecondProgress.visible = True
        
        # Try to retrieve the remote manifests.
        self.status = PATCHSTATUS_GETREMOTEMANIFEST
        
        extraHeaders = {}
        extraHeaders['Authorization'] = 'Basic ' + \
                     encodestring("%s:%s"%(self.cUsername,self.cPassword)).strip()
        
        if self.patchTag and not RPG_BUILD_LIVE:
            url = "%s/common/%s/manifest.zip"%(self.cPatchServerAddress,self.patchTag)
        else:
            url = "%s/common/manifest.zip"%self.cPatchServerAddress
        
        d = downloadPage(url,"./cache/base_manifest.zip", \
                         self.secondStatusCallback, \
                         self.secondProgressCallback, \
                         headers=extraHeaders)
        d.addCallbacks(self.remoteManifestResultback, \
                       self.remoteManifestErrback,("base",))
        
        extraHeaders = {}
        extraHeaders['Authorization'] = 'Basic ' + \
                     encodestring("%s:%s"%(self.username,self.password)).strip()
        
        if self.patchTag:
            url = "%s/%s/%s/manifest.zip"%(self.patchServerAddress, \
                                           PLATFORM,self.patchTag)
        else:
            url = "%s/%s/manifest.zip"%(self.patchServerAddress,PLATFORM)
        
        d = downloadPage(url,"./cache/%s_manifest.zip"%PLATFORM, \
                         self.firstStatusCallback, \
                         self.firstProgressCallback, \
                         headers=extraHeaders)
        d.addCallbacks(self.remoteManifestResultback, \
                       self.remoteManifestErrback,(PLATFORM,))
    
    
    def patch(self):
        global ABORT
        
        # Reset ourselves.
        self.reset()
        
        # Show the patcher gui.
        TGEEval("canvas.setContent(PatcherGui);")
        
        try:
            # Go up one level.
            os.chdir("../")
            
            # Make sure the cache directory exists.
            cachedir = "./cache"
            if os.path.exists(cachedir):
                # Check if it indeed is a directory.
                if not os.path.isdir(cachedir) or os.path.islink(cachedir):
                    # Not a directory, so attempt to remove it.
                    try:
                        os.remove(cachedir)
                    except:
                        traceback.print_exc()
                        TGEEval('MessageBoxOK("Patcher Error","Could not remove cache file/link (needs to be a directory). Missing permissions?","Py::OnPatchError();");')
                        return
                    # Invalid file removed, so create our directory now.
                    try:
                        os.makedirs(cachedir)
                    except:
                        traceback.print_exc()
                        TGEEval('MessageBoxOK("Patcher Error","Could not create cache directory. Missing permissions?","Py::OnPatchError();");')
                        return
            else:
                # Cache directory does not exist yet, so create one.
                try:
                    os.makedirs(cachedir)
                except:
                    traceback.print_exc()
                    TGEEval('MessageBoxOK("Patcher Error","Could not create cache directory. Missing permissions?","Py::OnPatchError();");')
                    return
            
            # Set status to generating local manifest.
            self.tgeStatusText.setText("Generating Local Manifest")
            self.tgeStatusText.visible = True
            self.tgeTotalText.setText("Inspecting and Caching Local Files")
            self.tgeTotalText.visible = True
            
            # Make related progress indicators visible.
            self.tgeFirstProgress.visible = True
            self.tgeTotalProgress.visible = True
            
            # Initialize substatus.
            self.tgeFirstText.setText("")
            self.tgeFirstText.visible = True
            
            # Create the local manifest.
            self.status = PATCHSTATUS_GETLOCALMANIFEST
            LocalManifest(self.localManifestResultback, \
                          self.firstStatusCallback,     \
                          self.firstProgressCallback,   \
                          self.localManifestErrback)
        
        except:
            ABORT = True
            errorString = 'There was an error during the patching process:\n%s'% \
                          traceback.format_exc()
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString,"Py::OnPatchError();")
    
    
    def patchInfoErrback(self, reason):
        TGECall("CloseMessagePopup")
        
        errorString = 'An error occurred while retrieving patch server information:\n%s'%reason.getErrorMessage()
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString)
    
    
    def patchServerResults(self, args, perspective):
        # Terminate connection to master server.
        perspective.broker.transport.loseConnection()
        
        TGECall("CloseMessagePopup")
        
        if args[0]:
            errorString = 'An error occurred while retrieving patch server information:\n%s'%args[1]
            print errorString
            TGECall("MessageBoxOK","Patcher Error",errorString)
            return
        
        # Patch server address, username and password for platform stuff.
        self.patchServerAddress,self.username,self.password = args[1]
        
        # Patch server address, username and password for content stuff.
        if len(args) > 2 and args[2]:
            self.cPatchServerAddress,self.cUsername,self.cPassword = args[2]
        else:
            self.cPatchServerAddress,self.cUsername,self.cPassword = args[1]
        
        self.patch()
    
    
    def patchLoginErrback(self, reason):
        TGECall("CloseMessagePopup")
        
        errorString = 'An error occurred while logging in to master server:\n%s'%reason.getErrorMessage()
        print errorString
        TGECall("MessageBoxOK","Patcher Error",errorString)
    
    
    def patchLoginConnected(self, perspective):
        TGECall("CloseMessagePopup")
        
        # Request the patch server information.
        TGECall("MessagePopup","Communicating with Master Server...","Please wait...")
        d = perspective.callRemote("PlayerAvatar","getPatchServerInfo", \
                                   PLATFORM,self.version)
        d.addCallbacks(self.patchServerResults,self.patchInfoErrback,(perspective,))
    
    
    def onPatchLogin(self):
        if self.patchCode == PATCHCODE_LIVEUPDATE:
            regkey = TGEObject("PATCHLOGIN_PUBLICNAME").getValue()
            TGEObject("MASTERLOGIN_PUBLICNAME").setText(regkey)
            password = TGEObject("PATCHLOGIN_PASSWORD").getValue()
            TGEObject("MASTERLOGIN_PASSWORD").setText(password)
        else:
            regkey = TGEObject("MASTERLOGIN_PUBLICNAME").getValue()
            TGEObject("PATCHLOGIN_PUBLICNAME").setText(regkey)
            password = TGEObject("MASTERLOGIN_PASSWORD").getValue()
            TGEObject("PATCHLOGIN_PASSWORD").setText(password)
        
        TGESetGlobal("$pref::PublicName",regkey)
        TGESetGlobal("$pref::MasterPassword",password)
        
        if not len(regkey) or not len(password):
            TGECall("MessageBoxOK","Error","Invalid username or password.")
            return
        
        # TODO, validate EMail form.
        
        masterIP = TGEGetGlobal("$Py::MasterIP")
        masterPort = int(TGEGetGlobal("$Py::MasterPort"))
        
        TGECall("MessagePopup","Logging into Master Server...","Please wait...")
        
        factory = pb.PBClientFactory()
        reactor.connectTCP(masterIP,masterPort,factory)
        password = md5(password).digest()
        
        d = factory.login(UsernamePassword("%s-Player"%regkey,password),pb.Root())
        d.addCallbacks(self.patchLoginConnected,self.patchLoginErrback)
    
    
    def onPatchRestart(self):
        # Export Prefs
        
        # In theory we're ready to launch.
        
        # Whatever this part is for... can't use patcher when not frozen anyway.
        if not main_is_frozen():
            cmd = sys.executable
            if GAMEROOT == "minions.of.mirth":
                args = os.path.normpath("%s/MinionsOfMirth.py"%os.getcwd())
            else:
                args = os.path.normpath("%s/Client.py"%os.getcwd())
            args += r' -patch'
            
            os.spawnl(os.P_DETACH,cmd,args)
            reactor.stop()
            TGEEval("quit();")
        
        else:
            if PLATFORM == "windows":
                if self.swapBin:
                    directory = "tempbin"
                else:
                    directory = "bin"
                
                if GAMEROOT == "minions.of.mirth":
                    cmd = "%s/%s/MinionsOfMirth.exe"%(os.getcwd(),directory)
                else:
                    cmd = "%s/%s/Client.exe"%(os.getcwd(),directory)
                
                args = r'-patch -pid=%i'%win32api.GetCurrentProcessId()
                
                # We'll be killed by the patcher process.
                os.spawnl(os.P_NOWAIT,cmd,args)
                os.chdir("./common")
                TGEEval("quit();")
            else:
                if DoPatchOSX():
                    #os.spawnl(os.P_NOWAIT,"./MinionsOfMirth.app/Contents/MacOS/MinionsOfMirth","./MinionsOfMirth.app/Contents/MacOS/MinionsOfMirth")
                    os.chdir("./common")
                    TGEEval("quit();")
    
    
    def onPatchError(self):
        global ABORT
        ABORT = True
        
        try:
            os.chdir("./common")
        except:
            pass
        TGEEval("canvas.setContent(MainMenuGui);")
    
    
    def onPatchCancel(self):
        global ABORT
        ABORT = True
        
        try:
            os.chdir("./common")
        except:
            pass
        TGEEval("canvas.setContent(MainMenuGui);")



Patcher()



def DisplayPatchInfo():
    try:
        f = file('./patchlist.txt','r')
        text = f.read()[:4000]
        f.close()
        
        text = text.replace('\r',"\\r")
        text = text.replace('\n',"\\n") # Valid quote
        text = text.replace('\a',"\\a") # Valid quote
        text = text.replace('"','\\"') # Invalid quote
        
        text = "<shadowcolor:000000><shadow:1:1><font:Arial Bold:14>%s  *** SNIP *** see patchlist.txt if you'd like to read more"%text
        
        TGEEval('patchinfownd_text.setText("%s");'%text)
        
        TGEEval("canvas.pushDialog(PatchInfoWnd);")
    except:
        pass


def DoPatchOSX():
    try:
        import stat
        
        # Create the restore directory and make sure we have access.
        os.makedirs("./restore")
        os.chmod("./restore",stat.S_IRWXO|stat.S_IRWXG|stat.S_IRWXU)
        
        # Install the downloaded patch files.
        for dirpath,dirnames,filenames in os.walk("./patch_files"):
            for file in filenames:
                fullPath = os.path.normpath(os.path.join(dirpath,file))
                dstPath = os.path.normpath(fullPath.replace("patch_files","."))
                
                os.chmod(fullPath,stat.S_IRWXO|stat.S_IRWXG|stat.S_IRWXU)
                
                # THESE DIRS PERMISSIONS ARE NOT +O-RWX!
                # Copy the file to be patched to the restore folder in case
                #  something bad happens.
                restorePath = None
                if os.path.exists(dstPath):
                    restorePath = os.path.normpath("./restore/%s"%dstPath)
                    try:
                        os.makedirs(os.path.normpath(os.path.dirname(restorePath)))
                    except:
                        pass
                    shutilCopy(dstPath,restorePath)
                    os.chmod(restorePath,stat.S_IRWXO|stat.S_IRWXG|stat.S_IRWXU)
                
                head,tail = os.path.split(dstPath)
                
                try:
                    os.makedirs(head)
                except:
                    pass
                
                starttime = time()
                while time() - starttime < 10:
                    try:
                        copyfile(fullPath,dstPath)
                        break
                    except:
                        sleep(1)
                
                # An error occurred, restore the original file.
                else:
                    if restorePath:
                        try:
                            shutilCopy(restorePath,dstPath)
                        except:
                            traceback.print_exc()
                    
                    TGEEval('MessageBoxOK("Patcher Error","Unable to copy file %s.","Py::OnPatchError();");'%fullPath)
                    return False
    
    except:
        traceback.print_exc()
        TGEEval('MessageBoxOK("Patcher Error","There was an error encountered during patch installation.  Please check your console.","Py::OnPatchError();");')
        return False
    
    return True


def OnPatch():
    Patcher.instance.setupPatchInfo(RPG_BUILD_DEMO)
    
    # Only patch if this application wasn't launched from editable
    #  source.
    if main_is_frozen():
        if not RPG_BUILD_DEMO:
            TGEEval('canvas.pushDialog("PatchLoginDlg");')
        else:
            Patcher.instance.patch()


def OnMasterLogin():
    Patcher.instance.setupPatchInfo(RPG_BUILD_DEMO,PATCHCODE_MULTIPLAYER)
    
    # Only check for patching if this application wasn't launched from
    #  editable source.
    if main_is_frozen():
        # If this is the free version...
        if RPG_BUILD_DEMO:
            if not HAVE_PATCHED:
                regkey = TGEObject("MASTERLOGIN_PUBLICNAME").getValue()
                password = TGEObject("MASTERLOGIN_PASSWORD").getValue()
                
                if not len(regkey) or not len(password):
                    TGEEval("Canvas.setContent(MainMenuGui);")
                    TGECall("MessageBoxOK","Error","Invalid username or password.")
                    return
                
                Patcher.instance.patch()
            
            else:
                DoMasterLogin()
        
        # Otherwise we're logging in from premium.
        else:
            if not HAVE_PATCHED:
                Patcher.instance.onPatchLogin()
            else:
                DoMasterLogin()
    
    # Launched from editable source, never update.
    else:
        DoMasterLogin()


def OnMultiplayer():
    TGEEval('canvas.pushDialog("MasterLoginDlg");')


# Upgrade the free version to premium.
def OnPatchToPremium():
    global HAVE_PATCHED
    HAVE_PATCHED = False
    
    # For testing we patch to live.
    Patcher.instance.setupPatchInfo(False,PATCHCODE_LIVEUPDATE,True)
    TGEEval('canvas.pushDialog("PatchLoginDlg");')



def PyExec():
    PATCHER = Patcher.instance
    PATCHER.initTGEObjects()
    
    TGEExport(PATCHER.onPatchLogin,"Py","OnPatchLogin","desc",1,1)
    TGEExport(PATCHER.onPatchRestart,"Py","OnPatchRestart","desc",1,1)
    TGEExport(PATCHER.onPatchError,"Py","OnPatchError","desc",1,1)
    TGEExport(PATCHER.onPatchCancel,"Py","OnPatchCancel","desc",1,1)
    
    TGEExport(DisplayPatchInfo,"Py","DisplayPatchInfo","desc",1,1)
    
    TGEExport(OnPatch,"Py","OnPatch","desc",1,1)
    TGEExport(OnMasterLogin,"Py","OnMasterLogin","desc",1,1)
    TGEExport(OnMultiplayer,"Py","OnMultiplayer","desc",1,1)
    TGEExport(OnPatchToPremium,"Py","OnPatchToPremium","desc",1,1)
    
    # Show the patch to premium button only if necessary.
    TGEObject("PTP_BUTTON").visible = RPG_BUILD_DEMO
    
    # Set the login name and password on the various prompts
    #  if they could be retrieved from settings.
    publicName = TGEGetGlobal("$pref::PublicName")
    if publicName == None:
        publicName = ""
    TGEObject("PATCHLOGIN_PUBLICNAME").setText(publicName)
    TGEObject("MASTERLOGIN_PUBLICNAME").setText(publicName)
    password = TGEGetGlobal("$pref::MasterPassword")
    if password == None:
        password = ""
    TGEObject("PATCHLOGIN_PASSWORD").setText(password)
    TGEObject("MASTERLOGIN_PASSWORD").setText(password)

