# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.gamesettings import *

from math import floor
import traceback,sys

RACEINFO = None
PlayerPerspective = None
DARKNESS = False

#xp penalties up the wazzu

SCORE_CONTROLS = {}
ADJ_CONTROLS = {}
MOD_CONTROLS = {}
TOTAL_CONTROLS = {}

from mud.world.shared.worlddata import NewCharacter            
MyChar = NewCharacter()

def SetRaceInfo(ri):
    global RACEINFO
    RACEINFO = ri

def VerifyCharacter():
    #there has to be a better way of doing this
    race = TGEObject("RacePopup").getText()
    klass = TGEObject("ClassPopup").getText()
    sex = TGEObject("SexPopup").getText()
    
    if RPG_BUILD_DEMO and (DARKNESS or race not in RPG_DEMO_RACES):
        TGEObject("DEMOINFO_BITMAP").setBitmap("~/data/ui/demo/races")        
        TGEObject("DEMOINFOWIND_LATERBUTTON").command = "canvas.popDialog(DemoInfoWnd);"        
        TGEEval("canvas.pushDialog(DemoInfoWnd);")
        return

    name = TGEObject("CharacterNameTextCtrl").getValue()
    if not name or len(name) < 4:
        TGECall("MessageBoxOK","Invalid Character!","Character name must be at least 4 letters.")
        return False

    if len(name) > 11:
        TGECall("MessageBoxOK","Invalid Character!","Character name must be less than 12 letters.")
        return False

    if name.endswith(" "):
        TGECall("MessageBoxOK","Invalid Character!","Character name must not end with a space.")
        return False
    
    if not name.isalpha():
        TGECall("MessageBoxOK","Invalid Character!","Character name must not have numbers or other punctuation.")
        return False
            
    
    
        
    if not race or not len(race):
        TGECall("MessageBoxOK","Invalid Character!","You must choose a race.")
        return False
        
    if not klass or not len(klass):
        TGECall("MessageBoxOK","Invalid Character!","You must choose a class.")
        return False
    
    if not sex or not len(sex):
        TGECall("MessageBoxOK","Invalid Character!","You must choose a sex.")
        return False
    
        
    if MyChar.ptsRemaining:
        TGECall("MessageBoxOK","Invalid Character!","You must spend all your points.")
        return False
        
    return True
    
    
def GotNewCharacterResult(result):
    global PlayerPerspective
    TGECall("CloseMessagePopup")
    
    code = result[0]
    msg = result[1]
    
    if code:
        title = "Error!"
    else:
        #success
        title = "Success!"    
        
        TGEObject("CharacterNameTextCtrl").setValue("")    
    
    if not code:
        try:
            nc = TGEObject("NEWCHAR_GUIOBJECTVIEW")
            nc.setEmpty()
        except:
            traceback.print_exc()
        
        from worldGui import Setup
        #back to world in a hackish manner
        Setup(PlayerPerspective,True)
        
        PlayerPerspective = None
        
        TGECall("MessageBoxOK",title,msg)
        
    else:
        
        TGECall("MessageBoxOK",title,msg)
        
def OnNewCharacterSubmit():
    
    
    race = TGEObject("RacePopup").getText()
    
    if not VerifyCharacter():
        return
        
    
    klass = TGEObject("ClassPopup").getText()
    sex = TGEObject("SexPopup").getText()

        
    name = TGEObject("CharacterNameTextCtrl").getValue()    
    name = name.capitalize()
    MyChar.name = name
    MyChar.sex = sex
    MyChar.klass = klass
    MyChar.race = race
    if DARKNESS:
        MyChar.realm = RPG_REALM_DARKNESS
    else:
        MyChar.realm = RPG_REALM_LIGHT
        
    
    if int(TGEObject("NEWCHARACTER_HEAVY").getValue()):
        MyChar.look=2
    if int(TGEObject("NEWCHARACTER_SLIGHT").getValue()):
        MyChar.look=0
    if int(TGEObject("NEWCHARACTER_MUSCULAR").getValue()):
        MyChar.look=1
    
    
    TGECall("MessagePopup","Submitting Character...","Please wait...")
    PlayerPerspective.callRemote("PlayerAvatar","newCharacter",MyChar).addCallbacks(GotNewCharacterResult,Failure)    

        
def OnModelChanged():
    
    race = TGEObject("RacePopup").getText()
    
    for ri in RACEINFO:
        if ri.name == race:
            break
    
    if int(TGEObject("NEWCHARACTER_HEAVY").getValue()):
        look=2
    if int(TGEObject("NEWCHARACTER_SLIGHT").getValue()):
        look=0
    if int(TGEObject("NEWCHARACTER_MUSCULAR").getValue()):
        look=1
        
    sex = TGEObject("SexPopup").getText()
    
    try:
        nc = TGEObject("NEWCHAR_GUIOBJECTVIEW")
        
        
        nc.unmountObject("Sword1", "mount0")
        nc.unmountObject("Sword2", "mount1")
        
        size = 1.0
        model = ""
        animation = ""
        if sex == "Female":
            size = ri.size_female
            animation = ri.animation_female
            texhead = ri.texture_head_female
            texbody = ri.texture_body_female
            texarms = ri.texture_arms_female
            texlegs = ri.texture_legs_female
            texhands = ri.texture_hands_female
            texfeet = ri.texture_feet_female
            texspecial = ri.texture_special_female
            if look == 0:
                model = ri.model_thin_female
            if look == 1:
                model = ri.model_fit_female
            if look == 2:
                model = ri.model_heavy_female
                
        elif sex == "Male":
            size = ri.size_male
            animation = ri.animation_male
            texhead = ri.texture_head_male
            texbody = ri.texture_body_male
            texarms = ri.texture_arms_male
            texlegs = ri.texture_legs_male
            texhands = ri.texture_hands_male
            texfeet = ri.texture_feet_male
            texspecial = ri.texture_special_male
            if look == 0:
                model = ri.model_thin_male
            if look == 1:
                model = ri.model_fit_male
            if look == 2:
                model = ri.model_heavy_male

        
        modelname = "~/data/shapes/character/models/%s.dts"%model
        
        nc.setEmpty()
        nc.setObject("PlayerModel", modelname, "", 0);
        nc.setSkin(0,"~/data/shapes/character/textures/%s"%texhead)#head
        nc.setSkin(1,"~/data/shapes/character/textures/%s"%texarms)#arms
        nc.setSkin(2,"~/data/shapes/character/textures/%s"%texlegs)#legs
        nc.setSkin(3,"~/data/shapes/character/textures/%s"%texfeet)#feet
        nc.setSkin(4,"~/data/shapes/character/textures/%s"%texhands)#hands
        nc.setSkin(5,"~/data/shapes/character/textures/%s"%texbody)#body
        if texspecial:
            nc.setSkin(6,"~/data/shapes/character/textures/%s"%texspecial)

        if animation:
            nc.loadDSQ("PlayerModel","~/data/shapes/character/animations/%s/idle.dsq"%animation)
        nc.setSequence("PlayerModel","idle",1)
        
        nc.mountObject("Sword1", "~/data/shapes/equipment/weapons/sword01.dts", "", "PlayerModel", "mount0", 0)
        nc.mountObject("Sword2", "~/data/shapes/equipment/weapons/sword01.dts", "", "PlayerModel", "mount1", 0)
        #nc.mountObject("Shield", "~/data/shapes/equipment/weapons/shield03.dts", "", "PlayerModel", "mount2", 0)
    except:
        traceback.print_exc()
    
    
def OnLookChanged():
    OnModelChanged()

def OnGenderChanged():
    OnModelChanged()
        
        
def OnRaceChanged():
    
    race = TGEObject("RacePopup").getText()

    ma = TGEObject("MOM_AVAILABLE")
    ma.visible = False
    ma.setActive(False)
        
    
    if RPG_BUILD_DEMO and (race not in RPG_DEMO_RACES or DARKNESS):
        ma.visible = True
    
    
    rstat = RPG_RACE_STATS[race]
    MyChar.scores['STR']=rstat.STR
    MyChar.scores['DEX']=rstat.DEX
    MyChar.scores['REF']=rstat.REF
    MyChar.scores['AGI']=rstat.AGI
    MyChar.scores['BDY']=rstat.BDY
    MyChar.scores['MND']=rstat.MND
    MyChar.scores['WIS']=rstat.WIS
    MyChar.scores['MYS']=rstat.MYS
    
       
    classes = TGEObject("ClassPopup")
    classes.clear()
    clist = RPG_RACE_CLASSES[race]
    clist.sort()
    x=0
    for s in clist:
        if DARKNESS:
            if s not in RPG_REALM_CLASSES[RPG_REALM_DARKNESS]:
                continue
        else:
            if s not in RPG_REALM_CLASSES[RPG_REALM_LIGHT]:
                continue

        classes.add(s,x)
        x+=1
         
    SetControlsFromChar()
    
    TGEObject("ClassPopup").setSelected(0)
    
    OnModelChanged()

def SetControlsFromChar():
    #stats+="""\cp\c2+%s\co"""%str(value)+" " <--- Green
    #stats+="""\cp\c1%s\co"""%str(value)+" " <--- Red
    
    TGEObject("NEWCHARPOINTSREMAINING").setText("Points Remaining: %s"%MyChar.ptsRemaining)
    
    for st in RPG_STATS:
        SCORE_CONTROLS[st].setText(MyChar.scores[st])
        total = MyChar.adjs[st] + MyChar.scores[st]
        
        if MyChar.adjs[st]:
            TGEEval(r'%s_ADJ.setText("\c2%i");'%(st,MyChar.adjs[st]))
            TGEEval(r'%s_TOTAL.setText("\c2%i");'%(st,total))
        else:
            TOTAL_CONTROLS[st].setText(total)
            ADJ_CONTROLS[st].setText(0)
        
        

def OnAddStat(args):
    statname = args[1]
    if MyChar.ptsRemaining >= 1:
        
        if MyChar.adjs[statname]<50:
            MyChar.ptsRemaining -= 5
            MyChar.adjs[statname]+=5
        
        SetControlsFromChar()

def OnSubStat(args):
    statname = args[1]
    
    if not MyChar.adjs[statname]:
        return
        
    MyChar.ptsRemaining += 5
    MyChar.adjs[statname]-=5
    SetControlsFromChar()
        
def Failure(reason):
    TGECall("CloseMessagePopup")
    TGECall("MessageBoxOK","Error!",reason)        
    
def Setup(playerperp,darkness=False):
    
    ma = TGEObject("MOM_AVAILABLE")
    ma.visible = False
    ma.setActive(False)
    
    global PlayerPerspective
    global DARKNESS
    DARKNESS = darkness
    PlayerPerspective = playerperp
    
    MyChar.reset()
    
    for s in RPG_STATS:
        MyChar.adjs[s]=0
        
    MyChar.ptsRemaining = 100

    
    TGEObject("NEWCHARGUI_PORTRAITBUTTON").setBitmap("~/data/ui/charportraits/%s"%MyChar.portraitPic)
    
    #setup controls
    for s in RPG_STATS:
        SCORE_CONTROLS[s]=TGEObject("%s_SCORE"%s)
        ADJ_CONTROLS[s]=TGEObject("%s_ADJ"%s)
        TOTAL_CONTROLS[s]=TGEObject("%s_TOTAL"%s)
    
    rctrl = TGEObject("RacePopup")
    rctrl.clear()
    x=0
    races = []
    for r in RACEINFO:
        races.append(r.name)
    
    races.sort()

    for r in races:
        rctrl.add(r,x)
        x+=1

    sexes = TGEObject("SexPopup")
    sexes.clear()
    x=0
    for s in ["Male","Female"]:
        sexes.add(s,x)
        x+=1
        
    TGEEval("canvas.setContent(NewCharacterGui);")
    
    
    TGEObject("NEWCHARACTER_HEAVY").setValue(0)
    TGEObject("NEWCHARACTER_SLIGHT").setValue(0)
    TGEObject("NEWCHARACTER_MUSCULAR").setValue(1)

    TGEObject("RacePopup").setSelected(0)
    TGEObject("SexPopup").setSelected(0)
    
    
    OnRaceChanged()
    
    SetControlsFromChar()
    
    TGEObject("CharacterNameTextCtrl").makeFirstResponder(1)

def OnNewCharacterCancel():
    global PlayerPerspective
    from worldGui import Setup
    #back to world in a hackish manner
    Setup(PlayerPerspective)
        
    PlayerPerspective = None
    

def ChoosePortrait(chosen):
    if not chosen:
        return
        
    from charPortraitWnd import SetChoosePortraitCallback
    
    MyChar.portraitPic = chosen
    TGEObject("NEWCHARGUI_PORTRAITBUTTON").setBitmap("~/data/ui/charportraits/%s"%chosen)
    
    

def OnNewCharChoosePortrait():
    from charPortraitWnd import SetChoosePortraitCallback
    SetChoosePortraitCallback(ChoosePortrait)
    TGEEval("canvas.pushDialog(CharPortraitWnd);")
    
#Py::OnDefaultStats();    


def OnDefaultStats():
    klass = TGEObject("ClassPopup").getText()
    
    if RPG_DEFAULT_STATS.has_key(klass):
        MyChar.ptsRemaining = 0
        MyChar.adjs= {}
        for stat,value in zip(RPG_STATS,RPG_DEFAULT_STATS[klass]):
            MyChar.adjs[stat]=value
            
        SetControlsFromChar()

    

def PyExec():
    
    TGEExport(OnNewCharacterSubmit,"Py","OnNewCharacterSubmit","desc",1,1)
    TGEExport(OnNewCharacterCancel,"Py","OnNewCharacterCancel","desc",1,1)
    TGEExport(OnAddStat,"Py","OnAddStat","desc",2,2)
    TGEExport(OnSubStat,"Py","OnSubStat","desc",2,2)
    TGEExport(OnRaceChanged,"Py","OnRaceChanged","desc",1,1)
    TGEExport(OnGenderChanged,"Py","OnGenderChanged","desc",1,1)
    TGEExport(OnLookChanged,"Py","OnLookChanged","desc",1,1)
    
    TGEExport(OnDefaultStats,"Py","OnDefaultStats","desc",1,1)
    
    TGEExport(OnNewCharChoosePortrait,"Py","OnNewCharChoosePortrait","desc",1,1)