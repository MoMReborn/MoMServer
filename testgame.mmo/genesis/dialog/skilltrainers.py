import math

from genesis.dbdict import DBDialog,DBDialogLine,DBDialogChoice,DBDialogAction,DBDialogRequirement
from mud.world.defines import *
from mud.world.core import GenMoneyText


def MakeSkillTrainer(skillName,cost):
    tin = long(cost[0])
    tin += cost[1] * 100L
    tin += cost[2] * 10000L
    tin += cost[3] * 1000000L
    tin += cost[4] * 100000000L
    money = GenMoneyText(tin)
    
    action = DBDialogAction()
    action.takeTin = tin
    action.trainSkill(skillName)
    
    skillReq = DBDialogRequirement()
    skillReq.addSkillRequirement(False,skillName)
    
    
    choice = DBDialogChoice(text=r'Learn the %s skill for %s.'%(skillName,money))
    choice.failLine = DBDialogLine(text= \
           "\\nI cannot teach you the %s skill at this time.\\n"%skillName)
    choice.successLine = DBDialogLine(text= \
           "\\nAlright, here's what you need to know!\\n")
    choice.successLine.addAction(action)
    choice.addRequirement(skillReq)
    
    greeting = DBDialogLine(text= \
               "Hello, would you like to learn the %s skill?\\n"%skillName)
    greeting.addChoice(choice)
    
    dialog = DBDialog(name="%s Trainer"%skillName,greeting=greeting)

MakeSkillTrainer("Healing Hands",(10,1,0,0,0))
MakeSkillTrainer("Archery",(10,1,0,0,0))
MakeSkillTrainer("Cooking",(10,1,0,0,0))
MakeSkillTrainer("Brewing",(10,1,0,0,0))
MakeSkillTrainer("Dual Wield",(10,1,0,0,0))
