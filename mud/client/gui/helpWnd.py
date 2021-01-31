# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.gamesettings import GAMEROOT


HELPTEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:20>Online Help
<font:Arial:16>
<color:BBBBFF>Mouse<just:left><font:Arial:13>

<color:FFFF00>OSX Note:<color:BBFFBB> Command click simulates a right click 

<color:FFFFFF>Left + Right Click <color:BBAAAA><color:BBFFBB> - Move Forward
<color:FFFFFF>Left Click <color:BBAAAA>on npc, monster, or player avatar <color:BBFFBB> - Select
<color:FFFFFF>Shift + Left Click <color:BBAAAA>on npc, monster, or player avatar <color:BBFFBB> - Inspect
<color:FFFFFF>Left Click <color:BBAAAA>on quick slot or macro slot <color:BBFFBB> - Activate
<color:FFFFFF>Shift + Left Click <color:BBAAAA>on macro slot <color:BBFFBB> - Stop running Macro
<color:FFFFFF>Left Click <color:BBAAAA>on target health bar with player targeted <color:BBFFBB> - Cycle Targets
<color:FFFFFF>Left Click <color:BBAAAA>on character name in Alliance window <color:BBFFBB> - Target Character
<color:FFFFFF>Left Click <color:BBAAAA>on character portrait <color:BBFFBB> - Set Active Character
<color:FFFFFF>Left Click <color:BBAAAA>on spell button in spell book <color:BBFFBB> - Cast the Spell
<color:FFFFFF>Left Click <color:BBAAAA>on skill button <color:BBFFBB> - Activate the Skill

<color:FFFFFF>Right Click <color:BBAAAA>and hold on world view <color:BBFFBB> - Enable Mouse Look
<color:FFFFFF>Right Click <color:BBAAAA>on inventory item <color:BBFFBB> - Toggle Item Information
<color:FFFFFF>Right Click <color:BBAAAA>on spellbook icon <color:BBFFBB> - Toggle Spell Information
<color:FFFFFF>Right Click <color:BBAAAA>on character portrait <color:BBFFBB> - Target Character

<color:FFFFFF>Double Click <color:BBAAAA>on npc <color:BBFFBB> - Interact
<color:FFFFFF>Double Click <color:BBAAAA>on enemy <color:BBFFBB> - Attack
<color:FFFFFF>Double Click <color:BBAAAA>on inventory item <color:BBFFBB> - Equip (if possible)
<color:FFFFFF>SHIFT + Double Click <color:BBAAAA>on inventory item <color:BBFFBB> - Quick Sell
<color:FFFFFF>Double Click <color:BBAAAA>on Destroy Corpse <color:BBFFBB> - Quick Destroy
<color:FFFFFF>Double Click <color:BBAAAA>on player with item in cursor <color:BBFFBB> - Trade
<color:FFFFFF>Double Click <color:BBAAAA>on pet with item in cursor (twice) <color:BBFFBB> - Equip Pet
<color:FFFFFF>Double Click <color:BBAAAA>on character portrait <color:BBFFBB> - Open Stat Pane
<color:FFFFFF>Double Click <color:BBAAAA>on vendor item <color:BBFFBB> - Quick Buy
<color:FFFFFF>Double Click <color:BBAAAA>on dialog choice <color:BBFFBB> - Select Choice
<color:FFFFFF>Double Click <color:BBAAAA>on corpse <color:BBFFBB> - Loot Corpse
<color:FFFFFF>Double Click <color:BBAAAA>on loot item <color:BBFFBB> - Quick Loot
<color:FFFFFF>Double Click <color:BBAAAA>on nonharmful effect icon <color:BBFFBB> - Cancel Effect
<color:FFFFFF>Double Click <color:BBAAAA>on skill or spell and drop in macro slot <color:BBFFBB> - Create Macro

<color:FFFF00>Item Linking:<color:BBFFBB> For many areas of the UI, such as inventory window, spell book, skill listing, and effects window:

<color:FFFFFF>Shift + Left Click <color:BBAAAA><color:BBFFBB> - Opens encyclopedia to appropriate page.
<color:FFFFFF>Shift + Right Click <color:BBAAAA><color:BBFFBB> - Places link in chat.

<font:Arial:16><just:center>
<color:BBBBFF>Default Keyboard<just:left><font:Arial:13>

<color:FFFFFF>ESCAPE <color:BBFFBB> - Options

<color:FFFFFF>W <color:BBFFBB> - Run Forward
<color:FFFFFF>S <color:BBFFBB> - Run Backwards
<color:FFFFFF>A <color:BBFFBB> - Sidestep Left
<color:FFFFFF>D <color:BBFFBB> - Sidestep Right    
<color:FFFFFF>Q <color:BBFFBB> - Turn Left
<color:FFFFFF>E <color:BBFFBB> - Turn Right
<color:FFFFFF>SPACE <color:BBFFBB> - Jump

<color:FFFFFF>V <color:BBFFBB> - Toggle Auto-Run

<color:FFFFFF>/ <color:BBFFBB> - Toggle Tome Command Input
<color:FFFFFF>ENTER <color:BBFFBB> - Toggle Tome Chat Input

<color:FFFFFF>X <color:BBFFBB> - Toggle Mouse Look (right mouse button also toggles Mouse Look)
<color:FFFFFF>Z <color:BBFFBB> - Squint

<color:FFFFFF>COMMA <color:BBFFBB> - Toggle 1st and 3rd person
<color:FFFFFF>MIDDLE MOUSE BUTTON <color:BBFFBB> - Rotate view around character

<color:FFFFFF>BACKSPACE <color:BBFFBB> - Clear Active Character's Target
<color:FFFFFF>G <color:BBFFBB> - Evaluate Target
<color:FFFFFF>TAB <color:BBFFBB> - Cycle Enemies Forward
<color:FFFFFF>SHIFT + TAB <color:BBFFBB> - Cycle Enemies Backward
<color:FFFFFF>~ <color:BBFFBB> - Target Nearest Enemy

<color:FFFFFF>J <color:BBFFBB> - Toggle Journal
<color:FFFFFF>H <color:BBFFBB> - Toggle Help
<color:FFFFFF>I <color:BBFFBB> - Toggle Inventory
<color:FFFFFF>K <color:BBFFBB> - Toggle Skills
<color:FFFFFF>C <color:BBFFBB> - Toggle Stats
<color:FFFFFF>B <color:BBFFBB> - Toggle Spells
<color:FFFFFF>T <color:BBFFBB> - Toggle Tracking
<color:FFFFFF>F <color:BBFFBB> - Toggle Buff Window
<color:FFFFFF>P <color:BBFFBB> - Toggle Party Mini Window
<color:FFFFFF>Y <color:BBFFBB> - Toggle Alliance Window
<color:FFFFFF>L <color:BBFFBB> - Toggle Leader Window
<color:FFFFFF>M <color:BBFFBB> - Toggle Map Window(Note that Map can be resized)
<color:FFFFFF>N <color:BBFFBB> - Toggle Macro Window

<color:FFFFFF>R <color:BBFFBB> - Reply to last private message
<color:FFFFFF>CTRL + TAB <color:BBFFBB> - Cycle to an older person who sent you a private messages.
<color:FFFFFF>CTRL + ALT + TAB<color:BBFFBB> - Cycle to an earlier person who sent you a private messages.

<color:FFFFFF>F1 - F6 <color:BBFFBB> - Set Active Party Member
<color:FFFFFF>SHIFT + (F1 - F6) <color:BBFFBB> - Target Party Member

<color:FFFFFF>Number Key <color:BBFFBB> - Trigger Hotkey
<color:FFFFFF>Shift + Number Key <color:BBFFBB> - Stop running Macro bound to this Hotkey
<color:FFFFFF>Ctrl + Number Key <color:BBFFBB> - Switch to Macro page <number>

<color:FFFFFF>CTRL + ~<color:BBFFBB> - Open Game Console 
"""

COMMANDTEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:20>Online Help
<font:Arial:16>
<color:BBBBFF>Chat Commands<just:left><font:Arial:13>

<color:FFFFFF>/m <color:BBFFBB> - MoM Channel (Ex. /m Hello eveyone!)

<color:FFFFFF>/mconnect <color:BBFFBB> - Connect to the MoM Chat Server. (if you get disconnected)

<color:FFFFFF>/h <color:BBFFBB> - Help Channel

<color:FFFFFF>/m <color:BBFFBB> - MoM Channel

<color:FFFFFF>/o <color:BBFFBB> - Off Topic Channel

<color:FFFFFF>/w <color:BBFFBB> - World Channel

<color:FFFFFF>/z <color:BBFFBB> - Zone Channel

<color:FFFFFF>/a <color:BBFFBB> - Alliance Channel

<color:FFFFFF>/g <color:BBFFBB> - Guild Channel

<color:FFFFFF>/s <color:BBFFBB> - Say Channel (within 30m can hear you)

<color:FFFFFF>/t <color:BBFFBB> - Send a private message. (Ex. /t Whizzo hey there!)

<color:FFFFFF>/me <color:BBFFBB> - Emote to all within 30m. (Ex. /me smiles at Whizzo)

* Once you have switched to a new chat channel you no longer need to type the channel prefix.

<color:FFFFFF>/channel help on|off <color:BBFFBB> - Listen to or mute help chat.

<color:FFFFFF>/channel offtopic on|off <color:BBFFBB> - Listen to or mute offtopic chat.

<color:FFFFFF>/channel mom on|off <color:BBFFBB> - Listen to or mute mom chat.

<color:FFFFFF>/channel world on|off <color:BBFFBB> - Listen to or mute world chat.

<color:FFFFFF>/channel zone on|off <color:BBFFBB> - Listen to or mute zone chat.

<color:FFFFFF>/channel combat on|off <color:BBFFBB> - Listen to or mute other's combat messages.

<color:FFFFFF>/ignore <character name> <color:BBFFBB> - Mute messages from the specified person.

<color:FFFFFF>/unignore <character name> <color:BBFFBB> - Unmute messages from the specified person.

<color:FFFFFF>/ignored <color:BBFFBB> - Show a list of everyone you are ignoring.

<color:FFFFFF>/clear <color:BBFFBB> - Clear chat window of all text.

<color:FFFFFF>/away *optional message* or /afk *optional message* <color:BBFFBB> - Set an autoresponse if someone sends you a private message.  If no optional message is provided, a default message will be used.  Use the command again to toggle it on or off.

<just:center><font:Arial:16>
<color:BBBBFF>Game Commands<just:left><just:left><font:Arial:13>

<color:FFFFFF>/camp <color:BBFFBB> - Leave the world and return to the main menu.

<color:FFFFFF>/quit <color:BBFFBB> - Leave the world and exit the game immediately.

<color:FFFFFF>/time <color:BBFFBB> - Display the current world time.

<color:FFFFFF>/localtime <color:BBFFBB> - Display the current time on your computer.

<color:FFFFFF>/suicide <color:BBFFBB> - If you become stuck, you can use this to return to your bindpoint.  Please note that this causes experience loss for characters over level 5.

<color:FFFFFF>/target *character name* <color:BBFFBB> - Target the named character.
<color:FFFFFF>/target pet<color:BBFFBB> - Target your pet.

<color:FFFFFF>/assist *character name* <color:BBFFBB> - Target the named character's target.
<color:FFFFFF>/assist pet<color:BBFFBB> - Target your pet's target.
<color:FFFFFF>/assist <color:BBFFBB> - Target your current target's target.

<color:FFFFFF>/attack <color:BBFFBB> - Toggles your Auto-Attack.

<color:FFFFFF>/rangedattack <color:BBFFBB> - Attacks with the item in your ranged slot.

<color:FFFFFF>/interact <color:BBFFBB> - Opens an NPC dialog window if available (friendly) or engages attack mode (enemy).

<color:FFFFFF>/roll <color:BBFFBB> - Roll a random number between 1 and 100.

<color:FFFFFF>/eval <color:BBFFBB> - Gives you information about your selected target, including relative difficulty to your active character, faction standing, etc.

<color:FFFFFF>/desc <color:BBFFBB> - Opens the target description window and displays information about your target more detailed than /eval. Does the same as shift-clicking the target.

<color:FFFFFF>/mydesc <color:BBFFBB> - Same as /desc for your active character, allows you to alter the characters description.

<color:FFFFFF>/craft *recipe name* <color:BBFFBB> - Have your active character attempt to craft the specified item.

<color:FFFFFF>/bind <color:BBFFBB> - If you are near a bindstone, this will change your bindpoint to your current position.  You can also double click on a bindstone.

<color:FFFFFF>/unlearn *spell name* <color:BBFFBB> - Removes the spell specified from your spellbook.  (Use with caution!)

<color:FFFFFF>/cast *spell name* <color:BBFFBB> - Casts the spell from your spellbook.

<color:FFFFFF>/skill *skill name* <color:BBFFBB> - Activates the skill from your skill list.

<color:FFFFFF>/lastname *name* <color:BBFFBB> - Gives your current character a last name. (must be at least level 25)

<color:FFFFFF>/clearlastname <color:BBFFBB> - Clears your current character's last name.

<color:FFFFFF>/server <color:BBFFBB> - Displays the name of the server you are on.

<color:FFFFFF>/friend add <character name> <color:BBFFBB> - Add a character to your friend list.

<color:FFFFFF>/friend remove <character name> <color:BBFFBB> - Remove a character from your friend list.

<color:FFFFFF>/map <description> <color:BBFFBB> - Add a map annotation to your 3d map and tracking list at your current location.

<color:FFFFFF>/unmap <description> <color:BBFFBB> - Remove the map annotation to your 3d map and tracking list matching the description given. Predefined annotations will only be removed temporarly.

<color:FFFFFF>/walk <on/off or nothing> <color:BBFFBB> - Toggles slow movement animations (gliding, walking) where available. If no argument is provided the command just toggles.

<just:center><font:Arial:16>
<color:BBBBFF>Guild Commands<just:left><font:Arial:13>

<color:FFFFFF>/gcreate <guildname> <color:BBFFBB> - Creates the guild specified with you as the leader.

<color:FFFFFF>/ginvite <character name> <color:BBFFBB> - Invites a player to join your guild.  (Guild Leader and Officers only)

<color:FFFFFF>/gjoin <color:BBFFBB> - Once invited, joins the guild.

<color:FFFFFF>/gdecline <color:BBFFBB> - Once invited, declines the invitation.

<color:FFFFFF>/gleave <color:BBFFBB> - Leaves your current guild.

<color:FFFFFF>/gwho <color:BBFFBB> - Display a list of all guild members in your world.

<color:FFFFFF>/g <message><color:BBFFBB> - Sends a message to all guild members in your world.

<color:FFFFFF>/gpromote <public name><color:BBFFBB> - Makes the player specified a guild officer. (Guild Leader only)

<color:FFFFFF>/gdemote <public name><color:BBFFBB> - Makes the player specified a guild member. (Guild Leader only)

<color:FFFFFF>/gremove <public name><color:BBFFBB> - Removes the player specified from the guild. (Guild Leader and Officers only)

<color:FFFFFF>/gsetmotd <message> <color:BBFFBB> - Sets the guild's message of the day. (Guild Leader and Officers only)

<color:FFFFFF>/gclearmotd <color:BBFFBB> - Clears the guild's message of the day. (Guild Leader and Officers only)

<color:FFFFFF>/groster <color:BBFFBB> - Displays all guild members and officers. (Guild Leader and Officers only)

<color:FFFFFF>/gcharacters <public name> <color:BBFFBB> - Displays all characters belonging to the specified guild member. (Guild Leader and Officers only)

<color:FFFFFF>/gpublicname <character name> <color:BBFFBB> - Displays the guild member who owns the specified character. (Guild Leader and Officers only)

<color:FFFFFF>/gsetleader <public name><color:BBFFBB> -  Sets the specified player as the new leader.  You become an officer. (Guild Leader only)

<color:FFFFFF>/gdisband <color:BBFFBB> -  Disbands the guild. (Guild Leader only)

<just:center><font:Arial:16>
<color:BBBBFF>Inventory Commands<just:left><font:Arial:13>

<color:FFFFFF>/useitem <item name><color:BBFFBB> - Searches inventory for specified item name (case insensitive) and attempts to use the item if found. Items on cursor get ignored.

<color:FFFFFF>/poison <target slot> <poison name><color:BBFFBB> - Searches inventory for specified poison name (case insensitive) and attempts to apply the poison to the weapon in the provided slot if one exists. Poisons on cursor get ignored.

<color:FFFFFF>/empty <color:BBFFBB> - Removes items from craft window slots to character inventory slots

<color:FFFFFF>/stack <color:BBFFBB> - Stacks items in a character's inventory

<color:FFFFFF>/sort <color:BBFFBB> - Sorts items within a character's inventory. Possible Options:

alpha = Sorts items in alphabetical order(default)
stack = Reduces item stacks (default)
nostack = Sort stacks in alphabetical order, but does not reduce stacks
reverse = Sort items in reverse alphabetical order
all = Sorts all inventory pages (default)
page1 = Only sorts items on first inventory page
page2 = Onlys sort items on second inventory page

<just:center><font:Arial:16>
<color:BBBBFF>Misc Commands<just:left><just:left><font:Arial:13>

<color:FFFFFF>//*text* or /memo *text*<color:BBFFBB> - Send a message to your game window.

<color:FFFFFF>/unstick <color:BBFFBB> - Attempts to free a player if you are stuck.

<color:FFFFFF>/resize <color:BBFFBB> - Toggles between normal size and standard human size.

<color:FFFFFF>/unstick <color:BBFFBB> - Attempts to free a player if you are stuck.

<color:FFFFFF>/stopcast <color:BBFFBB> - Cancels the casting of a spell

<color:FFFFFF>/stopmacro <macroname><color:BBFFBB> - Stops all macros that bear the supplied name for current character.

<color:FFFFFF>/stopmacros <color:BBFFBB> - Stops all macros for current character.

<color:FFFFFF>/ladder <color:BBFFBB> - Displays the characters with the most experience.  Note that some classes/races have XP bonuses, so it isn't uncommon for a lower level character to be higher on the ladder.

<color:FFFFFF>/avatar <color:BBFFBB> - Switch your 3d avatar to another character in your party. (Ex. /avatar Bingo)

<color:FFFFFF>/who <color:BBFFBB> - Displays the characters in the world and what zone they are in.  

<color:FFFFFF>/who <character name> <color:BBFFBB> - Displays the server the specified character is playing on.

<color:FFFFFF>/coords <color:BBFFBB> - Displays your location, which is useful for submitting problems where location is important.

<color:FFFFFF>/uptime <color:BBFFBB> - Displays the server's uptime.

<color:FFFFFF>/version <color:BBFFBB> - Displays the server's version.

<just:center><font:Arial:16>
<color:BBBBFF>Pet Commands<just:left><just:left><font:Arial:13>

<color:FFFFFF>/pet attack <color:BBFFBB> - Orders your pet to attack your target.

<color:FFFFFF>/pet stay <color:BBFFBB> - Orders your pet to stay.

<color:FFFFFF>/pet followme <color:BBFFBB> - Orders your pet to follow you.

<color:FFFFFF>/pet standdown <color:BBFFBB> - Orders your pet to cease attacking.

<color:FFFFFF>/pet dismiss <color:BBFFBB> - Orders your pet to leave.

<just:center><font:Arial:16>
<color:BBBBFF>Emote Animation and Audio Commands<just:left><just:left><font:Arial:13>

<color:BBFFBB>All of the following emote commands have default text and support custom text.  For example, '/dance' without a target, '/dance' with a target, and '/dance *custom text*' will display different messages, but all use the dance animation.

<color:FFFFFF>/dance <color:BBFFBB> - Your avatar does a nifty dance.

<color:FFFFFF>/bow <color:BBFFBB> - Your avatar bows.

<color:FFFFFF>/point <color:BBFFBB> - Your avatar points.

<color:FFFFFF>/wave <color:BBFFBB> - Your avatar waves.

<color:FFFFFF>/agree or /yes<color:BBFFBB> - Your avatar agrees.

<color:FFFFFF>/disagree or /no<color:BBFFBB> - Your avatar disagrees.

<color:FFFFFF>/laugh <color:BBFFBB> - Your avatar audibly laughs.

<color:FFFFFF>/scream <color:BBFFBB> - Your avatar audibly screams.

<color:FFFFFF>/groan <color:BBFFBB> - Your avatar audibly groans.


<just:center><font:Arial:16>
<color:BBBBFF>Reporting Commands<just:left><just:left><font:Arial:13>

<color:FFFFFF>Bug Report<color:BBFFBB>

Type /t mom bug 'replace this with your text'. Please try to explain what happened in reproducible steps so that we can attempt to reproduce the issue in order to resolve it. The more information you include the easier it will be for us to track down the problem.

For example: /t mom bug When I try to climb the outside Rogue Guild stairs in Trinst, I seem to walk through them and get stuck about halfway up. This happens every time I walk up the stairs unless I am looking straight up to the sky. 

An email will be sent to us including your name and message. 

<color:FFFFFF>Abuse Report<color:BBFFBB>

Type /t mom abuse 'replace this with your text'. Please try to explain what happened and give the name of the party or parties involved. This method should be used if there is not a Guardian online at the time, you are unable to resolve the situation on your own, and the situation occurred in the public chat channels.

For example: /t mom abuse MissL is using the Help channel to talk about inappropriate topics that directly violate the Play Nice Policy. 

An email will be sent to us including your name and message.
"""


FAQTEXT = """<linkcolor:AAAA00><shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:20>Online Help
<font:Arial:16>
<color:BBBBFF>FAQ<just:left><font:Arial:13>

<color:FFFFFF><font:Arial Bold:15>How can I improve my framerate?<color:BBFFBB><font:Arial:13>

In the Graphics Pane of the Options Dialog there are 4 preset Graphics Detail settings that you can choose from, select one and click on *Apply Changes*.  This should increase your framerate.

<color:FFFFFF><font:Arial Bold:15>I am totally confused?  I can't keep track of what's going on!!!<color:BBFFBB><font:Arial:13>

If you are playing the game with more than one character in your party, try dropping some off at an inn and playing with only one.  The game is fully playable with one character and you can multiclass.  Many people actually prefer playing this way!  

<color:FFFFFF><font:Arial Bold:15>I have more than one character in my party, though can only see one character?<color:BBFFBB><font:Arial:13>

Your party is represented in the world by a single 3d avatar.  You can change which character represents your party with the /avatar command or by clicking on the *Set Avatar* button on the Settings Page of your Character Window.

<color:FFFFFF><font:Arial Bold:15>One of my characters has died!!! What should I do?<color:BBFFBB><font:Arial:13>

You need a cleric to resurrect you.  You can visit Istri Sansmil in Trinst or Maurgon in Kauldur.  You may want to add a cleric to your party as they can resurrect at level 20.  High level necromancers can cast Undeath.

<color:FFFFFF><font:Arial Bold:15>How do I trade with other players?<color:BBFFBB><font:Arial:13>

With an item in your cursor, double click on the player.

<color:FFFFFF><font:Arial Bold:15>How do I equip my pet?<color:BBFFBB><font:Arial:13>

On the Item pane of your character window, click on the *P* button to open your pet's inventory and equip as usual.

<color:FFFFFF><font:Arial Bold:15>How do I multiclass?<color:BBFFBB><font:Arial:13>

You can select a secondary class at level 5 and a tertiary class at level 15.  There are numerous trainers in Trinst that can teach you the basics of your new class.  You can also control experience points to each of these classes with the provided XP sliders!

<color:FFFFFF><font:Arial Bold:15>How do I add/remove characters from my party?<color:BBFFBB><font:Arial:13>

You can add and remove characters at inns.

<color:FFFFFF><font:Arial Bold:15>How do I save my game?<color:BBFFBB><font:Arial:13>

Single Player:  The game is automatically saved at one minute intervals.  You can save your progress at any time by camping. 

Multiplayer:  Your progress is saved on the world server at one minute intervals.

<color:FFFFFF><font:Arial Bold:15>How do I scribe a scroll?<color:BBFFBB><font:Arial:13>

Ctrl + Double click the scroll to scribe it into your spellbook.

<color:FFFFFF><font:Arial Bold:15>How do I loot corpses?<color:BBFFBB><font:Arial:13>

Double click or ctrl-click the corpse.

<color:FFFFFF><font:Arial Bold:15>What's a party?  What's an alliance?<color:BBFFBB><font:Arial:13>

As a player, you can have a party of up to 6 characters. In multiplayer, you can form an alliance with up to 6 other players. That's 36 characters!!! An alliance shares XP and can chat on a private alliance channel. Furthermore, some spells affect your entire party and some spells affect your entire alliance.

"""


EULATEXT = """<linkcolor:AAAA00><shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:22><yourgamenamehere> ++VERSION++ - Licensing Agreement

<color:FFFFFF><just:left><font:Arial:13>
This Software Licensing Agreement (\\"Agreement\\") is a legal agreement between you and <yourcompanynamehere>. By installing this Software, by loading or running the Software, by placing or copying the Software onto your hard drive, or by distributing the Software, you agree to be bound by the terms of this Agreement. These are the only terms by which <yourcompanynamehere> permits copying or use.

<just:center><font:Arial Bold:16><yourcompanynamehere>' LICENSE AGREEMENT FOR the <yourgamenamehere> ++VERSION++.
<just:left>

General terms:

<font:Arial Bold:15>1. THE SOFTWARE.
<font:Arial:14>The Software licensed under this Agreement is the ++VERSION++ version of the computer program <yourgamenamehere>, which consists of executable files, data files, and documentation.

<font:Arial Bold:15>2. GRANT OF LICENSE.
<font:Arial:14>Subject to the terms and conditions contained in this Agreement, <yourcompanynamehere> hereby grants a non-exclusive license and right to install and use one (1) copy of the Software for your use on either a home, business, or portable computer for the purpose of testing <yourgamenamehere>. In addition, the Software has a multi-player capability that allows users to utilize the Software over the Internet. Use of the Software over the Internet is subject to your acceptance of the Agreement. <yourcompanynamehere> reserves the right to update, modify, or change the Agreement at any time. The Program is licensed, not sold. Your license confers no title or ownership in the Program. You may not modify, translate, disassemble, reverse engineer, decompile, or create derivative works based upon the Software. You also may not in any way redistribute the software.

<font:Arial Bold:15>3. COPYRIGHT.
<font:Arial:14>All title, ownership, and intellectual property rights in and to the Software and any and all copies thereof (including, but not limited to, any titles, computer code, themes, objects, characters, character names, stories, dialog, catch phrases, locations, concepts, artwork, animations, sounds, musical compositions, audio-visual effects, methods of operation, moral rights, any related documentation, and \\"applets\\" incorporated into the Software) are owned by <yourcompanynamehere> or it's licensors. The Software is protected by the copyright laws of the United States, international copyright treaties and conventions, and other laws. All rights are reserved. The Software contains certain licensed materials, and <yourcompanynamehere>' licensors may protect their rights in the event of any violation of this Agreement.

<font:Arial Bold:15>4. NO WARRANTY.
<font:Arial:14>THE SOFTWARE IS PROVIDED \\"AS-IS\\". NO WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, ARE MADE AS TO IT OR ANY MEDIUM IT MAY BE ON. <yourcompanynamehere> WILL PROVIDE NO REMEDY FOR INDIRECT, CONSEQUENTIAL, PUNITIVE OR INCIDENTAL DAMAGES ARISING FROM IT, INCLUDING SUCH FROM NEGLIGENCE, STRICT LIABILITY, OR BREACH OF WARRANTY OR CONTRACT, EVEN AFTER NOTICE OF THE POSSIBILITY OF SUCH DAMAGES.

<font:Arial Bold:15>5. TERM.
<font:Arial:14>The term of this license grant is perpetual. You may terminate this Agreement at any time by destroying the copy of the Software in your possession. Your license to use the Software will automatically terminate if you breach the terms of this Agreement.

<font:Arial Bold:15>6. GENERAL PROVISIONS.
<font:Arial:14>This Agreement is the sole and entire Agreement relating to the subject matter hereof, and supercedes all prior understandings, agreements, and documentation relating to such subject matter. If any provision in this Agreement is held by a court of competent jurisdiction to be invalid, void, or unenforceable, the remaining provisions will continue in full force without being impaired or invalidated in any way. This Agreement will be governed by the laws of the State of California. With respect to every matter arising under this Agreement, you consent to the exclusive jurisdiction and venue of the state and federal courts sitting in Los Angeles, California, and to service by certified mail, return receipt requested, or as otherwise permitted by law. This Agreement does not create any agency or partner relationship. Your rights under this Agreement are personal and do not include any right to sublicense the Software. This Agreement may be terminated by <yourcompanynamehere> by giving a 30-day advance written notice.


Thank you for using this Software in accordance with the terms of this Agreement
"""


CREDITSTEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98>
<font:Arial Bold:22>Credits
"""


if RPG_BUILD_DEMO:
    EULATEXT = EULATEXT.replace("++VERSION++","Free Edition")
elif RPG_BUILD_TESTING:
    EULATEXT = EULATEXT.replace("++VERSION++","Test Version")
else:
    EULATEXT = EULATEXT.replace("++VERSION++","Premium Edition")


def OnHelpKeyboard():
    TGEObject("HELPWND_KEYBOARDPANE").visible=True
    TGEObject("HELPWND_COMMANDSPANE").visible=False
    TGEObject("HELPWND_FAQPANE").visible=False

def OnHelpFAQ():
    TGEObject("HELPWND_KEYBOARDPANE").visible=False
    TGEObject("HELPWND_COMMANDSPANE").visible=False
    TGEObject("HELPWND_FAQPANE").visible=True

def OnHelpCommands():
    TGEObject("HELPWND_KEYBOARDPANE").visible=False
    TGEObject("HELPWND_COMMANDSPANE").visible=True
    TGEObject("HELPWND_FAQPANE").visible=False

def PyExec():
    #eventually this can be a full help system
    
    TGEObject("MOM_VERSION_TEXT").setText(RPG_CLIENT_VERSION)
    
    r = HELPTEXT.replace('\n','\\n')
    c = COMMANDTEXT.replace('\n','\\n')
    f = FAQTEXT.replace('\n','\\n')
    
    TGEEval(r'HelpWnd_KEYBOARDText.setText("%s");'%r)
    TGEEval(r'HelpWnd_CommandsText.setText("%s");'%c)
    TGEEval(r'HelpWnd_FaqText.setText("%s");'%f)
    
    TGEExport(OnHelpKeyboard,"Py","OnHelpKeyboard","desc",1,1)
    TGEExport(OnHelpCommands,"Py","OnHelpCommands","desc",1,1)
    TGEExport(OnHelpFAQ,"Py","OnHelpFAQ","desc",1,1)
    
    TGEObject("HELPKEYBOARDBUTTON").performClick()
    
    eula = EULATEXT.replace('\n','\\n')
    credits = CREDITSTEXT.replace('\n','\\n')
    TGEObject("EulaWND_window").setText("Licensing Agreement")
    TGEObject("CreditsWND_window").setText("Credits")

    TGEEval(r'Eulatext.setText("%s");'%eula)
    TGEEval(r'MoMCreditsText.setText("%s");'%credits)
    
    
