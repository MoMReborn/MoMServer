import math
from genesis.dbdict import DBDialog,DBDialogLine,DBDialogChoice,DBDialogAction,DBDialogRequirement
from mud.world.defines import *

req = DBDialogRequirement()
req.requireClassNumber = 3
req.positiveCheck = False

def MakeClassTrainer(className,costgold, greetText,successText,failureText):
    costpp = costgold/100
    if costpp:
        costgold = costgold-costpp*100
    
    if costpp:
        money = "%i platinum pieces"%costpp
        if costgold:
            money = money[:-6]
            money+="and %i gold pieces"%costgold
    else:
        money = "%i gold pieces"%costgold
        
    
    greeting = DBDialogLine(text = greetText)
    
    choiceconfirm = DBDialogChoice(text=r'Yes, I want to train in the %s class for %s.'%(className,money))        
    choiceconfirm.failLine = DBDialogLine(text=failureText)
    choiceconfirm.successLine = DBDialogLine(text=successText)
    
    choicecancel = DBDialogChoice(text=r'No, I have chosen to reconsider.')        

    classReq = DBDialogRequirement()
    classReq.addClassRequirement(False,className)
    
    choice = DBDialogChoice(text=r'Train in the %s class for %s.'%(className,money))
    choice.addRequirement(req)
    choice.addRequirement(classReq)
    
    choice.successLine = DBDialogLine(text="\\nDo you really want to train in the %s for %s?\\n"%(className,money))
    choice.successLine.addChoice(choiceconfirm)
    choice.successLine.addChoice(choicecancel)
    
    action = DBDialogAction()
    action.takeGold = costgold
    action.takePlatinum = costpp
    action.trainClass = className
    
    choiceconfirm.successLine.addAction(action)
    
    greeting.addChoice(choice)
    
    dialog = DBDialog(name="%s Trainer"%className,greeting = greeting)
    
    
#--- Necromancer

greetLine = "Hrmph!  Decide quickly if you desire instruction in the art of Necromancy!\\n"
successLine = "\\nAlthough you aren't worthy, I will teach you\\n"
failLine = "\\nI'm sorry I cannot train you in the Necromancer class at this time.\\n" 

MakeClassTrainer("Necromancer",100,greetLine,successLine,failLine)

#--- Warrior

greetLine = "Ho!  Blood and gore!!  Do you need to know more?!?!?!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Warrior class at this time.\\n" 

MakeClassTrainer("Warrior",50,greetLine,successLine,failLine)

#--- Bard



greetLine = "For a price, I'll train you to be a bard!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Bard class at this time.\\n" 

MakeClassTrainer("Bard",60,greetLine,successLine,failLine)

#--- Ranger



greetLine = "For a price, I'll train you to be a ranger!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Ranger class at this time.\\n" 

MakeClassTrainer("Ranger",90,greetLine,successLine,failLine)


#--- Cleric


greetLine = "For a price, I'll train you to be a cleric!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Cleric class at this time.\\n" 

MakeClassTrainer("Cleric",54,greetLine,successLine,failLine)


#--- Wizard



greetLine = "Yes I know, I am huge!  It's a damned curse, ok!  Do you need training in the ways of the wizard or not?!?!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Wizard class at this time.\\n" 

MakeClassTrainer("Wizard",90,greetLine,successLine,failLine)
    
#--- Druid



greetLine = "For a price, I'll train you to be a druid!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Druid class at this time.\\n" 

MakeClassTrainer("Druid",20,greetLine,successLine,failLine)


#--- Revealer
greetLine = "For a price, I'll train you in the zany ways of the revealer!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Revealer class at this time.\\n" 

MakeClassTrainer("Revealer",95,greetLine,successLine,failLine)

#--- Paladin


greetLine = "For a price, I'll train you in the ways of the paladin!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Paladin class at this time.\\n" 

MakeClassTrainer("Paladin",110,greetLine,successLine,failLine)


#--- Monk

greetLine = "For a price, I'll train you in the ways of the monk!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Monk class at this time.\\n" 

MakeClassTrainer("Monk",10,greetLine,successLine,failLine)

#--- Tempest

greetLine = "For a price, I'll train you in the ways of the tempest!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Tempest class at this time.\\n" 

MakeClassTrainer("Tempest",90,greetLine,successLine,failLine)

#--- Shaman

greetLine = "For a price, I'll train you in the ways of the shaman!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Shaman class at this time.\\n" 

MakeClassTrainer("Shaman",5,greetLine,successLine,failLine)


#--- Barbarian

greetLine = "For a price, I'll train you in the ways of the barbarian!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Barbarian class at this time.\\n" 

MakeClassTrainer("Barbarian",40,greetLine,successLine,failLine)

#--- Assassin

greetLine = "For a price, I'll train you in the ways of the assassin!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Assassin class at this time.\\n" 

MakeClassTrainer("Assassin",100,greetLine,successLine,failLine)
    

#--- Thief

greetLine = "For a price, I'll train you in the ways of the scout!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Thief class at this time.\\n" 

MakeClassTrainer("Thief",30,greetLine,successLine,failLine)
    
#--- Doom Knight

greetLine = "For a price, I'll train you in the ways of the mercenary!\\n"
successLine = "\\nAlright, here's what you need to know.\\n"
failLine = "\\nI'm sorry I cannot train you in the Doom Knight class at this time.\\n" 

MakeClassTrainer("Doom Knight",50,greetLine,successLine,failLine)






