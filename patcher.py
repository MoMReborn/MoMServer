# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



#I have to disable this on client until it has SSL 
#from twisted.internet.iocpreactor import install
#install()

import imp, os, sys,time,shutil,traceback
from mud.gamesettings import *

DISPLAY_SPLASH = True
LOCK = None

if sys.platform[:6] != 'darwin':
    
    
    import win32con
    import win32api
    import win32event
    import winerror
    import win32gui
    import struct
        
    #splash screen
    
    
    IDC_BITMAP = 1028
    
    g_registeredClass = 0
    
    SPLASH_SCREEN = None
    
    class Splash:
        def __init__(self, bitmapPath):
            win32gui.InitCommonControls()
            self.hinst = win32api.GetModuleHandle(None)
    
            #retreive width and height from bitmap file, because GetObject does not work for bitmaps :-(
            f = open(bitmapPath, 'rb')
            hdrfm = '<18xii'
            self.bmWidth, self.bmHeight = struct.unpack(hdrfm, f.read(struct.calcsize(hdrfm)))
            f.close()
    
            self.hSplash = win32gui.LoadImage(self.hinst, bitmapPath, win32con.IMAGE_BITMAP, 
                                              0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            
                
        def _RegisterWndClass(self):
            className = "PythonSplash"
            global g_registeredClass
            if not g_registeredClass:
                message_map = {}
                wc = win32gui.WNDCLASS()
                wc.SetDialogProc() # Make it a dialog class.
                self.hinst = wc.hInstance = win32api.GetModuleHandle(None)
                wc.lpszClassName = className
                wc.style = 0
                wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
                wc.hbrBackground = win32con.COLOR_WINDOW + 1
                wc.lpfnWndProc = message_map # could also specify a wndproc.
                wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
                classAtom = win32gui.RegisterClass(wc)
                g_registeredClass = 1
            return className
    
        def _GetDialogTemplate(self, dlgClassName):
            style = win32con.WS_POPUP
    
            dlg = [ ["", (0, 0, 0, 0), style, None, (8, "MS Sans Serif"), None, dlgClassName], ]
    
            dlg.append([130, "", IDC_BITMAP, (0, 0, 0, 0), win32con.WS_VISIBLE | win32con.SS_BITMAP])
    
            return dlg
    
        def CreateWindow(self):
            self._DoCreate(win32gui.CreateDialogIndirect)
    
        def DoModal(self):
            return self._DoCreate(win32gui.DialogBoxIndirect)
    
        def _DoCreate(self, fn):
            message_map = {
                win32con.WM_INITDIALOG: self.OnInitDialog,
                win32con.WM_CLOSE: self.OnClose,
            }
            dlgClassName = self._RegisterWndClass()
            template = self._GetDialogTemplate(dlgClassName)
            return fn(self.hinst, template, 0, message_map)
    
    
        def OnInitDialog(self, hwnd, msg, wparam, lparam):
            self.hwnd = hwnd
    
            desktop = win32gui.GetDesktopWindow()
            dt_l, dt_t, dt_r, dt_b = win32gui.GetWindowRect(desktop)
            centre_x, centre_y = win32gui.ClientToScreen( desktop, ( (dt_r-dt_l)/2, (dt_b-dt_t)/2) )
    
            bmCtrl = win32gui.GetDlgItem(self.hwnd, IDC_BITMAP)
            win32gui.SendMessage(bmCtrl, win32con.STM_SETIMAGE, win32con.IMAGE_BITMAP, self.hSplash)
    
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 
                                  centre_x-(self.bmWidth/2), centre_y-(self.bmHeight/2), 
                                  self.bmWidth, self.bmHeight, win32con.SWP_HIDEWINDOW)
            win32gui.SetForegroundWindow(self.hwnd)
            
            
        def Show(self):
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
          
        def Timer(self, timeOut):
            import time
            time.sleep(timeOut)
            self.EndDialog()
    
        def EndDialogAfter(self, timeOut):
            #thread needed because win32gui does not expose SetTimer API
            import thread
            thread.start_new_thread(self.Timer, (timeOut, ))
        
        def EndDialog(self):
            win32gui.EndDialog(self.hwnd, 0)
            
        def OnClose(self, hwnd, msg, wparam, lparam):
            self.EndDialog()


    def SplashThread(args):
        global DISPLAY_SPLASH
        if "-patch" in sys.argv:
            SPLASH_SCREEN = Splash("./common/%s/client/ui/minions_splash.bmp"%GAMEROOT)
        else:
            SPLASH_SCREEN = Splash("../common/%s/client/ui/minions_splash.bmp"%GAMEROOT)
            
        SPLASH_SCREEN.CreateWindow()
        SPLASH_SCREEN.Show()
        while True:
            LOCK.acquire()
            if not DISPLAY_SPLASH:
                break
            LOCK.release()
            win32gui.PumpWaitingMessages()
            
        SPLASH_SCREEN.EndDialog()
            


    
        
def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

    
    
def DoPatch():
    
    global DISPLAY_SPLASH

    try:
        import time,shutil#,zipimport
        
        #unload library.zip, no more imports from here
        #sys.path_importer_cache.clear()
        #zipimport._zip_directory_cache.clear()       
            
        
        #copy to restore
        
        os.makedirs("./restore")
        
        for dirpath,dirnames,filenames in os.walk("./patch_files"):
            for file in filenames:
                full = os.path.normpath(dirpath+"/"+file)
                
                error = True
                dst = full.replace("patch_files",".")                        
                
                if os.path.exists(dst):
                    try:
                        os.makedirs(os.path.normpath(os.path.dirname("./restore/"+dst[2:])))
                    except:
                        pass
                    shutil.copy(dst,"./restore/"+dst[2:])

                head,tail = os.path.split(dst)
                
                try:
                    os.makedirs(head)
                except:
                    pass

                    
                
                starttime = time.time()
                while time.time()-starttime < 10:
                    try:
                        shutil.copy(full,dst)
                        error = False
                        break
                    except:
                        time.sleep(1)
                        pass
                    
                if error:
                    #restore
                    for dirpath,dirnames,filenames in os.walk("./restore"):
                        for file in filenames:
                            rfull = os.path.normpath(dirpath+"/"+file)
                            dst = rfull[8:] #get rid of restore   
                            try:                         
                                shutil.copy(rfull,dst)
                            except:
                                traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
                                
                        if LOCK:
                            LOCK.acquire()
                            DISPLAY_SPLASH = False
                            LOCK.release()

                    win32api.MessageBox(0, 'Unable to copy file %s'%full, "Error",win32con.MB_OK)
                    return  
                
                
        try:
            if os.path.exists("./patch_files"):
                shutil.rmtree("./patch_files")
        except:
            pass

        
        if GAMEROOT == "minions.of.mirth":
            cmd = os.getcwd()+"\\bin\\MinionsOfMirth.exe"
        else:
            cmd = os.getcwd()+"\\bin\\Client.exe"
            
        os.chdir("./bin")
        args = r'-displaypatch'
        os.spawnl(os.P_NOWAIT,cmd,args)
            
    except:
        traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        if LOCK:
            LOCK.acquire()
            DISPLAY_SPLASH = False
            LOCK.release()

        win32api.MessageBox(0, "An error was encountered.  If the problem persists please reboot your computer and try again.", "Patcher Error",win32con.MB_OK)
        
    
    if LOCK:
        LOCK.acquire()
        DISPLAY_SPLASH = False
        LOCK.release()
        
    sys.exit()
        

def RunPatcher():
    
    global LOCK
    if sys.platform[:6] != 'darwin' and main_is_frozen():
        import thread
        LOCK = thread.allocate_lock()
        thread.start_new_thread(SplashThread,(None,))
        
    
        pid = -1
        for arg in sys.argv:
            if arg.startswith("-pid="):
                pid = int(arg[5:])
                break
            
        if pid == -1:
            if LOCK:
                LOCK.acquire()
                DISPLAY_SPLASH = False
                LOCK.release()
            win32api.MessageBox(0, 'Error Getting Process ID', "Error",win32con.MB_OK)
            sys.exit()

        

        handle = None
        try:
            #wait for exit
            handle = win32api.OpenProcess(win32con.SYNCHRONIZE|win32con.PROCESS_QUERY_INFORMATION, 0, pid)
            
            if handle:
                result = win32event.WaitForSingleObject(handle,win32event.INFINITE)
                #if result == win32con.WAIT_TIMEOUT:
                #raise "WaitForSingleObject Timed Out"
                win32api.CloseHandle(handle)

        except:
            traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
            try:
                #kill
                handle = win32api.OpenProcess(1, 0, pid)
                if handle:
                    win32api.TerminateProcess(handle,0)
                    win32api.CloseHandle(handle)
            except:
                traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        
        DoPatch()
            
    else:
        #import profile
        #profile.run("main()","profile.prof")
        
        if LOCK:
            
            LOCK.acquire()
            DISPLAY_SPLASH = False
            LOCK.release()


        
        
    
    
    
