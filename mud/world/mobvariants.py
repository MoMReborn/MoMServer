# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#variants

#add to base stats

#add to level

#add to mobinfo stuff (Scale, move, visibilty)

#race mods (undead have spectral variants for instance)

#named variants 

from mud.world.defines import *

import random

PCRACES = ("Human","Gnome","Dwarf","Halfling","Elf","Ogre","Drakken","Troll","Orc","Goblin","Dark Elf","Titan")


def AdjustLevel(mob, plevel, slevel=0, tlevel=0):
    
    level = mob.plevel + plevel
    if level > 100:
        level = 100
    elif level < 1:
        level = 1
    mob.plevel = level
    
    if mob.slevel:
        level = mob.slevel + slevel
        if level > 100:
            level = 100
        elif level < 1:
            level = 1
        if level > mob.plevel:
            level = mob.plevel
        mob.slevel = level
        
        if mob.tlevel:
            level = mob.tlevel + tlevel
            if level > 100:
                level = 100
            elif level < 1:
                level = 1
            if level > mob.slevel:
                level = mob.slevel
            mob.tlevel = level


def DoScaleVariant(mob):
    #Diminutive, Tiny, Small, Large, Huge, Gargantuan, Colossal
    scale = 1.0
    plevel,slevel,tlevel = 0,0,0
    
    range = mob.plevel+80
    if range > 100:
        range = 100
    r = random.randint(1,range)
    
    if r == 100: 
        name = "Colossal"
        scale = 2.0 
        plevel = 5
        slevel = 4
        tlevel = 3
    elif r>=94: 
        name = "Gargantuan"
        scale = 1.75 
        plevel = 3
        slevel = 1
    elif r>=85: 
        name = "Huge"
        scale = 1.5 
        plevel = 2
    elif r>=40: 
        name = "Large"
        scale = 1.25 
        plevel = 1
    elif r>=10: 
        name = "Small"
        scale = .75
        plevel = -1
    elif r>1: 
        name = "Tiny"
        scale = .5
        plevel=-2
    else:
        name = "Diminutive"
        scale = .25
        plevel=-3
        slevel=-1
        
    mob.variantName = name
    mob.size *= scale
    
    AdjustLevel(mob,plevel,slevel,tlevel)
    
    
def DoUndeadVariant(mob):
    #can include size variants
    vname = ""
    if random.randint(1,100)<=10:
        DoScaleVariant(mob)
        vname = mob.variantName
        
    variants = {}
    
    #vis, level, haste, xpmod, physical resists, regen(*level)
    variants["Phantasmal"]=(.85,(5,3,2),.5,5,100,2)
    variants["Spectral"]=(.65,(3,2,1),.3,5,50,1)
    variants["Ghostly"]=(.5,(2,1,0),.25,2.5,25,.5)
    variants["Spooky"]=(.35,(1,0,0),.1,1.1,10,.25)
    
    range = mob.plevel+80
    if range > 100:
        range = 100

    
    r = random.randint(1,range)
    if r >= 98:
        v = "Phantasmal"
    elif r > 90:
        v = "Spectral"
    elif r > 65:
        v = "Ghostly"
    else:
        v = "Spooky"
        
    if vname:
        mob.variantName = vname+" "+v
    else:
        mob.variantName = v

    v = variants[v]
        
    mob.visibility-=v[0]
    
    AdjustLevel(mob,v[1][0],v[1][1],v[1][2])
    
    mob.innateHaste+=v[2]
    mob.xpMod+=v[3]
    
    mob.resists[RPG_RESIST_PHYSICAL] += v[4]
        
    mob.regenHealth+=v[5]*mob.plevel
    
def DoLevelVariant(mob):
    #, , , , 
    
    variants = {}
    
    #size, levels, light, haste, xp Mod
    variants["Sickly"]=(1.0,(-1,-1,-1),0,-.1,0)
    variants["Stalwart"]=(1.0,(1,0,0),0,.1,.5)
    variants["Formidable"]=(1.0,(2,1,0),0,.2,.75)
    variants["Talented"]=(1.1,(3,2,1),0,.4,1)
    variants["Fearsome"]=(1.2,(5,4,3),0,.6,4)
    variants["Legendary"]=(1.5,(10,9,8),2,1,9)
    
    range = mob.plevel+80
    if range > 100:
        range = 100

    r = random.randint(1,range)
    
    if r == 98:
        v = "Legendary"
    elif r > 88:
        v = "Fearsome"
    elif r > 75:
        v = "Talented"
    elif r > 60:
        v = "Formidable"
    elif r > 35:
        v = "Sickly"
    else:
        v = "Stalwart"
        
    allresists = [RPG_RESIST_PHYSICAL,RPG_RESIST_MAGICAL,RPG_RESIST_FIRE,RPG_RESIST_COLD,RPG_RESIST_POISON,RPG_RESIST_DISEASE,RPG_RESIST_ACID,RPG_RESIST_ELECTRICAL]

    
    if v == "Legendary":
        for r in allresists:
            mob.resists[r] += 25
            
        
    mob.variantName = v

    v = variants[v]
    
    mob.size*=v[0]
    AdjustLevel(mob,v[1][0],v[1][1],v[1][2])
    mob.light+=v[2]
    if v[3]>0:
        mob.innateHaste+=v[3]
    else:
        mob.slow+=-v[3]
        
    mob.xpMod += v[4]
    

def GenerateVariant(mob):
    if mob.spawn.flags&RPG_SPAWN_UNIQUE:
        return
        
    if mob.spawn.flags&RPG_SPAWN_RESOURCE:
        return
    
    #unique
    if random.randint(1,100) <=6:
        DoUniqueVariant(mob)
        if mob.uniqueVariant:
            AdjustLevel(mob,1)
            return

    
    #UNDEAD
    if mob.spawn.race == "Undead":
        #1 in 10 undead is a variant
        if random.randint(1,100) <= 10:
            DoUndeadVariant(mob)
            return
    
    #8% of mobs have a scale variance
    if mob.spawn.race not in PCRACES:
        if random.randint(1,100) <=8:
            DoScaleVariant(mob)
            return

    #8% of mobs have a level variance
    if random.randint(1,100) <=8:
        DoLevelVariant(mob)
        return
    
     
def DoUniqueVariant(mob):
    if mob.spawn.flags&RPG_SPAWN_RESOURCE:
        return

    spawn = mob.spawn
    

    if not random.randint(0,1):    
        if mob.spawn.sex == "Female" and mob.spawn.realm == RPG_REALM_DARKNESS and spawn.race in ("Human","Dark Elf","Gnome","Goblin"):
            names = UNIQUE_NAMES['VILLIANESS']
            mob.name = names[random.randint(0,len(names)-1)]
            mob.uniqueVariant = True
            return
            
    
    if not random.randint(0,1):
        if mob.spawn.race in PCRACES:
            if mob.spawn.pclassInternal == "Necromancer":
                names = UNIQUE_NAMES['NECROMANCER']
                mob.name = names[random.randint(0,len(names)-1)]
                mob.uniqueVariant = True
                return
            if mob.spawn.pclassInternal == "Warrior":
                names = UNIQUE_NAMES['WARRIOR']
                mob.name = names[random.randint(0,len(names)-1)]
                mob.uniqueVariant = True
                return

    
    if mob.spawn.race == "Treant":
        names = UNIQUE_NAMES['TREANT']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return

    if mob.spawn.race == "Dwarf":
        names = UNIQUE_NAMES['DWARF']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return
        
    if mob.spawn.race == "Elf":
        names = UNIQUE_NAMES['ELF']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return

    if mob.spawn.race == "Dark Elf":
        names = UNIQUE_NAMES['DARKELF']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return


    if mob.spawn.race == "Halfling":
        names = UNIQUE_NAMES['HALFLING']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return

    if mob.spawn.race == "Gnome":
        names = UNIQUE_NAMES['GNOME']
        mob.name = names[random.randint(0,len(names)-1)]
        mob.uniqueVariant = True
        return
    
    if mob.spawn.race not in PCRACES:
        if mob.spawn.realm == RPG_REALM_MONSTER:
            names = UNIQUE_NAMES['MONSTER']
            mob.name = names[random.randint(0,len(names)-1)]
            mob.uniqueVariant = True
            return
        
    
    
UNIQUE_NAMES = {
'DWARF':(
'Bfaky Warlockhunter','Dah Silverfist','Def Quartzgrinder','Dirake Steelkiller','Falule Grimminer',
'Fegeri Dragonsmiter','Fmidr Grimtracker','Gol Stonetunnel','Hadtu Foesmiter','Hesreh Goblinsmiter',
'Heti Warlockslayer','Hgah Goblinslayer','Iode Grayforger','Kared Ogreslasher','Kir Warlockslayer',
'Kortud Doomfighter','Lam Slatehunter','Murela Rockbreaker','Nar Redslasher','Nutlir Bronzecut',
'Redet Cairnslasher','Rih Cairnfighter','Rleds Devilcrusher','Rures Graymolder','Yirari Ironkiller',
),

'TREANT':(
'Alderbriar','Alderfoot','Aldershoot','Armfrond','Armgrove','Armhedge','Ashbriar','Ashheel','Ashtalon','Ashtooth',
'Baldbramble','Baldhazel','Beamclaw','Beamclaw','Beamlock','Beammane','Beardbramble','Bentseed','Berrybraid',
'Berryfury','Birchshoot','Birchsmile','Birchtrunk','Blackbush','Bonebriar','Braidgrove','Bramblehand','Branchsmile',
'Briarmane','Briarsmile','Brightbramble','Brownherb','Brownpalm','Brownshrub','Brownskin','Brownsmile','Browntalon',
'Brownwillow','Budclaw','Calmseed','Calmyew','Cedarclaw','Cedarroot','Cedarsprig','Cedarsprig','Clawleaf','Copsehand',
'Copseskin','Craftbirch','Craftbraid','Craftbriar','Craftclaw','Craftlimb','Craftlock','Crownherb','Crownroot',
'Elmbraid','Elmfury','Elmhand','Elmlimb','Elmsprig','Fallcedar','Fallshrub','Fallweed','Farblossom','Footgrove',
'Footjungle','Foresthazel','Forestoak','Furyjungle','Gladstaff','Grandfrond','Grandmaple','Grandpalm','Grandpine',
'Greatblossom','Greenash','Greenbirch','Greenbriar','Greenpalm','Greenrowan','Handthorn','Hazelbark','Hazelgrove',
'Hazeltwig','Hedgebraid','Hedgefoot','Herbbeam','Herbbirch','Herbcrown','Herbheel','Herbleg','Herblimb','Herbmane',
'Herbmoss','Herboak','Herbpine','Herbpine','Herbskin','Herbwood','Highcraft','Highelm','Highwillow','Hollyhedge',
'Hollyherb','Hollyjungle','Hollylock','Honeyherb','Junglearm','Junglefury','Jungleoak','Jungleskin','Limbbranch',
'Limblock','Limbmarrow','Lowcraft','Madcraft','Maplebramble','Maplemane','Marrowbloom','Marrowfrond','Marrowthicket',
'Marrowthorn','Marrowtwig','Oaklimb','Oddbriar','Oddgrove','Oddthicket','Oldbush','Oldroot','Palmsmile','Pinefoot',
'Quickmoss','Quickshoot','Quickshrub','Rootbone','Rootlock','Rowanbud','Rowanclaw','Rowancrown','Rowanleg','Rowanmane',
'Sadcopse','Saphazel','Sapholly','Saplimb','Shootfoot','Shoottooth','Shrubalder','Shrubmoss','Smilebloom','Sprigbraid',
'Springcedar','Springcrown','Springcrown','Springhazel','Springmarrow','Springsmile','Strangebark','Strangemaple',
'Strangeyew','Summerbeard','Summerlock','Summerrowan','Talonbloom','Talonherb','Talonthicket','Talonthicket',
'Thorncrown','Timberheel','Timberleg','Timberpalm','Toothbark','Weedbranch','Weedfoot','Weedhedge','Weedheel',
'Weedmoss','Weedrowan','Weedsmile','Wildlock','Wildrowan','Willowbone','Willowcrown','Willowmarrow','Winterpalm',
'Winterpalm','Winterpine','Wiseherb','Woodarm','Woodmaple','Woodrowan','Woodskin','Wyrdleaf','Yewbeard','Yewcrown',
'Yewhand','Yewtrunk','Youngcraft','Youngshoot',),

'NECROMANCER':(
'Aetanie Moonchant','Aetucanele Redeye','Ahicivara Flamefury','Airebrcal Colddrinker','Alali Ironweeper',
'Alaranei Painvenom','Alenaninat Ebonmist','Aleval Steelmark','Alisa Plaguemist','Alisma Darkspell',
'Aluseie Shadowplague','Amonuco Deadskull','Anabet Scardirge','Andagi Coldhand','Angeliat Dreadmaw',
'Anibarosa Cruelflame','Anonindali Darkbite','Antieb Fogrip','Ardag Farmurk','Arostrde Ironghost',
'Arulis Grimslayer','Azarcop Darkbone','Baban Blackheart','Bacarde Fearwolf','Bacer Farbane','Bagelusa Icefear',
'Bahononie Ironmist','Balan Evilslayer','Balanti Ebonrune','Balueos Scardeath','Banem Darktear',
'Banth Plaguestalk','Barar Cruelghoul','Barelel Deadtomb','Bebrdeli Bonefate','Benilie Irontear',
'Bentan Coldblade','Beracah Deadchain','Beselibe Icespirit','Besmar Sinrend','Betiusel Cruelmist',
'Brala Grimmurk','Cagdema Warptomb','Calei Grimstalk','Calesm Wildrend','Canatusan Sinknife','Catiares Spellstalk',
'Cazanelae Moonbind','Celerar Redscar','Cenie Farmaw','Cerlalelur Helldirge','Chasora Eboncry','Chelemina Coffinfate',
'Chesanisal Warhowl','China Farstorm','Ciebanorco Fogbeast','Ciebard Terrorshadow','Cierlele Devildream',
'Cilaik Grimgrave','Cisaven Devilpain','Conelarone Warmaw','Conenebral Dreadnight','Congda Redshadow',
'Copha Twistkill','Cophor Direeye','Corendor Coldrain','Corlicalem Duskghoul','Cornd Wildhowl','Costa Dreaddemon',
'Dalebagd Diredemon','Daneterdo Steelhunter','Dasargab Venombrood','Delesaro Voidkill','Deneoph Cryptfate',
'Desele Ebonchain','Devaza Painsoul','Doliele Darkcry','Dophandrt Colddirge','Dorasa Cursefury',
'Doshani Ironbeast','Dosteleie Cruelsoul','Dramoram Mistbind','Drdal Deathbrood','Drdraz Farwolf',
'Drenelic Darkdragon','Drlichal Griefkill','Dronth Crueldevil','Drorelicha Darkblood','Drueluc Tombstorm',
'Eivanter Wildchain','Elali Darkbind','Elazaero Coldghost','Elelazanar Grimmurk','Elene Windstrike',
'Elerdala Grimbane','Elisali Bonerend','Eluch Venomwoe','Eluluenur Plaguerune','Emalelarar Ebondevil',
'Enala Cairngrief','Engari Darkbite','Enisala Steelshriek','Eniuele Evilwolf','Ereba Dreadwing',
'Esendrana Duskclaw','Esmane Darkfire','Etenius Dreadspawn','Etetelend Doomfog','Ezarur Chantclaw',
'Febah Plaguetomb','Febam Twiststalker','Febesor Deathweeper','Feielesa Venomdirge','Feira Painrune',
'Feiust Venomspawn','Felaneb Deadwind','Feleba Dreadcoffin','Felelelaev Deadrune','Felerda Cryptmourner',
'Felernos Evilrain','Feliri Sinbite','Felis Wildcloud','Felusena Blackhell','Femid Blackwing','Fenaletis Dreadmurk',
'Fenanies Grimcry','Fenanthole Coldghoul','Fenereli Cruelbite','Fenganel Fearstrike','Fercard Chaindoom',
'Ferda Darkblood','Ferdeiaelu Icehand','Feresontal Murkhunter','Ferga Grimnight','Fergal Horrorfire',
'Feronthica Devilspawn','Ferucanag Fogmurk','Fesebard Coffinmist','Fesmanar Tombeye','Festian Deadshadow',
'Festulid Duskstrike','Fezaba Diredevil','Fezaco Farknife','Galeont Nightheart','Ganene Wildmourner',
'Gdaluei Blackmoon','Gdantela Smokefang','Gdole Icebite','Gdonan Chantfury','Gdorgde Steelweeper',
'Gdrailele Tombbite','Gdran Blackghoul','Gdrdo Cairnbane','Gebalenda Nightstalk','Gelebarca Ironrend',
'Geluel Farkiller','Gelus Terrorbind','Gendosaniu Evilrune','Gerciemana Deathcoffin','Geval Voidchain',
'Giceve Horrorbeast','Gieidese Mistweeper','Giene Blacksinner','Gioraro Fearshadow','Gisavaenav Mistdragon',
'Gismarn Scardemon','Gison Deadshadow','Giusetisha Voidslayer','Habrlen Smokehaunt','Hanaz Steelclaw',
'Haneba Murkbite','Hanelan Dreadwind','Hanilue Cursestalk','Hanolane Irondemon','Hanteniole Murkknife',
'Hardarebav Direhand','Harlicano Deadrain','Harni Plaguerend','Harordan Horrorrain','Harorue Coldsnake',
'Harus Deadvenom','Hathalen Mistspirit','Havine Cairnshade','Heletiv Fardirge','Hisarelirn Graveghast',
'Hiulican Steelhaunt','Hosesta Chantrip','Ialetuesh Wildsinner','Iananusan Cairnbane','Ianevases Steelstrike',
'Ibetibah Mistmourner','Icenosan Darkfang','Iciagdosm Warflame','Ieiue Horrortear','Ielei Sinmurk',
'Ielelelel Murkrain','Ielezaza Redheart','Iemezale Cruelsinner','Ienirtri Eboncurse','Ierdo Coffinwarp',
'Ietarin Twistshade','Ikron Devilslayer','Ikroph Redclaw','Ilinab Venomrend','Inuselu Steeldusk',
'Irchieli Darkheart','Irintr Murkskull','Isaicagie Woemist','Isalusol Deathshade','Isanosaco Voidhaunt',
'Isanthang Cruelspawn','Isesavone Direfire','Isosemi Darkshade','Iucichari Flamestrike','Jeisan Farghoul',
'Jelev Chantcairn','Jendr Darkmourner','Jeorleisa Venomclaw','Jerali Griefsnake','Jesenelu Spelldream',
'Jeshardri Dreadbrood','Jucanulel Blackmaw','Jucieosman Gloomspawn','Juciv Cursestrike','Jucor Darkknife',
'Juelu Painstrike','Jueneles Coffinwar','Juler Fearstalk','Julernt Warphowl','Julianen Smokerip',
'Juravianan Cursewarp','Jusal Dreadvenom','Jusarc Ebonbind','Jusarl Blackdragon','Jusaroriu Grimfog',
'Jusmoro Coffinfear','Jusor Ebonfire','Krale Dirgescream','Kralethabe Blackwind','Kraliais Wildmist',
'Krarardebe Evilstalk','Krdarenu Murkspawn','Krdophord Steelbrood','Krdordo Fogdragon','Krdos Woemist',
'Krdrisar Blackfang','Krdrus Nightrip','Kriet Tombwarp','Krlend Coldhell','Krndenar Wildmist','Krneven Direeye',
'Kropham Painkill','Krora Twistscar','Krordal Graveclaw','Krosenal Redrain','Krtes Doommourn','Krtisang Ironwing',
'Lagiesman Wildvenom','Lanan Tombskull','Lanelelerg Dreadclaw','Lebrnd Doommaw','Leleos Wargrave',
'Leluson Scarhunter','Lenachan Horrorcloud','Leniane Farspawn','Leral Deadnight','Lertico Devilknife',
'Lesemama Wildtear','Letiarne Blackshadow','Letisma Evilfury','Levacortu Cursestalk','Levaha Devilblade',
'Levaro Paincloud','Lezal Blackbrood','Lezarer Grimspectre','Liagicebe Nightdoom','Liame Coldfire',
'Liceieba Redbone','Liciacon Redshriek','Lidro Murkscar','Lietiesh Dreadmark','Lileiaiet Shadowshade',
'Linavi Deathfire','Liulebes Hellblood','Mabanusa Cryptwing','Mairenas Smokestorm','Malel Scardirge',
'Maleses Chantbeast','Mamarler Hellghoul','Mandebeb Blackcoffin','Maniue Twisttomb','Marden Dreadghoul',
'Melemac Dreaddragon','Menetantir Ironvenom','Metrlagd Deadghoul','Miaru Horrordirge','Micev Wildghoul',
'Miend Farcry','Miliethona Farmourn','Monar Plaguebone','Mondraha Griefcoffin','Morariopha Deadbone',
'Nanan Murkbeast','Nandr Dirgehunter','Ndales Fearshriek','Ndatetarir Redflame','Ndrninen Evildirge',
'Nicarnthi Ironcurse','Niliso Deathshriek','Niondrar Ironkill','Nivalela Murkhand','Nthar Warcurse',
'Nucarleb Flameghast','Olanirne Direcurse','Olebri Paindevil','Oletrd Duskclaw','Onanarirar Venomfear',
'Ondrial Ebondrinker','Onelem Dreadskull','Oneneteli Grimbane','Ongeondone Icestalk','Ongesh Coldghast',
'Onico Griefeye','Ontra Venombind','Onurdrdore Ebonstalker','Opharti Ironhaunter','Orarnti Cursecairn',
'Ordanesa Coldrule','Ordaram Runewar','Ordricis Evilmourner','Osano Deadspell','Osavies Blackmurk',
'Osazardaro Bloodstalk','Osenal Redeye','Osholusa Warfang','Osmanu Farfog','Ososm Redmaw','Phaes Evildusk',
'Phaikrth Cruelrule','Phalesandr Fardevil','Phalicer Dirgemourner','Phalist Dreamtomb','Phalu Blackrend',
'Phane Sinfury','Phanei Grimhell','Phardarano Darkblood','Pharntre Dreamdragon','Phelelie Sinrend',
'Phercalele Redrip','Phole Evilbite','Phonan Windslayer','Phonicha Icedream','Phophaca Diredemon',
'Phosevang Cursespell','Phosoliv Cruelspectre','Rananar Chainbane','Randebeb Cryptscream','Raniu Grimcloud',
'Rceles Reddusk','Rcosevis Nightbeast','Rderei Darkbite','Rdoph Farrain','Rdrdahieri Grimskull',
'Rdrnulei Steelmourn','Reliacava Fargrave','Renialesah Cruelstalker','Rgidebe Terrormist','Riophar Steelwind',
'Rliceba Twisttomb','Rnonevonth Fatespawn','Ronendro Steelbane','Rteseval Murkgrave','Sacevoneo Gloommist',
'Saleleme Ebonmourner','Saliesanac Frostbite','Sandan Cursemurk','Sararc Spelldragon','Sardonaic Evilbind',
'Sazac Evilmourn','Selerteth Dreadclaw','Seline Blackgrave','Selisezaz Ebonhowl','Senalikrae Ironfury',
'Seneli Ironscar','Shaneth Nightwing','Shorda Farghoul','Smahaluc Ebonrune','Smalan Sindragon','Smale Cursedeath',
'Smani Mistmurk','Smielule Twistsmoke','Smiesali Venomdeath','Smisale Coldmurk','Smophiv Coldghast',
'Songa Grimclaw','Sosalicale Ironsinner','Sthielie Warpscream','Sticesa Twistmourn','Tagderan Graverain',
'Tahele Icehaunter','Talise Twistbane','Tamardor Coldbeast','Taniar Dreamdemon','Tantulana Warpfury',
'Teisan Flameblade','Telucen Plaguekill','Thare Flamefire','Thatet Deadspell','Thavo Diredemon','Thiule Cursescream',
'Tiala Dreaddragon','Tielalic Wildsnake','Tielaniceo Eboncrypt','Tiero Redweeper','Tiste Duskblade',
'Tiuriuco Eboncoffin','Tiusamaca Blackspell','Triagerdos Mistvoid','Tulene Evilghast','Tuluci Dirgewing',
'Tusan Duskcry','Tusand Darkcry','Ucardrcen Steelmoon','Ueiei Direghast','Ueletete Blackfire','Uelic Painmourn',
'Ulaliaz Blackclaw','Ulelele Twistdemon','Ulend Bloodvoid','Ulenerga Darkdusk','Urdrdophan Blackmist',
'Urgisar Wildscream','Usalebenti Fearwind','Usani Doomdirge','Usasarl Coldrain','Usave Moonhunter',
'Usernie Eboncrypt','Userusa Ironrune','Usesmaza Terrornight','Useza Cryptgrief','Usmare Dirgeclaw',
'Vacoror Gravesin','Vaist Fearmourner','Valeiel Bloodvoid','Vamana Grimclaw','Vanes Wildrip','Vardo Farmist',
'Varidone Moonskull','Varnane Scarsin','Vaseluel Devilcloud','Vazanari Farrip','Veteicana Coldbite',
'Vianor Venomsinner','Vibanelio Darkblood','Vicandose Wildcrypt','Vidrar Wildeye','Vietelenan Blackcoffin',
'Vilikr Diremourner','Vingende Redhand','Virtinde Steelstrike','Viusmosa Deathghost','Vorne Farfang',
'Vorone Horrorbone','Vortiemo Horrorscar','Vosanticir Grimmurk','Xabar Curseeye','Xabele Paindragon',
'Xaican Doomghast','Xalebale Darkghast','Xaleman Darkmist','Xalinama Farbrood','Xaluez Horrorshade',
'Xamal Deathhand','Xanalenai Redghost','Xanaries Hellrain','Xanercosam Blackrule','Xanevel Cursegrief',
'Xanicelie Grimdirge','Xaniniceo Iceblade','Xarabrd Direspawn','Xaresmane Bloodhand','Xaries Dreamwing',
'Zacelebemi Redghast','Zacesang Cursecrypt','Zaicabav Ironstalk','Zalesmi Steelmurk','Zaletuse Diredragon',
'Zaliev Duskskull','Zalind Cruelspawn','Zaluch Nightscream','Zalusari Fatevenom','Zanaro Plaguefang',
'Zandanie Ebonshade','Zandavi Coldcloud','Zarch Darksmoke','Zardo Spellbind','Zareoliu Moondream',
'Zarineo Shadowcloud','Zazanda Blackblade','Zazareb Horrorhunter',),

'ELF':(
'Aducguap Fairkiller','Aganrour Reddruid','Apdael Grimblow','Aregnoed Heartflail','Baridubl Brushlash',
'Buteel Snakesinger','Catitilg Breezelance','Cehteel Foxmolder','Ciseriht Dreambat','Conion Magicflute',
'Elenigial Brushsmile','Hisidnith Duskwand','Ibicheth Jadepotion','Ihagudirn Brushwolf','Inocead Touchjuggler',
'Isanads Stormarrow','Itdueh Fairdreamer','Lelosr Deerhunter','Lihediar Icesting','Lihteil Leafwand',
'Nadrihd Swordpotion','Ranisg Searoot','Reniln Gembrewer','Sahiraeg Arrowmaster','Usihonl Pathbull',
'Aggeah Smiledeer','Aressiol Blowmolder','Aruteoh Duneflail','Cahigdoel Moonmaker','Edceit Doommace',
'Enidien Boarstealer','Esarilt Hawkvictor','Gagatb Clericshooter','Hacibhinh Coralhunter','Hisraad Starstreak',
'Idaleid Horsestealer','Lapreeg Vinefighter','Nerigh Snakerider','Nugotbatl Grandpriest','Orasatenn Cometsnake',
'Oribasors Greenrain','Redsigd Beakfollower','Relebeil Battlegrass','Resaplads Grandsnake','Rinien Moonphoenix',
'Ritelapd Starbear','Tipreil Moonlance','Toturh Tearwing','Upteen Swordclaw','Uridiat Scribedancer',
),

'DARKELF':(
'Abaxe Sailormolder','Abekecev Jademolder','Abikovyt Strikehunter','Abirurez Weaseleater','Abiser Clawwanderer',
'Abiuz Ghosttracker','Abixin Jewelcaster','Abxaz Wandseer','Acatuton Cavernsinger','Aclen Bardseeker',
'Aconeri Shadowshine','Acudux Bardtwister','Acuvi Jadeshooter','Adamir Embervoyager','Adbak Starmagus',
'Adcin Tearwarper','Addal Pathtraveller','Adetubi Handruler','Adiketu Mightytooth','Adili Tearmagus',
'Adiniya Bardhunter','Adiray Icequester','Adirot Whipfletcher','Adirulor Mightyweasel','Admif Undermolder',
'Adore Bonerod','Adrod Shadejackal','Adurib Mightywound','Adydadel Redflame','Afase Pathwolf','Afdyn Lowvenom',
'Afeyo Dragonruler','Afosate Spellpacer','Ahady Diveseer','Ahcut Chaoslock','Ahihyxor Maskcarver',
'Ahiob Unholydirge','Ahnak Swampember','Akabudib Coldjackal','Akafuler Jademask','Akamarek Falcontraveller',
'Akarado Boarthief','Akaram Blowruler','Akavenaz Songwhip','Akazekox Bladejewel','Akedebit Waterrot',
'Akemyret Cometrat','Akera Pearlrift','Aketanar Lostbone','Akide Snakewanderer','Akirafe Ivoryrat',
'Akoer Cairnbattle','Akorur Stonecinder','Akovuzys Redwhip','Akoyik Grincurser','Akrek Stonescar',
'Akrid Darkcinder','Akrom Strongmaster','Akusici Taildevil','Alaheya Kickdreamer','Alamid Stonepath',
'Aleda Gemjackal','Alfar Songshot','Alieh Sailormaker','Aliok Froststaff','Aliro Bonetraveller',
'Alron Nestmaker','Aludenit Venomtooth','Alytedot Mightyworm','Alyze Ivoryheart','Amaze Madkick',
'Amoet Vilefinder','Amtux Witvoyager','Amxit Lanceseeker','Anaex Woundseeker','Anaib Frostclaw',
'Anamane Madscribe','Anaoc Chaosfighter','Ancuk Deviltracer','Aneco Whitestaff','Anererul Battracker',
'Anhif Magekiller','Anicobe Snarlsinger','Anifener Woundwolf','Aniid Jadeseer','Anirabyn Cairnrain',
'Aniranax Huntbreaker','Anirokah Wildheart','Anlat Wildbone','Antef Swampmolder','Anuka Wardragon',
'Anyheve Emberhammer','Anykikod Ashtracker','Araad Lowrain','Araaz Cursetaker','Aranal Bleakblow',
'Araned Curseghoul','Aranil Tearfang','Ararek Farsnake','Ararik Hornbreaker','Arata Mightydevil',
'Arate Whitepaw','Aravorin Stoneseer','Araxeko Panthermaster','Ardir Lizardsinger','Aredovi Cattraveller',
'Arefo Highjackal','Arehebal Battlelash','Areil Fangcarver','Arekac Fallcarver','Aremirar Breakeye',
'Arenirab Heartghost','Arerik Earthhorn','Arifih Bleakbone','Arifo Redruler','Arita Scribetracker',
'Arlem Hornwarper','Arnas Warpwarrior','Arobenad Battleghoul','Aroel Wardreamer','Arora Shadeseeker',
'Arore Shadowdreamer','Aroreb Jadearcher','Arorira Blacksnarl','Arosa Riftmaker','Arote Deathpath',
'Aroxif Firefang','Arrad Banetwister','Arrot Cairnwarper','Arrud Wildcurse','Artod Bravevoyager',
'Aruvani Spinebreaker','Arynir Battlesting','Asaud Ashbone','Aselaca Ivoryseer','Aseor Maceslayer',
'Aseseko Rifttooth','Asodoy Stonecat','Asriv Pearlmage','Astit Lockhunter','Ataba Shadowmark','Atacif Silentwarper',
'Atader Doomrider','Atahol Swordtracer','Atanera Scarshot','Atedolat Streakwanderer','Atelar Starhand',
'Aterid Pathstreak','Ateru Chaosbreaker','Atexu Cavetracker','Atied Growlmolder','Atirozu Dusktwister',
'Atiru Cutruler','Atixosav Hawkrider','Atkeh Battletaker','Atoax Cursehorn','Atobeli Clawtwister',
'Atoez Jadeflute','Atohek Pearldash','Atorodan Firesinger','Atutefir Cavegash','Avahalev Swampghost',
'Avain Skyraven','Avaiy Chantmagus','Avitore Bravebat','Avorarey Hammertracer','Avyad Magevictor',
'Axaek Songworm','Axedo Doomskull','Axeoz Hornpacer','Axidi Cursedragon','Axifeca Earthrat','Axufiter Redshadow',
'Ayadunok Blackcurser','Ayiro Chillscar','Azalodax Whitefletcher','Azobaket Banewhip','Azosor Ravenseeker',
'Azotim Starseeker','Azral Doomwit','Azuku Chaosweasel','Balolovy Irondash','Banetiak Warbull','Baror Chillcat',
'Basen Magustraveller','Basor Grimblow','Bavelifo Madchaos','Baxod Moonhunter','Bayanlel Wildtracer',
'Bedaneoh Undermace','Berakner Touchdancer','Beredyun Magestealer','Bexaxidi Windfinder','Bezyn Hammermaker',
'Bidahzax Jaderoot','Bide Rainflail','Bilal Rainthief','Birelahe Firehunter','Bisco Locktracker',
'Biteteem Cursewarrior','Bixod Ironraven','Bixri Mawpacer','Bolan Bonebull','Borasrer Warpmolder',
'Borudix Leapcurser','Bozihcat Bleaktracker','Byka Strongtracker','Cacoruk Snarldancer','Cadalude Bullcurser',
'Calik Dancesnarl','Canri Wandhunter','Cata Gemfletcher','Cedayer Cavebeak','Cehastun Nightpanther',
'Cehined Breakwarrior','Cehukave Venomtracer','Cemad Firecarver','Ceto Bladelance','Cexazrar Scardrum',
'Cidazet Ragehand','Cidedoz Spinewolf','Cika Angrykick','Cilunaub Stonehammer','Cime Ashvenom','Ciyel Crystalwarp',
'Cobixaey Bloodraven','Conol Ivorysinger','Cotekiay Startouch','Cudebifa Earthfang','Cufu Warpsling',
'Cylacrin Cairntooth','Dadir Redlash','Dadiz Moonraven','Dahci Coldthief','Dahte Ragehunter','Dakar Tearstaff',
'Dakbo Magevictor','Daker Redraven','Dalik Breakcurser','Dama Spellcurser','Danayoti Vinemaker',
'Danenode Lockcarver','Danva Pearlrat','Dareniaf Hawksinger','Daritys Poisonmask','Darytol Cindertraveller',
'Dasfe Jackaldreamer','Dasli Redskull','Dasutici Waterwarper','Datebesa Chaosrift','Datok Snakesinger',
'Davaz Wartouch','Daxesok Battledemon','Daxro Woundbreaker','Dayaxol Dirgefinder','Dedah Swampmagus',
'Dedireox Grayspine','Dekabuki Grinbreaker','Dekzo Swampmaker','Delihave Longbreak','Demacaek Warpmark',
'Denahir Rodvictor','Denarmif Spinevoyager','Derataf Lancedancer','Derfe Iceclaw','Derim Earthlizard',
'Desan Farvictor','Desec Vinepanther','Deseriza Silverarrow','Devavale Lostghoul','Dexuxlan Pearlshot',
'Dibar Streakwanderer','Dicovin Chaosrod','Dihaymab Kickvoyager','Dikaxez Moonseer','Dikifan Angrywanderer',
'Dikra Blackfang','Dilam Grimstar','Dilnu Growlsinger','Dilu Rootmark','Dinbe Chantflute','Dira Blackwarper',
'Direkora Bleaktaker','Diris Whitesnake','Dita Mawshooter','Ditycur Starmoan','Dixu Loststaff','Dizadhil Wormpacer',
'Dize Grincurser','Dizla Gashwarper','Dizonool Caverngem','Dizuvmod Teararrow','Dobih Bladedragon',
'Dohaszor Jackalcutter','Dokar Darkarcher','Dolarik Angryblade','Dolba Rainpacer','Dora Swamproot',
'Dora Wardemon','Dorollum Chantwand','Dovoz Jadestealer','Doxerhez Ghosttaker','Dozofovu Tearcat',
'Duceken Bleakmark','Duduskey Doomice','Durna Wardemon','Durra Icedancer','Dykekref Witnest','Dykirat Battleice',
'Dylco Lonewarper','Dynuhoal Woundlash','Dyrireid Flutekiller','Dysoren Riftsnake','Ebenoro Graytwister',
'Ebeuk Scarkiller','Eboel Irontraveller','Eboir Shadedevil','Eburit Wardragon','Ecirocek Cometclaw',
'Ecuver Grimchant','Edaaf Chaosrage','Edadidiv Starfinder','Edaet Stingfletcher','Edaib Cindershooter',
'Edanirul Deathflame','Edaon Angryember','Edaot Catvoyager','Edeaz Whiteweasel','Edelo Battlefletcher',
'Edena Ragebat','Ediketi Snarlbreaker','Edile Ghostsinger','Edirik Flamedash','Edofik Grandwarrior',
'Edoir Deathgem','Efarobe Skullseeker','Efeto Cutstrike','Efirer Earthlash','Efutena Strongspine',
'Ehaod Doombreaker','Eherami Farfire','Ehumalex Pathrider','Ekadino Warcarver','Ekate Earthstrike',
'Ekeen Icehorn','Ekelina Shotmaster','Ekexez Spellrider','Ekfox Scarsnake','Ekihysad Chantwand',
'Ekitaheb Chaosdragon','Ekixix Cairnbreaker','Ekoiz Bravefire','Ekolo Clawrider','Ekrih Lancepacer',
'Ekunirak Wildweasel','Ekuradir Highpanther','Eladicif Ghostsinger','Elaty Starrat','Elelotix Wiseseer',
'Elidilot Songjewel','Eliko Granddemon','Eloid Drumtracer','Elovete Cavemagic','Elucimer Fallcurser',
'Elulanah Ratquester','Emaar Farstreak','Emido Eyetracker','Emoar Icekiller','Emuhy Ironhunter',
'Emzer Tearfall','Endax Moonseer','Enerama Longsinger','Enezat Bullcutter','Enidarem Wounddreamer',
'Enitafal Highwand','Enoat Lonevictor','Enomaki Lizardmaster','Enotir Coldflail','Enrat Ivoryhawk',
'Enykarur Poisonrat','Eradaru Bravecomet','Eradiko Catvoyager','Erafaloh Baneblow','Erahol Lostwand',
'Eravaku Nightcat','Erdal Jadeblow','Erdok Silvervictor','Erear Frosthand','Ereki Skytooth','Erekid Battledive',
'Erena Firesnake','Erenul Warriorshooter','Ereor Wildbull','Ereot Devilquester','Ererore Skullwarrior',
'Ererul Icepaw','Eriit Colddancer','Erine Swampmace','Erizonoc Windwand','Erobala Falconbreaker',
'Erobi Nightgrowl','Eroel Cairnmolder','Eroin Vineraven','Erokira Rootbull','Eronoko Pantherthief',
'Eroresar Venomstrike','Erosen Lonemagus','Erote Chaostracker','Erreh Witmask','Eruvotar Moontail',
'Esihavi Snakeeater','Esuir Chaosstealer','Esuur Emberdevil','Etaac Irongrowl','Etadab Wormmaster',
'Etalaro Mightywarrior','Etaronur Starfang','Etatika Grimdusk','Etericas Stormjewel','Etetar Wildquester',
'Etidota Farbone','Etizuk Fangmolder','Etuli Longwarper','Evaraxo Chaosghost','Evaro Darkworm','Evasa Songrod',
'Evebeli Reddemon','Evkat Ashwind','Evoil Flamesnake','Evorito Wildvictor','Evynuta Grimshooter',
'Exayz Cavernsailor','Exedamer Lashmaster','Exvin Grandsnarl','Exyto Unholyrain','Eytan Flailtracer',
'Ezaxol Fireslayer','Ezeca Dragontracer','Ezeseno Pawwarper','Ezunon Curseblow','Fabehid Cairnhunter',
'Face Shinetracer','Fanorait Curseworm','Fase Gemclaw','Feferari Hailfletcher','Fekot Dancelash',
'Femaxeiv Chaostaker','Fenit Cavernrift','Feraheut Cutsinger','Fidik Weaselpacer','Fidokzir Stoneworm',
'Fihomdel Spellmolder','Firulser Unholytwister','Fitos Strongchaos','Fivitayl Strongfighter',
'Focilier Touchmolder','Fokre Shadowcurser','Fokzy Demonruler','Fotak Chaosvenom','Foyidrot Ashblow',
'Furerez Highbat','Futamnar Lockkiller','Fycab Wildrage','Fycefaur Bonecarver','Fydaler Cutwand',
'Fylil Demonslayer','Fyvdu Divecurser','Habudnav Woundwhip','Hadaztoz Jackalpacer','Hadecrer Cursekick',
'Hady Bonebull','Hafu Redgem','Hanit Nestvictor','Harab Swordtooth','Harexahi Pawtwister','Harra Moonsnake',
'Havak Unholyjewel','Havubayi Magethief','Haxirem Lowshine','Hazetsov Greatwand','Hazifis Ironfletcher',
'Hazki Blackseer','Hebocazo Braveslash','Heda Pathbard','Hedalail Mightymaw','Hede Farboar','Hedi Roothunter',
'Hehiran Wolfhunter','Heni Nightfire','Heniviri Cairndive','Herir Strongarrow','Herut Farwanderer',
'Hetodek Clawtracer','Hibanol Cutgrowl','Hibavey Falconruler','Hiforoal Roothorn','Hifovair Bravequester',
'Hikatole Jackalruler','Hiki Rodshooter','Hilon Frostmaker','Hiri Touchseer','Hironaet Coldrod',
'Hixecnuv Rothawk','Hodob Nightdrum','Hokut Warscribe','Holar Warpkiller','Homra Weaselbreaker',
'Honev Wandpacer','Honey Breaktracker','Honivais Cairnshot','Hori Pearlmagus','Horutut Breakbull',
'Hurazayd Coldhawk','Ibakesi Danceblow','Ibaral Battlebreaker','Ibaza Madcaster','Ibdif Firerat',
'Iberuryr Ironbone','Iboov Rootpacer','Icalat Poisonarcher','Icerinir Ragemask','Icidibo Cairnsnake',
'Icokade Pawshooter','Icoredo Nightcutter','Idaer Shotpacer','Idanele Angrydemon','Idear Jademagus',
'Idetober Embercat','Idikekim Cuthawk','Idinelib Dancedragon','Idiricar Hearthorn','Idiry Toothcaster',
'Idoan Nighttear','Idohola Vinelash','Idsar Wardance','Idvet Lostdive','Idxur Cavernquester','Ifadurar Shadecarver',
'Ifohaz Windpacer','Ihabufi Warflute','Ihaty Clawslayer','Iheva Angrymaster','Ihmyt Wildspine','Ikadac Silverstaff',
'Ikamala Warpfalcon','Ikara Fallquester','Ikareru Pearllizard','Ikati Fightertracker','Ikavise Wildslash',
'Ikear Grimmark','Ikesi Demonruler','Ikiab Witbull','Ikidiref Battlemagus','Ikiya Growlseer','Iknek Magusseeker',
'Ikoab Warfighter','Ikodi Tailpanther','Ikorarer Cutworm','Iktid Frostsinger','Ikuak Battletracker',
'Ikyor Stormarcher','Ilalodo Swordstaff','Ilarari Hopekiller','Ilavat Growldancer','Ildir Cursehail',
'Ileme Cutfang','Ilivira Hornvoyager','Ilofeho Growlkiller','Iloik Lockmaker','Ilore Darkfinder',
'Ilotocan Toothcaster','Ilsyd Breakblow','Iluday Growlquester','Ilukali Strikevoyager','Ilynuku Swampworm',
'Imdox Clawhunter','Iminotos Chillfire','Imior Scribevictor','Imulir Watervenom','Inabava Ragedevil',
'Inabohof Jewelwarper','Inael Dirgehail','Inakad Duskhorn','Inatysi Lonerift','Inava Frostpaw','Ineaz Battlecutter',
'Ineen Nightsting','Ineit Venomwing','Inerudi Ratwanderer','Initaki Magewarper','Innuk Silvermark',
'Inodik Caverncutter','Inofil Divehorn','Inokatir Starlock','Inotera Tailgrowl','Inran Ivorycutter',
'Inuliro Silverlance','Inuti Strongchaos','Inynale Devilmaker','Iratak Cometvoyager','Irateru Ironflute',
'Iraxabil Ragevictor','Irdar Rainweasel','Irelo Devilquester','Irenetan Demoncurser','Iriak Scartaker',
'Irihova Skyshine','Irinavih Nightcarver','Irkiz Staffkiller','Iroar Chaosarrow','Iroha Grandwarrior',
'Irona Swordmace','Ironyno Mightymage','Iroryma Boarseer','Irosuzan Bardvoyager','Irrik Farwarp',
'Irudi Underhail','Iruleri Beakvoyager','Iruror Waterjewel','Iryrenet Clawbreaker','Isakirik Stonespine',
'Isano Grayclaw','Isaye Farice','Isoax Ravenvictor','Italo Irontraveller','Itebid Bonefletcher',
'Itoak Whiterat','Itoav Magichunt','Itoek Firefang','Itois Ashdancer','Itoxerad Weaselvictor','Ituen Clawcutter',
'Iturax Doomice','Ivanati Bonequester','Ivedata Pearlstealer','Ivenel Madfall','Iviot Magicmask',
'Ivirara Venomnest','Ivniv Breakweasel','Ixasa Bardmaster','Ixdim Stormclaw','Ixead Caverndancer',
'Ixesin Ivoryshade','Ixhin Wisedancer','Ixilafo Rootmolder','Ixrar Flamethief','Iyenativ Snakestealer',
'Iyobeso Windgrin','Izacid Icestreak','Izaih Embereye','Izeber Chaoslock','Izeda Starsnake','Izeharu Unholybattle',
'Izivakul Bonedreamer','Izoel Ironwing','Izoki Chantdrum','Izurel Jackalvoyager','Izyor Longwand',
'Kadilefe Snakesinger','Kadisixy Waterworm','Kafusety Songdash','Kahdu Cutcaster','Kahivala Vilehunt',
'Kakinier Magusmolder','Kaluzan Magicwarper','Kamidear Rootfletcher','Kamoyera Ratcurser','Kana Pearlpoison',
'Kanan Earthmoan','Kaneruet Battlemage','Kanil Battlehunt','Kanir Warriorbreaker','Kanivtar Cavernmagus',
'Kanix Firebreak','Kanuron Blooddevil','Kanye Demonmolder','Karardak Windshot','Karer Grimstaff',
'Karoliat Rottwister','Karra Cavernwolf','Karu Warstaff','Kasa Taillance','Kates Nightbone','Katidior Bravekiller',
'Kator Earthdragon','Kavicyl Touchquester','Kaxar Embersailor','Kazizita Dragonpacer','Kebalory Starsnake',
'Kebol Iceslash','Kecytoum Icehunter','Kedad Dreamwanderer','Kelaslad Flamebard','Keleheta Hornsinger',
'Kelunlyr Firearrow','Kemekoma Horncurser','Kenabuis Silentvenom','Kenar Watervine','Kenircir Mightymage',
'Keniroav Hailruler','Kenis Silentsnarl','Kenke Cometleap','Kerekiir Waterfire','Kerik Unholyjackal',
'Kerra Banedash','Ketoy Ragemaw','Kicalean Hightear','Kidaf Icelash','Kidekit Ivorydragon','Kinvi Clawrider',
'Kinyx Firestealer','Kirik Blackcutter','Kirik Coldwhip','Kirilar Firesinger','Kiro Bleakcarver',
'Kisetral Tearfletcher','Kivir Hornquester','Kiyza Bonemolder','Kizesiti Rodrider','Kobce Moonrage',
'Kobinoak Ashfinder','Kodetay Woundsnake','Kokutaih Bonebreaker','Koner Songtracer','Korizlax Breakwarper',
'Koronkut Moontraveller','Kosinise Falcontaker','Kosysuk Banetracer','Kotirmel Deathvoyager',
'Kotra Stormbull','Koxinais Jadedive','Koxitile Chaosmage','Koxko Rotwarrior','Kozecuod Warpstaff',
'Kuyi Longdirge','Labak Coldfletcher','Labizik Mooncaster','Laciyib Duskbreak','Lacizkaz Moondance',
'Lahro Underfire','Laka Mawwarper','Lakuvrub Grindancer','Lala Swordclaw','Lalehler Chilltwister',
'Lalyruk Snakequester','Lanan Breakgrin','Lanarbar Warbat','Lanne Venomseer','Larar Highroot','Lared Skydancer',
'Larenoir Spinefinder','Laribiru Starwarper','Lasa Ivoryember','Latatuco Longruler','Latenvin Teartaker',
'Ledinnit Loneshine','Leduc Underscar','Lehenona Starraven','Lekathid Danceflail','Leki Magicstrike',
'Lekusion Catfinder','Lekzi Skulleye','Lenra Bonewhip','Leriv Bravelizard','Leru Kicktraveller',
'Letec Embermoan','Letma Firesnake','Letun Arrowmolder','Liba Cutrider','Lifavrer Bardtwister','Liha Shadehammer',
'Lihle Bladeeye','Likxa Moongrowl','Linaf Wormrider','Linen Warcat','Linenal Chillcaster','Linonzoh Strikequester',
'Lirer Skullhawk','Lirer Stormtouch','Liribidi Swampmaster','Liroxit Fluterider','Lirun Strikecutter',
'Lisotied Wiserat','Lobor Nightdance','Lobycuv Gashfinder','Locirkel Teardemon','Locotnas Spellwanderer',
'Lodibveh Grandjackal','Lohekoax Leapwarper','Loky Loststealer','Lolre Hopehawk','Loralear Gemdragon',
'Lorri Gemlizard','Losadaku Ragenest','Lovariho Greatwhip','Lovifaad Viletaker','Lovro Boneghoul',
'Lukre Lizardfinder','Luledam Frostbattle','Luteredi Divetracker','Lutibafi Whiprider','Lylukkac Bleakstar',
'Mabed Angrybeak','Makirar Clawcutter','Malenoxa Dreamsailor','Manna Warshine','Matno Chillwing',
'Maxitedo Clawslayer','Mayikeb Wildraven','Meba Bravefighter','Medaxani Fighterwanderer','Medireir Streakdancer',
'Melivnih Rainmagus','Mexer Skydreamer','Mibetief Nightwand','Mikavrey Fireblow','Mirro Scarruler',
'Mizilyot Snakecutter','Mokytoha Whitebull','Morodrok Woundfalcon','Motka Beakfletcher','Movoz Highdash',
'Moxi Cairndreamer','Muti Nightcurse','Myderoas Fireworm','Nabahed Chillstorm','Nabyklan Witstrike',
'Nadte Shinetracker','Nake Viledevil','Nakixer Darkwound','Nakuc Dashmolder','Nakudiha Ashsnake',
'Nalazul Songmoan','Nane Chillwanderer','Nanir Chaosmask','Narar Raincarver','Nareraud Whiteshade',
'Naroc Ghostthief','Narti Greatfalcon','Nasa Shadetaker','Nasoz Darkstar','Nasun Cavebull','Nati Bonefall',
'Natimeor Ghoulcurser','Nato Crystalmask','Navra Rainrat','Navur Stormboar','Naxe Stareye','Naxir Nightdreamer',
'Nazelare Maguscaster','Nazha Spinecutter','Necolor Lanceseer','Nedanone Skullseer','Nedariab Shinefinder',
'Nedotax Macetracker','Nehalian Waterwolf','Nehibyni Dirgerider','Neky Doomchaos','Nenar Deviltraveller',
'Nenikial Hopegrin','Nenixnas Horndancer','Nera Unholymaster','Nerivaax Skywanderer','Neryt Coldsnake',
'Nexodour Boneruler','Nidyvdud Gemfighter','Nifirely Shadownest','Nike Stonefire','Nikor Windslayer',
'Nilezay Shadowhammer','Nilmo Spineraven','Nilov Spellhunt','Nilyrove Bravemaker','Nimak Spellcinder',
'Niraxbon Songvictor','Niri Darkstealer','Nirik Magusthief','Nirohaen Icewarper','Nirotecu Coldseeker',
'Nirto Hammerthief','Nisehor Wildarrow','Nital Cursecat','Nitireod Hopeflame','Nivarusa Magedancer',
'Nive Raincat','Nixak Viletooth','Nixiful Shadewand','Nixikita Cutbard','Nixu Divejackal','Nizehix Boarruler',
'Nobe Moonmaw','Nodelrit Warseeker','Nofol Starsting','Nofulyro Bravesling','Nolenet Nightstaff',
'Noli Greatwound','Nonru Hawkwanderer','Norirar Wolfcaster','Noron Dancetraveller','Norti Madfang',
'Nosut Devileater','Notidira Cursebreak','Noxyteki Slingwanderer','Nubam Warmagus','Nufer Dashthief',
'Nukazryk Stormseer','Nukik Handcarver','Nulokkir Mightynest','Nurokedi Bloodbattle','Nusse Chillstrike',
'Nuve Bravedive','Nybre Warsnake','Nydednom Battlesailor','Nydri Poisongrowl','Nylab Bullsinger',
'Obaka Crystalflame','Oboda Bloodgash','Ocrin Duskhunt','Odahu Angrymolder','Odain Rotghost','Odaye Drumtracker',
'Odeniser Pearltracker','Odidiri Bardruler','Odinet Vinerod','Odireto Wildhunter','Odoracid Devilsinger',
'Ofiki Ashbull','Oftes Battlemaster','Ohaal Frostweasel','Ohahyvo Moonjackal','Ohtir Grandrat','Okaiv Warriorvictor',
'Okane Danceblow','Okesaf Witdreamer','Oketukab Falconvoyager','Okhev Duskdevil','Okouy Magusvoyager',
'Okoza Shadesnake','Okudib Scribetraveller','Olalulus Falconsinger','Olarida Lonecutter','Oldan Spellhorn',
'Oliaf Warriorwanderer','Olinabis Cursemaw','Olkox Gemwolf','Olril Lostgash','Olxix Waterrod','Onaic Strikestealer',
'Onaketat Watertooth','Oniit Snakeseeker','Onoduk Eyewarper','Oraceki Stingmolder','Orady Battledancer',
'Orakir Nestbreaker','Orali Blackrot','Orayuka Cairnbreaker','Orber Nightcaster','Ordir Batquester',
'Ordix Rotbreaker','Oremera Nestshooter','Oretada Weaselmaster','Orire Wingsinger','Orixe Grimlock',
'Orizeric Boneworm','Orkar Swordtaker','Orker Hammertracker','Orkir Boneruler','Orlen Dirgesnake',
'Ormur Silverember','Ororar Spinemaker','Oroxa Whitecarver','Orubo Weaselcutter','Orucoyin Bonegrin',
'Oruke Deathrat','Orutehid Wildspell','Oruto Skullsinger','Osiin Frostdemon','Otetab Gasheye','Otexeker Swampsword',
'Otinorex Startraveller','Otivode Blackdreamer','Otlad Whitechaos','Ovaeh Growlvoyager','Ovahucom Whitebattle',
'Ovaleri Flameraven','Ovidema Swordhand','Oviraro Silentflute','Ovoxetah Slingseeker','Oxaaf Moonsting',
'Oxareze Moontouch','Oxaro Gashdrum','Oxatadil Warember','Oxbas Boneraven','Oxekanab Silenttooth',
'Oxeok Vileseer','Oxeza Snakecarver','Oxidi Strongleap','Oxkiv Venombull','Oxror Greatkiller','Oxyat Skullsnake',
'Ozadat Lizarddreamer','Ozazid Bonebeak','Oziev Emberdash','Ozimelit Highquester','Ozioc Leapwanderer',
'Ozkat Nightcutter','Ozker Longflute','Ozoar Coldthief','Ozokyre Silverraven','Rabak Dirgemask',
'Rada Whiteflame','Radih Riftwanderer','Radix Moonfall','Rado Madcat','Radri Cindertwister','Rahokit Cavernhawk',
'Rakeroir Shinefinder','Rakid Grandkiller','Rakitoer Slingruler','Rakivuca Moongrin','Rakre Crystalfalcon',
'Rakxa Jadeshine','Ralurryt Marktwister','Ramek Raventaker','Ramicib Scarmolder','Ramoveor Cavernbane',
'Ranaxer Streakdancer','Ranibol Flutemaster','Raniseat Poisonsnake','Ranobily Lanceslayer','Ranokar Pantherbreaker',
'Rarabik Archercaster','Raral Greattwister','Raralola Cavernruler','Rararece Poisonlock','Rarasox Coldmagus',
'Rareleat Swampice','Rarihiax Venomdreamer','Rarilear Cavernclaw','Rariniur Darkshot','Rarixdat Eyepacer',
'Raro Lockdreamer','Rarod Handseer','Rarodexe Ashghoul','Rarombat Kicktaker','Raron Rootsling','Raros Flailstealer',
'Raruz Stonegash','Rarze Undersnarl','Rasab Bravetail','Rasi Cutfalcon','Rasin Panthershooter','Rasitedo Pawmaker',
'Ratem Dancepacer','Ravevyac Undercat','Ravikiri Tearsling','Ravo Battleweasel','Raxabim Snakeslayer',
'Raxek Coldghost','Raxer Bonewing','Razaroro Ragefang','Razek Heartwolf','Razeryem Shotmaster','Razulif Bonefletcher',
'Reca Ivoryslash','Recovoh Lowtracker','Redad Nestcurser','Rede Bonecaster','Redot Witdrum','Refavdik Ivoryruler',
'Refva Vinefletcher','Reheruar Windcutter','Rehinrat Swordclaw','Rehumur Warwise','Rekah Skybull',
'Rekakati Nestthief','Reko Ironscar','Relet Breakwarrior','Relne Ironscribe','Relti Lostwing','Remanuac Undersnarl',
'Renetein Vinemolder','Renir Lonecutter','Rerexet Divecinder','Rerit Gemlizard','Rerke Tearcarver',
'Rerku Witscribe','Rero Rootdash','Resa Ashbard','Resmi Lostslash','Reson Highfinder','Retahah Jackalmolder',
'Retanrak Starboar','Retar Nightraven','Retaz Bonewanderer','Reter Jackalsinger','Reve Unholywit',
'Revi Chilllash','Rexde Pearlgrin','Rexoskir Breakbard','Rexoxar Bonefletcher','Ribon Jadeghoul',
'Ribyxer Tailsting','Rida Deathskull','Ridakcys Warmaker','Ridakel Pearllizard','Ridir Vinefang',
'Ridoc Frostpoison','Rihinuor Riftlizard','Rikezem Hopejackal','Rikivos Dragoncaster','Rikmu Loneice',
'Rikorote Rotsailor','Rikur Eyerider','Rilud Wilddrum','Rimki Wisesting','Rinidot Mawtaker','Rinuh Wolftraveller',
'Riraf Stafffletcher','Rirarufa Vineraven','Rirca Magefletcher','Rirebit Fallthief','Rirec Wildbat',
'Rirerlen Lostlance','Rireyrab Cavernshadow','Riromiro Whitesling','Riroxxur Bardmolder','Risax Falconseeker',
'Ritec Grimeater','Riter Mooncomet','Riteraih Silentsnake','Riti Moonstaff','Rito Wingseer','Ritsi Magetaker',
'Rivazdal Battlemark','Rizobavu Snakevictor','Robazixi Mawmaster','Rofar Nightclaw','Rofesoxa Spellrat',
'Rohik Poisonraven','Rohozron Farblow','Rola Ratthief','Rola Witbull','Role Bleakarrow','Roledin Hopehunter',
'Rona Pearlrod','Ronir Duskpacer','Rono Divemark','Ronsi Waterweasel','Rorakyer Nightlance','Roranol Dragonkiller',
'Rorarbik Boneclaw','Roril Blackwhip','Rorlo Bonefire','Rorofrit Coldfletcher','Rorohyl Skulldemon',
'Rosetnak Silvermaster','Rosit Chaospaw','Rota Cavernrider','Rotac Lasheater','Rotit Lowdemon','Royakita Blackstealer',
'Rozurake Sailorruler','Rubeloab Dreamhawk','Rubi Skycomet','Rucorlif Silentvenom','Rudor Lonepacer',
'Ruha Shinevoyager','Ruhalcol Riftmaster','Rukitret Magicfall','Rule Nestcarver','Ruli Tearhawk',
'Rumil Songwhip','Runle Firemace','Rurakiek Ironmask','Rurenoxo Underghost','Rurin Taildemon','Ruriroam Ragedemon',
'Ruroh Farpaw','Ruta Bonetraveller','Ruteyifu Swampdance','Rutovzor Farheart','Rutu Spinestealer',
'Ruxetiud Grandmage','Ruyar Shadowcaster','Ruza Ironrain','Rydar Tearvictor','Rykanira Pearlsong',
'Rykorete Crystalwit','Ryluhov Chaoscarver','Rynedaix Riftfang','Ryravuat Shadowsailor','Ryruhcik Witmolder',
'Rysikoir Moonwarper','Rytireen Darkboar','Rytodtol Bravedash','Ryvurir Redgrin','Ryxordav Bonenest',
'Saderiir Tailhammer','Sadikrox Vineflail','Safa Arrowseeker','Safuxker Clawcurser','Salirnod Ironruler',
'Salix Bonecaster','Samaroti Clawthief','Sane Grayshine','Saromiit Coldseeker','Sarsa Fangmaster',
'Sarutyim Nightember','Satne Banemaker','Savahbar Magicquester','Savud Weaselcarver','Sazi Bravestealer',
'Secal Shadowhorn','Sedovinu Teareater','Senazoot Magicpaw','Seririaz Greatmaster','Setuzib Catkiller',
'Seveteeb Battlesnake','Sibarer Bladetooth','Sidarote Hailseer','Sindo Gemscribe','Sirazbal Crystaldevil',
'Sirobir Kickpacer','Sizosiye Redwarrior','Sodukala Watergrin','Sofor Shadowmolder','Sohid Flailwarper',
'Sokenen Whitemark','Sokir Ashflail','Sorir Bonecurse','Sory Coldscribe','Soselac Stargrin','Sotiruon Jadeice',
'Sukev Unholyrift','Surim Ragestealer','Syhke Ivoryfalcon','Syrev Underwit','Tabodune Frostvictor',
'Tadeb Beakeater','Tadel Scribepacer','Tadha Silverfinder','Tadro Icelock','Tadur Tearthief','Taduroka Fardragon',
'Tafadium Dreambreak','Takek Ragehunter','Takri Hornstealer','Talef Nightrain','Taliduk Grayblow',
'Talky Lowspine','Tamik Stonebreaker','Tanikavy Riftruler','Tanut Cursedragon','Tararuz Ironwarrior',
'Tarenrex Moonpacer','Tarideno Frosthawk','Tarma Silverwit','Tase Vilecat','Taticxex Starlance',
'Tatodfik Highbane','Tazab Ivoryvictor','Tazinooh Cavesnake','Tebe Bleakdevil','Tecru Touchtraveller',
'Tele Skulldevil','Tenaveum Heartfalcon','Tenit Dirgeshot','Teri Witdemon','Terol Silentshooter',
'Teros Ivorytwister','Teryrir Dashvoyager','Tetihfer Bloodsting','Tetri Lostpacer','Tetulain Cuttaker',
'Tevom Chaosdragon','Tezfu Ivoryghoul','Tibikih Fangtraveller','Tibodnor Snarlcaster','Tiburik Gashcaster',
'Ticelixa Lowfalcon','Ticra Cutcarver','Tidadoki Wildmolder','Tidinari Vilehammer','Tiditud Ashshot',
'Tidse Warsnarl','Tikor Boarseeker','Tilad Riftmage','Tileh Ivoryskull','Tinetar Cursebat','Tinih Battlespine',
'Tiniyah Frostwind','Tinot Vilefletcher','Tireyaav Clawtwister','Tirizcub Fardream','Tirso Tailbard',
'Titaduix Mawfinder','Titevbar Coldseeker','Titor Ironcat','Tixbe Banedash','Todi Lostfighter','Toduriya Riftboar',
'Tokenuad Whiteworm','Tokok Wandvictor','Tokon Whippacer','Toldo Cairnstaff','Toradale Chaosquester',
'Tore Strongcutter','Torerair Bonecutter','Tove Spellseer','Tovu Mawtaker','Toxaned Ivorylance',
'Tozuvyad Panthermolder','Tufadeex Stormraven','Tura Starnest','Tuzy Weaselmaster','Ubasale Cometwarrior',
'Ubika Doomwolf','Ucael Eyeseer','Ucerir Battleworm','Udeir Tailquester','Udetan Dirgehorn','Uditi Ratfinder',
'Udnas Cindertracker','Udoxa Bonetracer','Ufezac Nightraven','Uhidave Angrypanther','Ukaro Lonetraveller',
'Ukazuyaz Clawfletcher','Ukera Icedrum','Ukese Ashtooth','Ukiay Angryshine','Ukror Ragemask','Ukymalit Lizardtracker',
'Ulaor Stormghost','Umirited Nightcat','Umori Lashthief','Umvat Wisemagus','Unalit Cutsting','Unari Snarltraveller',
'Unuil Devilsinger','Urear Greatsailor','Urerad Blooddragon','Urikik Skullcurser','Urinafe Longroot',
'Urirehir Silentrat','Urtox Starhand','Urvev Silenthammer','Usaar Toothfinder','Usatihi Whipcurser',
'Usefav Poisonstrike','Useom Ravensinger','Usodado Farcomet','Utahen Scribecarver','Utavakir Wingbreaker',
'Utesit Blackpoison','Utikiser Warriorbreaker','Utiril Drumfinder','Utohu Moanruler','Utvic Nightthief',
'Uvera Bleakhand','Uvirox Ghoulstealer','Uvoal Catcutter','Uxlyt Banedragon','Uxuav Eyecurser','Uxyhadad Macedancer',
'Uyrem Wisehunter','Uzenifut Rothunter','Uzihateb Wardusk','Uzlak Dirgeseeker','Vadirare Roottracker',
'Valonkid Snarlkiller','Varadaal Stonerat','Vararero Doomwarrior','Varerkin Unholymace','Varko Snarlmolder',
'Varoh Stonemage','Vasymoto Masktwister','Vazuriik Witmolder','Vefu Underbreak','Vehry Warwarper',
'Veke Vinedancer','Vekibrir Bleakwhip','Venohar Witslayer','Veraz Warriorfletcher','Verurir Slashslayer',
'Verzo Blackboar','Vibanin Clawmaker','Viblo Starmaster','Vidyn Caverntraveller','Vikzo Waterhammer',
'Vini Flametracer','Vocik Falconhunter','Vokisair Chantraven','Vomazos Chantshooter','Vonan Woundseeker',
'Voreriha Eyesinger','Votyriod Greatstreak','Voyi Riftwhip','Vudat Bravefalcon','Vunozer Bladetracer',
'Vunux Archertracer','Vykodido Jeweltwister','Xable Startaker','Xahez Riftvictor','Xakac Ravenstealer',
'Xalaboot Vileghoul','Xalxe Bloodsting','Xamerol Moontraveller','Xarot Pawtraveller','Xarukaor Jeweldancer',
'Xatarobo Swamprat','Xatilod Moondash','Xatulrok Wildvine','Xazeryit Staffcurser','Xebareko Divemaw',
'Xeco Catpacer','Xedat Chaosrage','Xedyr Bardfinder','Xehomah Fightereater','Xelo Clawwanderer',
'Xenaz Devilsinger','Xenuk Wildtwister','Xerasol Understealer','Xerid Silentquester','Xeyirat Bleaklance',
'Xibra Cometvictor','Xiharato Stonejackal','Xilat Unholyscar','Xilohior Silentfalcon','Xiretoxi Mightymark',
'Xirot Kickmaker','Xitanrix Staffshooter','Xiveduki Vinequester','Xoradiam Starwarper','Xoseruir Chilltouch',
'Xotez Cavernseer','Xotox Undertraveller','Xuber Scarkick','Xuliz Skullvictor','Xunamuol Handwanderer',
'Xutaveno Battlescar','Xutku Gemseer','Yatel Cutrod','Yaza Touchfinder','Ybanaki Lowmolder','Ybaok Banehunt',
'Ydate Snaketracker','Yedaseav Bloodraven','Yerol Icescar','Yerucaat Banetouch','Yhsir Blackstorm',
'Yidinar Icesnake','Yidod Duskhunt','Yizokavi Shadecutter','Ykureno Watermask','Ylait Underpaw',
'Yloxi Cavetraveller','Ylrah Gashhorn','Ynikisa Gashtaker','Yninoko Longcinder','Ynmih Fallcurser',
'Yoxaloh Moonkick','Yoxxo Rotdemon','Yrato Ivoryvoyager','Ytcar Hawkwarper','Ytetehed Ivorydreamer',
'Yudo Songvictor','Zadertun Duskhail','Zahnu Cutdragon','Zaki Beakruler','Zalad Cavernblow','Zaladiis Fallvictor',
'Zalehuux Archermaker','Zarba Nestvictor','Zati Venomseer','Zatyrak Strongdancer','Zaze Silvervictor',
'Zede Chaosmoan','Zerak Caveraven','Zeslu Gemshooter','Zetidcis Undersinger','Zexaled Vileghoul',
'Zezor Stonefinder','Zibinrah Banemaw','Zidetex Bulltaker','Zikifaro Dashseer','Zila Blackdemon',
'Zilaxkor Nightskull','Zines Embervoyager','Zoked Hornmaker','Zora Rodtraveller','Zoribezy Starblow',
'Zoror Bonetouch','Zotidar Poisonwhip','Zoxo Cometcinder','Zulitiza Eyetracker','Zusaz Battleghoul',
'Zuxyrofu Waterlance','Zynos Skydusk',),

'VILLIANESS':(
'Alessandra Winter','Aphra Noire','Aphra the Poisonous','Astarte Vixenia','Cornelia Blackheart',
'Cyrilla Wynter','Damia the Obscene','Delilah the Unclean','Editha Nyx','Emeraude Wynter','Gertrude de Sangria',
'Hildegarde the Serpent','Huldah the Ill-Famed','Huldah von Garvel','Huldah von Malheur','Isadora the Ill-Mannered',
'Kali the Shadow','Leila Grendel','Lilith Viridian','Lobelia the Temptress','Lucretia the Obscene',
'Lydia Viridian','Magda the Grotesque','Maudetta the Hellcat','Morgause Cygne','Morgause Falkwing',
'Morgiana of Mourne','Natasha the Raven','Olga Wynter','Prunella Helborne','Ravenna Helborne','Rubella the Gruesome',
'Rufina del Mourne','Sophronia the Succubus','The Deadly Fury','The Fanged Shrew','The Festering Banshee',
'The Forsaken Harridan','The Gruesome Serpent','The Infamous She-Wolf','The Infectious Hag','The Terrible Hag',
'The Unclean Tigress','The Unpleasant Hellcat','The Vicious Virago','Theodora Corvida','Ursula Tempest',
'Vanessa de Blackheart','Zelda the Vixen','Zsazsa Drear',),

'GNOME':(
'Berenbell','Bleewinkle','Bunkkor','Bunko','Bunktwiss','Corynottin','Daermut','Dalbur','Dalkor','Dimbjon','Dwobmut',
'Ellyjowinkle','Elmip','Errkin','Errwocket','Fonman','Fudnab','Garman','Gerbur','Gergel','Glimdo','Glimmadge','Hednig',
'Hodgeji','Klemwicket','Lindjon','Loopder','Loopger','Looppen','Loopzig','Lumman','Mardmut','Minnijon','Nambur','Ningel',
'Ninrick','Nobder','Olffnock','Pilder','Piljon','Pilmip','Ranzji','Roonji','Roonnor','Roygel','Seejon','Turjon','Waynottin',
'Wimmottin','Zookwyn',),

'WARRIOR':(
'Paien Swiftstep','Sahak of the Four Devices','Otrygg Pikethrower','Lucan Godsmark','Soroush Farhaan',
'Vagn the Mongoose','Motya the Black','Hjalti the Club','Thorvald Cougartrapper','Vasilii the Boar',
'Etienne Tracethoughts','Bazil of the Fighting Tongue','Lehen the Delirious Wizard','Acennan Oakhome',
'Godric Copperlance','Cheslav Stanislovovich','Sighvat Pigtrapper','Cadmon Goldaxe','Brogan Gaderianson',
'Solvi Aslakson','Marz the Unspeakable Wizard','Faran Axewielder','Kari the Lance','Edlin the Jeweler',
'Maule of the Frigid Waters','Majnun of the Eight Eyes','Attor Beechson','Ivan the Nimble','Pruet Nimblestep',
'Besyrwan Foxtooth','Lar the Tinker','Semyon Vanechkaov','Ingi Lizardseeker','Semyon Armanovich',
'Chretien Traceflight','Ekaitz of the Red Hand','Garabed of the Swarming Faces','Jasha the Trickster',
'Hrypa the Shopkeeper','Dragon Aldredson','Bodvar Godssword','Zivon the Poisoner','Deniska the Guardian',
'Rognvald Greenmark','Ranie Bijan','Hadrian Darklash','Vermund Blackmark','Deogol Pikethrasher',
'Finn Daggerthruster','Eguen of the Lightning Hollows','Hakim Mika','Cougar Aartsson','Govannon Graybird',
'Edlin Lucanson','Ulf Lancethruster','Besyrwan Athelstanson','Jermija of Malotin','Yrre Yellowhelm',
'Yngvar the Sword','Monkey Eriansson','Hord the Arrow','Ormod Moonbody','Kjell Stillstick','Lar Knifebreaker',
'Ogier Ghostmover','Jakue of the Green Spirit','Gremian Clubthruster','Gildas Elderleaf','Odon Eldergold',
'Nadir Fadil','Torr Gaderianson','Thorgrim the Turtle','Inguma of the Ethereal Tongue','Bogdashka the Bear',
'Aart the Painter','Ingolf Turtlechaser','Einar Axewielder','Majnun of the Four Masters','Grani Starsword',
'Rafiki Amal','Snorri Weaselkiller','Kolbein Doghead','Hring Steinkelsson','Herjolf Snorrissen',
'Arnlaug Greenarrow','Ferragus Phantomtouch','Maore of the Night Face','Aslak Pantherseeker',
'Onbera of the Western Valley','Hroald the Staff','Itzaina the Blood Sorceror','Tamar Graystick',
'Solvi Hjaltison','Fisk Graybody','Athelstan Demonford','Arman the Gamesman','Ozur the Cougar','Vanechka Danyaovich',
'Alfgeir Strongmark','Slean Eaglerunner','Erian Fishtrapper','Jacques Phantomstep','Jal Yasir','Gildas Daggerthrower',
'Hedeon the Nomad','Olezka the Seeker','Eder the Ivory Sorceror','Gasteiz the Storm Wizard','Bedrosian of the Six Colors',
'Bogdashka of Homel','Raziq Shareef','Itzaina the Blue Wizard','Grim the Crow','Rabican Phantomtouch',
'Grimbold the Stonecutter','Yrre Staffthruster','Wregan Hogtrainer','Sarlic Wolfhunter','Finn Vandradson',
'Erruki of the Golden Eye','Alvar Blackgarden','Besyrwan Bluecloud','Nuxila the Battle Sorceror',
'Grimbold Aartsson','Pyotr the Hare','Brand Weaselherder','Finn Macethrasher','Valdemar Darkflower',
'Yurik the True','Torsten Goldspot','Penrith Daggerwielder','Tellan Cedargold','Odon Elmson','Talon Slightflight',
'Maju the Dawn Wizard','Aslak Ratmaster','Atol Elmgrove','Gunnlaug Arrowbreaker','Gizur Valgardssen',
'Jaizki the Unspeakable Wizard','Banning Oakheart','Ragnar Grayson','Jamshaid Nafis','Vassi the Wildcat',
'Deniska of Ust-Vym','Jakobe of the Golden Soul','Hibai of the Timeless Land','Hring the Mace',
'Torr Firehammer','Svein the Pike','Odon Redclub','Romochka the Nimble','Raven Maccusson','Maccus Ironknife',
'Urtun the Undying Sorceror','Yasha of the Watch','Kevork of the Eight Fires','Zigor of the Eternal Place',
'Zarif Talya','Wyrm Athelstansson','Erramu of the Gray Body','Geir Illugison','Finn Swordthrasher',
'Orixe of the Bright Forest','Ketil Firesaber','Ilya of Trepol','Endura of the Delirious Body',
'Glum the Shark','Bellinus Sarlicsson','Oxa Selwynson','Derian Beechgold','Amundi the Staff','Grisha of Slobodskoi',
'Mustafa Mubaarak','Otsoa of the Pale Shore','Itamar Rasul','Olaf the Saber','Tamar Bluebody','Fadeyka of Mikulin',
'Manton the Archer','Galan Lancethrower','Osric Bluedagger','Valerik the Wyrm','Raaghib Mannan',
'Edric Tellansson','Arnfinn Silverarrow','Luzea of the Shadow Spirit','Zeru of the Middle Spirit',
'Hrypa Beechgrove','Baiardo of the Fighting Tongue','Nuno of the Glowing City','Ibrahim Miksa',
'Strang Aldergrove','Ozur Macewielder','Harkaitz the Laughing Warlock','Alain Cleverflight','Possum Banningson',
'Mikhail the Doomsayer','Errando of the Icy Ocean','Manton Redwater','Fridgeir the Axe','Tellan the Chandler',
'Hauk Strongdagger','Ragnar Tostison','Steinthor Bluemark','Torr Cedarwood','Hovan of the Many Devices',
'Gurutz the Gray Magician','Hawk Sleansson','Osric Littlespot','Vartan of the Eight Rings','Bernat the Middle Wizard',
'Gasteiz of the Unspeakable Sea','Geir the Fish','Garabed of the Three Winds','Shawar Zemar',
'Maccus Dragonmaster','Bikendi the Ninth Wizard','Indar of the Ethereal Body','Besyrwan Tinclub',
'Strang the Fisherman','Dimitri of Chertoryisk','Cyrus of the Seven Powers','Erlend Bluemace',
'Thorir Ratmaster','Hakon the Pike','Vachel Smooththoughts','Viktor the Deer','Sigurd Sumarlidisson',
'Derian Swordthrasher','Harald Moonarrow','Nechtan the Farmer','Marlon Phantomthoughts','Rheged Pikethrasher',
'Harek Lancethrasher','Edur the Evening Wizard','Ander of the Ancient Island','Borya of Driutesk',
'Gremian Staffwielder','Hastein the Arrow','Assim of the Six Eyes','Sarlic the Assassin','Lucan Birdtrapper',
'Hogni Ingolfssen','Ivan the Possum','Bjorn the Frog','Gaur of the White Hand','Chanler Quicktouch',
'Nishan of the Eight Wonders','Lukyan the Strong',),

'HALFLING':(
'Boirry','Frappi','Drogo','Fragrin','Periam','Riabo','Budoc','Merebo','Bem','Suppi','Merodo','Driagrin','Friabo','Sudo','Siarry',
'Meredoc','Ribo','Froibo','Siado','Fribo','Surry','Perodoc','Frubo','Dragrin','Meroido','Drubo','Bogrin','Rirry','Peroibo',
'Fridoc','Droigrin','Perum','Sarry','Perubo','Merago','Drarry','Berry','Perago','Soim','Meribo','Rugo','Dredoc','Suppi','Drum',
'Rigrin','Dragrin','Meredoc','Driado','Meram','Drabo',),

'MONSTER':(
"Bigslime","Bonerot","Darkbane","Darkmaw","Darkstomach","Fouldweller","Foulshade","Foulshadow","Ghostdrool",
"Giantclub","Greatscum","Greattongue","Irondrool","Madshade","Metalscum","Pukegouger","Screamjeer","Shademaw",
"Spineooze","Vomitbreaker","Aep'tshallelh","Bbhanorh","Catllliga","Eg'bhulaugtho","Eho-ggu","Hoacthuar","K'delak",
"Keghulhabotl","Kego-ughol","Mazh-stlzo","Ntulloskr-hac","Oithachat","Othiqudep","Otllama","Phameha","Phug-mmm",
"R'lolathua","Ra-ul","Rsakruaru","Sthabonakit","Ugotho","Ulleita","Yin'sammmone","Zhomarnygo","Zoth-abo","Chainmourn",
"Chantmoon","Cursechain","Darkmark","Darkstorm","Deadbeast","Deadbrood","Deathcairn","Deathscar","Direstalk",
"Dreadbone","Dreadfury","Dreadhaunter","Ebonmark","Ebonshade","Ebonspectre","Ebonspectre","Evilheart","Fardusk",
"Farhaunter","Fatemourner","Grimbone","Ironcrypt","Redcry","Wildkill","Blackbind","Coldspectre","Cursefury",
"Darkdusk","Deadrule","Devilspawn","Direbeast","Direcry","Dreaddusk","Dreadmoon","Dreadstalker","Dreamknife",
"Ebonscream","Evilspirit","Farrip","Farstrike","Fogkiller","Gloomscar","Griefshadow","Icegloom","Ironfog","Reddirge",
"Wildcairn","Wildmurk","Woeghast","Blackhowl","Blackspawn","Coldweeper","Cruelspawn","Cursefire","Darkchain",
"Darkhowl","Evilbind","Evilshade","Fatesoul","Fogpain","Gloomsoul","Grimsoul","Hellbrood","Hellgloom","Murkhand",
"Nightdoom","Plaguebrood","Plaguescream","Redrule","Scarfate","Shadowwoe","Sinspell","Steelbite","Wildshade",
"Aulko","Beth","Cargi","Doria","Durdela","Dutur","Eglinglaulk","Egori","Glrntug","Gweg","Haelutuglimman","Hangon","Indorca",
"Kaeturianglath","Kalitun","Kori","Laurchur","Moruit","Olonchan","Rgland","Sandetu","Shmatha","Valortha","Vandrorg",
"Vathmo","Shin-Chewer","Thrall-Taster","Helm-Hammer","Helm-Tenderizer","Knee-Eater","King-Stomper","Skull-Mangler",
"Neck-Chewer","Sword-Reaper","Knee-Chopper","Goat-Taker","Thrall-Taker","Spine-Chewer","Bone-Folder","Dog-Snapper",
"Man-Stalker","Arm-Tenderizer","Skin-Smasher","Head-Breaker","Tooth-Gnawer","Face-Tenderizer","Face-Chopper",
"Head-Stealer","Corpse-Crusher","Light-Tenderizer","Horn-Gnawer","Khelguzun","Binarakh","Barukgundil",
"Khelguluth","Barukloth","Mornigin","Rorthin","Bizardithil","Kelekzanik","Muzarduruk","Arzarath","Thukzizil",
"Ibiznizil","Khelednuz","Erekgundag","Nukulu","Innuzum","Guzibmoruk","Khimilagul","Ibinzukum","Izukgul","Ranmor",
"Kelekmud","Erekmormuk","Agazthidul","Guzibmormuk","Patchpale","Kilpad","Stalemuck","Foulor","Rotcloud",
"Sickpad","Gapclawer","Rotgnawer","Kirmcrawl","Frotheater","Palemuk","Rotas","Kokmuck","Rotstomach","Onegnawer",
"Kilcraw","Palecraw","Bitefury","Sickmaw","Quiverom","Goreph","Stalerott","Stalecrawler","Kilos",)}

