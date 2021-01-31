from mud.world.defines import *
from genesis.dbdict import *

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Teleport to grassland"
dialog.name = "TeleportGrasslandTwo"
dialog.greeting = DBDialogLine(text = """You may go back to grassland by stepping into the fireplace.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Kill Mountain Crawlers"
dialog.name = "KillMountainCrawlers"
dialog.greeting = DBDialogLine(text = """Hunt them down and kill them. They carry precious loot.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Setting your bindpoint"
dialog.name = "BindInfoTwo"
dialog.greeting = DBDialogLine(text = """You may choose to set your bindpoint here.\\n""")
dialog.greeting.addChoice(choice)
