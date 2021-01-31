from mud.world.defines import *
from genesis.dbdict import *

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Teleport to grassland"
dialog.name = "TeleportGrasslandOne"
dialog.greeting = DBDialogLine(text = """You may go back to grassland by stepping into the fireplace.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Kill Swamp Walkers"
dialog.name = "KillSwampWalkers"
dialog.greeting = DBDialogLine(text = """Hunt them down and kill them. They carry precious loot.\\n""")
dialog.greeting.addChoice(choice)
action = DBDialogAction()
action.endInteraction = True

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Setting your bindpoint"
dialog.name = "BindInfoOne"
dialog.greeting = DBDialogLine(text = """You may choose to set your bindpoint here.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

action1 = DBDialogAction()
action1.teleportZone="landone"
action1.teleportTransform="8.18327 410.594 120.95 1 0 0 0"
action1.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

choice1 = DBDialogChoice(text = "Teleport me.")
choice1.successLine = DBDialogLine(text = "")
choice1.successLine.addAction(action1)

dialog = DBDialog()
dialog.title = "To the lake"
dialog.name = "ToLake"
dialog.greeting = DBDialogLine(text = """This teleporter will bring you to the swimming lake.\\n""")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

action1 = DBDialogAction()
action1.teleportZone="landone"
action1.teleportTransform="15.5326 -267.211 124.9 1 0 0 0"
action1.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

choice1 = DBDialogChoice(text = "Teleport me.")
choice1.successLine = DBDialogLine(text = "")
choice1.successLine.addAction(action1)

dialog = DBDialog()
dialog.title = "Back from swimming"
dialog.name = "ToCentral"
dialog.greeting = DBDialogLine(text = """This teleporter brings you back to the central area.\\n""")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice)
