from genesis.dbdict import DBDialog,DBDialogLine,DBDialogChoice,DBDialogAction
from mud.world.defines import *



#ghetto resurrection, hey it's free

action = DBDialogAction()

action.resurrect = True
action.playSound = "sfx/Pickup_HolyCross.ogg"

choice = DBDialogChoice(text = "Resurrect with no XP recovery for free.")
choice.failLine = DBDialogLine(text = "\\nI don't see anyone in need of resurrection!\\n")
choice.successLine = DBDialogLine(text = "\\nBring out yer dead!\\n")
choice.successLine.addAction(action)


action2 = DBDialogAction()
action2.resurrect = True
action2.resurrectXP = .5
action2.takeSilver = 10
choice2 = DBDialogChoice(text = "Resurrect with 50% XP recovery for 10 sp.")
choice2.failLine = DBDialogLine(text = "\\nBah!\\n")
choice2.successLine = DBDialogLine(text = "\\nBring out yer dead!\\n")
choice2.successLine.addAction(action2)


dialog = DBDialog()
dialog.name = "Ghetto Resurrection"
dialog.greeting = DBDialogLine(text = "This will never be displayed.  This is inserted into existing spawn dialog.")
dialog.greeting.addChoice(choice)
dialog.greeting.addChoice(choice2)







