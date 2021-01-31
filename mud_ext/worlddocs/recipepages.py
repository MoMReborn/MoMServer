# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.world.crafting import Recipe
from mud.world.defines import *
from utils import *


RecipePage = """
---+ ^^RECIPENAME^^

---++ Description

^^DESCTEXT^^
    
"""

def RecipeLevelSort(a,b):
    if a.skillLevel < b.skillLevel:
        return -1
    if a.skillLevel > b.skillLevel:
        return 1
    return 0

    
def GenDescText(recipe):

    stext = ""
    tname = "Item"+GetTWikiName(recipe.craftedItemProto.name)
    stext+="*Crafted Item:* [[%s][%s]]"%(tname,recipe.craftedItemProto.name)
    
    stext+="<br><br>\n*Skill:* %s (%s) "%(recipe.skillname,recipe.skillLevel)
    
    stext+="<br><br>\n*Ingredients:*\n"
    for ing in recipe.ingredients:
        tname = "Item"+GetTWikiName(ing.itemProto.name)
        if ing.count:
            itext = "%s (%i)"%(ing.itemProto.name,ing.count)
        else:
            itext = ing.itemProto.name
            
        stext+="\t[[%s][%s]]\n"%(tname,itext)
    
    return stext


def CreateRecipeSubIndex(indexFile,indexTitle,recipeList):
    subpage = "---+ %s\n\n"%indexTitle
    for recipe in recipeList:
        TWIKINAME = "Recipe"+GetTWikiName(recipe.name)
        subpage+="\t* (%i)\t [[%s][%s]]\n"%(recipe.skillLevel,TWIKINAME,recipe.name)
    f = file("./distrib/twiki/data/MoMWorld/%s.txt"%indexFile,"w")
    f.write(subpage)
    f.close()


def CreateRecipePages():
    
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Recipe Index\n\n"
    
    listname = "All Recipes"
    TWIKINAMEALL = "RecipeAllIndex"
    indexPage += "\t* [[%s][%s]]\n"%(TWIKINAMEALL,listname)
    allPage = "---+ All Recipes\n\n"
    
    
    recipeCollection = {}
    recipeCollection[listname] = []
    for r in Recipe.select(orderBy="name"):
        page = RecipePage
        
        TWIKINAME = "Recipe"+GetTWikiName(r.name)
        allPage += "\t* (%i)\t [[%s][%s]]\n"%(r.skillLevel,TWIKINAME,r.name)
        
        DESCTEXT = GenDescText(r)
        page = page.replace("^^RECIPENAME^^",r.name.upper()+" RECIPE")
        page = page.replace("^^DESCTEXT^^",DESCTEXT)
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
        
        if not recipeCollection.has_key(r.skillname):
            recipeCollection[r.skillname] = []
        if r not in recipeCollection[r.skillname]:
            recipeCollection[r.skillname].append(r)
        if r not in recipeCollection[listname]:
            recipeCollection[listname].append(r)
    
    f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAMEALL,"w")
    f.write(allPage)
    f.close()
    
    
    TWIKINAMELEVEL = "RecipeAllLevelIndex"
    listnameLevel = listname+" by Skill Level"
    indexPage += "\t* [[%s][%s]]\n\n"%(TWIKINAMELEVEL,listnameLevel)
    recipeList = recipeCollection[listname]
    recipeList.sort(RecipeLevelSort)
    CreateRecipeSubIndex(TWIKINAMELEVEL,listnameLevel,recipeList)
    del recipeCollection["All Recipes"]
    for listname in recipeCollection.iterkeys():
        recipeList = recipeCollection[listname]
        TWIKINAME = "Recipe"+GetTWikiName(listname)+"Index"
        TWIKINAMELEVEL = "Recipe"+GetTWikiName(listname)+"LevelIndex"
        listnameLevel = listname+" by Skill Level"
        indexPage += "\t* [[%s][%s]]\n"%(TWIKINAME,listname)
        indexPage += "\t* [[%s][%s]]\n"%(TWIKINAMELEVEL,listnameLevel)
        CreateRecipeSubIndex(TWIKINAME,listname,recipeList)
        recipeList.sort(RecipeLevelSort)
        CreateRecipeSubIndex(TWIKINAMELEVEL,listnameLevel,recipeList)

    f = file("./distrib/twiki/data/MoMWorld/RecipeIndex.txt","w")
    f.write(indexPage)
    f.close()
        
        
  