from mud.world.defines import *
from genesis.dbdict import *

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

action1 = DBDialogAction()
action1.giveMonster = "Wolf"
action1.endInteraction = True

choice1 = DBDialogChoice(text = "Give me the wolf template.")
choice1.successLine = DBDialogLine(text = "")
choice1.successLine.addAction(action1)

action2 = DBDialogAction()
action2.giveMonster = "Dog"
action2.endInteraction = True

choice2 = DBDialogChoice(text = "Give me the dog template.")
choice2.successLine = DBDialogLine(text = "")
choice2.successLine.addAction(action2)

action3 = DBDialogAction()
action3.giveMonster = "Rolf"
action3.endInteraction = True

choice3 = DBDialogChoice(text = "Give me the rolf template.")
choice3.successLine = DBDialogLine(text = "")
choice3.successLine.addAction(action3)

dialog = DBDialog()
dialog.title = "Welcome to the Demo Game"
dialog.name = "Welcome"
dialog.greeting = DBDialogLine(text = """If you turn around and walk up the hill you'll find some interesting places. We put up some more places to play around. Kill wolves, try to find and sell some stones. You can even start an epic battle, be sure to claim your reward afterwards.\\nAs a paladin you can learn a healing skill. As a wizard you can learn two combat spells. As a druid you can learn to summon pets. As a bard yu can learn a spell to make your whole party fly.\\nTry to earn some money, learn archery and buy yourself bow and arrows. Take some monster templates and play a dog, wolf or rolf. You can also walk along the path and watch some fighters. Or visit wolfman, he'll give you a quest.\\n""")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice2)
dialog.greeting.addChoice(choice3)
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Teleport to the land of mountains"
dialog.name = "TeleportMountains"
dialog.greeting = DBDialogLine(text = """You may visit the land of mountains by stepping into the fireplace.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Teleport to the land of swamps"
dialog.name = "TeleportSwamps"
dialog.greeting = DBDialogLine(text = """You may visit the land of swamps by stepping into the fireplace.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Reference objects"
dialog.name = "RefObject"
dialog.greeting = DBDialogLine(text = """This are some reference objects. They can be useful to compare size and rotation when importing objects from your favorite 3D modeling program. And they can be used to visualize dimensions ingame.\\n\\nThe cube is exactly 2 units each side and shows the positive directions of the coordinate axes.\\nThe pole is 2 units long, the rings are 2 units in diameter and 4 units in height.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about aggroranges"
dialog.name = "AggroDemo"
dialog.greeting = DBDialogLine(text = """Enemies have different aggroranges. Here we made them visible for you.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about assisting"
dialog.name = "AggroHelp"
dialog.greeting = DBDialogLine(text = """Be warned, wolves help each other. Dogs don't.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Rolf the Wolf"
dialog.name = "RolfWolf"
dialog.greeting = DBDialogLine(text = """This is Rolf the stonebearer. Kill him but try to avoid his minions. We made the waypoints visible to give you a little help.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about vendors"
dialog.name = "VendorInfo"
dialog.greeting = DBDialogLine(text = """This vendor will buy and sell strange stones.\\n""")
dialog.greeting.addChoice(choice)

dialog = DBDialog()
dialog.name = "Stone Vendor Dialog"
dialog.greeting = DBDialogLine()
dialog.greeting.text = "Stones are my life!"

dialog = DBDialog()
dialog.name = "Scroll Vendor Dialog"
dialog.greeting = DBDialogLine()
dialog.greeting.text = "I deal scrolls!"

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about vendors"
dialog.name = "ScrollVendorInfo"
dialog.greeting = DBDialogLine(text = """This vendor will buy and sell scrolls.\\n""")
dialog.greeting.addChoice(choice)

dialog = DBDialog()
dialog.name = "Skill Trainer Dialog"
dialog.greeting = DBDialogLine()
dialog.greeting.text = "I train skills!"
traindialog1 = DBDialog.getDBDialog('Healing Hands Trainer')
traindialog2 = DBDialog.getDBDialog('Archery Trainer')
traindialog3 = DBDialog.getDBDialog('Cooking Trainer')
traindialog4 = DBDialog.getDBDialog('Brewing Trainer')
traindialog5 = DBDialog.getDBDialog('Dual Wield Trainer')
dialog.addDialog(traindialog1)
dialog.addDialog(traindialog2)
dialog.addDialog(traindialog3)
dialog.addDialog(traindialog4)
dialog.addDialog(traindialog5)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about trainers"
dialog.name = "TrainerInfo"
dialog.greeting = DBDialogLine(text = """This trainer will teach you skills.\\n""")
dialog.greeting.addChoice(choice)

dialog = DBDialog()
dialog.name = "Weapon Vendor Dialog"
dialog.greeting = DBDialogLine()
dialog.greeting.text = "I deal weapons!"

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about vendors"
dialog.name = "WeaponVendorInfo"
dialog.greeting = DBDialogLine(text = """This vendor will buy and sell weapons.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

action1 = DBDialogAction()
action1.addFaction("The Red",-50)
action1.addFaction("The Green",100)
action1.addFaction("The Blue",-50)
action1.endInteraction = True

action2 = DBDialogAction()
action2.addFaction("The Red",100)
action2.addFaction("The Green",-50)
action2.addFaction("The Blue",-50)
action2.endInteraction = True

action3 = DBDialogAction()
action3.addFaction("The Red",-50)
action3.addFaction("The Green",-50)
action3.addFaction("The Blue",100)
action3.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

choice1 = DBDialogChoice(text = "Support the Green.")
choice1.successLine = DBDialogLine(text = "")
choice1.successLine.addAction(action1)

choice2 = DBDialogChoice(text = "Support the Red.")
choice2.successLine = DBDialogLine(text = "")
choice2.successLine.addAction(action2)

choice3 = DBDialogChoice(text = "Support the Blue.")
choice3.successLine = DBDialogLine(text = "")
choice3.successLine.addAction(action3)

dialog = DBDialog()
dialog.title = "Learning about factions"
dialog.name = "FactionInfo"
dialog.greeting = DBDialogLine(text = """Here you can decide how to stand with the factions of The Red, The Green or The Blue.\\n\\nSupport the faction of your choice but be aware, the others will form an alliance against you.\\n""")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice2)
dialog.greeting.addChoice(choice3)
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

action1 = DBDialogAction()
action1.triggerSpawnGroup = "TRWOLFANDDOGSP"
action1.endInteraction = True
action1a = DBDialogAction()
action1a.endInteraction = True

action2 = DBDialogAction()
action2.triggerSpawnGroup = "TRROLFSP"
action2.endInteraction = True
action2a = DBDialogAction()
action2a.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

choice1 = DBDialogChoice(text = "Summon Rolf's minions.")
choice1.successLine = DBDialogLine(text = "")
choice1.successLine.addAction(action1)
choice1.failLine = DBDialogLine(text = "They are already here!")
choice1.failLine.addAction(action1a)

choice2 = DBDialogChoice(text = "Summon Rolf.")
choice2.successLine = DBDialogLine(text = "")
choice2.successLine.addAction(action2)
choice2.failLine = DBDialogLine(text = "He is already here!")
choice2.failLine.addAction(action2a)

dialog = DBDialog()
dialog.title = "Learning about triggered spawns"
dialog.name = "TriggeredSpawnInfo"
dialog.greeting = DBDialogLine(text = """You may order to summon a Rolf or a Wolf. Find out the difference.\\n""")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice2)
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
dialog.name = "BindInfoBase"
dialog.greeting = DBDialogLine(text = """You may choose to set your bindpoint here.\\n""")
dialog.greeting.addChoice(choice)

dialog = DBDialog()
dialog.name = "Food Vendor Dialog"
dialog.greeting = DBDialogLine()
dialog.greeting.text = "Snacks for all... who can afford it!"

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about vendors"
dialog.name = "FoodvendorInfo"
dialog.greeting = DBDialogLine(text = """This vendor will buy and sell food and drinks.\\n""")
dialog.greeting.addChoice(choice)
action = DBDialogAction()
action.endInteraction = True

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about fights"
dialog.name = "FightInfo"
dialog.greeting = DBDialogLine(text = """The fighters and the wolves will walk into each other and fight.\\n""")
dialog.greeting.addChoice(choice)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "Learning about quests"
dialog.name = "QuestInfo"
dialog.greeting = DBDialogLine(text = """Wolfman has a quest for you.\\n""")
dialog.greeting.addChoice(choice)

action1 = DBDialogAction()
action1.journalTopic = "Wolves"
action1.journalEntry = "The Wolf quest"
action1.journalText = "Kill some wolves and bring Wolfman a Grey Wolf Hide and Wolf Meat."
action1.endInteraction = True

action2 = DBDialogAction()
action2.endInteraction = True

action3 = DBDialogAction()
action3.endInteraction = True

action4 = DBDialogAction()
action4.addTakeItem("Grey Wolf Hide")
action4.addTakeItem("Wolf Meat")
action4.addGiveItem("Strange stone")
action4.journalTopic = "Wolves"
action4.journalEntry = "The Wolf quest"
action4.journalText = "You have received the stone and solved the wolf quest."
action4.endInteraction = True

choice1 = DBDialogChoice(text = "I'll do that for you.")
choice1.successLine = DBDialogLine(text = "Good.")
choice1.successLine.addAction(action1)
choice1.identifier = "Wolfman Quest"
choice1.maxTimes = 1

choice2 = DBDialogChoice(text = "Exit.")
choice2.successLine = DBDialogLine(text = "Come back later.")
choice2.successLine.addAction(action2)

choice3 = DBDialogChoice(text = "I have the Items!")
choice3.successLine = DBDialogLine(text = "Well done. Let me give you the desired stone!")
choice3.successLine.addAction(action4)
choice3.failLine = DBDialogLine(text = "You are mistaken or a buffoon. Probably both!")
choice3.failLine.addAction(action3)
choice3.identifier = "Wolfman Quest"
choice3.maxTimes = 1
choice3.maxBump = True

dialog = DBDialog()
dialog.name = "The Wolf Quest"
dialog.greeting = DBDialogLine(text = "Kill some wolves and bring me a Grey Wolf Hide and Wolf Meat.")
dialog.greeting.addChoice(choice1)
dialog.greeting.addChoice(choice3)
dialog.greeting.addChoice(choice2)

#--- HumanWolfSkirmishReward Dialog
action = DBDialogAction()
action.giveGold = 10
action.despawn = True

choice = DBDialogChoice(text=r'Take reward.')
choice.successLine = DBDialogLine(text="""Thanks for alerting us! Please accept this
gift in gratitude! Goodbye.""")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.name = "HumanWolfSkirmishReward"
dialog.greeting = DBDialogLine()
dialog.greeting.text = """Thank you for helping us defeat the legions of Captain Flamehorn!\\n"""
dialog.greeting.addChoice(choice)

#--- HumanWolfSkirmish Dialog
action1 = DBDialogAction()
action1.endInteraction = True

action2 = DBDialogAction()
action2.triggerBattle = "HumanWolfSkirmish"
action2.endInteraction = True

choice = DBDialogChoice(text=r'I prepared myself and want the battle to start now.')
choice.successLine = DBDialogLine(text="Make haste to the battle!")
choice.successLine.addAction(action2)

choice2 = DBDialogChoice(text=r'I will let you know if I find anything.')
choice2.successLine = DBDialogLine(text="Be careful!")
choice2.successLine.addAction(action1)

dialog = DBDialog()
dialog.name = "HumanWolfSkirmish"
dialog.greeting = DBDialogLine(text = """Be watchful around these parts. There are rumors of wolf packs mobilizing! Please report back to me if you come across any useful information!\\n""")
dialog.greeting.addChoice(choice)
dialog.greeting.addChoice(choice2)

action = DBDialogAction()
action.endInteraction = True

choice = DBDialogChoice(text = "Exit.")
choice.successLine = DBDialogLine(text = "")
choice.successLine.addAction(action)

dialog = DBDialog()
dialog.title = "AI Collision Demo"
dialog.name = "AICollision"
dialog.greeting = DBDialogLine(text = """Watch one fighter stepping over the obstacle while the other walks right trough it. The AICollision flag sets DTS objects to npc collidable. Be careful, there is no pathfinding so npcs easily get stuck.\\n""")
dialog.greeting.addChoice(choice)
