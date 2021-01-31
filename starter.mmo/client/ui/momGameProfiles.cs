//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Override base controls


//-----------------------------------------------------------------------------
// Chat Hud profiles


new GuiControlProfile ("MoMGameTextProfile")
{
   fontType = "Arial";
   fontSize = 14;
   fontColor = "44 172 181";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "4 235 105";   // client join/drop, tournament mode
   fontColors[2] = "219 200 128"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "77 253 95";   // team chat, spam protection message, client tasks
   fontColors[4] = "40 231 240";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   fontColorLink = "44 172 181";
   autoSizeWidth = true;
   autoSizeHeight = true;
};

new GuiControlProfile ("MoMSpeechTextProfile")
{
   fontType = "Arial";
   fontSize = 14;
   fontColor = "44 172 181";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "4 235 105";   // client join/drop, tournament mode
   fontColors[2] = "219 200 128"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "77 253 95";   // team chat, spam protection message, client tasks
   fontColors[4] = "40 231 240";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   fontColorLink = "44 172 181";
   autoSizeWidth = true;
   autoSizeHeight = true;
};



new GuiControlProfile ("CharacterStatText")
{
   fontType = "Arial";
   fontSize = 14;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring 
   autoSizeWidth = true;
   autoSizeHeight = true;
};


new GuiControlProfile ("ChatHudScrollProfile")
{
   opaque = false;
   border = true;
   borderColor = "0 0 0";
   bitmap = "common/ui/darkScroll";
   hasBitmapArray = true;
};


//-----------------------------------------------------------------------------
// Common Hud profiles

new GuiControlProfile ("HudScrollProfile")
{
   opaque = false;
   border = true;
   borderColor = "0 255 0";
   bitmap = "common/ui/darkScroll";
   hasBitmapArray = true;
};

new GuiControlProfile ("HudTextProfile")
{
   opaque = false;
   fillColor = "128 128 128";
   fontColor = "0 255 0";
   border = true;
   borderColor = "0 255 0";
};


//-----------------------------------------------------------------------------
// Center and bottom print

new GuiControlProfile ("CenterPrintProfile")
{
   opaque = false;
   fillColor = "128 128 128";
   fontColor = "0 255 0";
   border = true;
   borderColor = "0 255 0";
};

new GuiControlProfile ("CenterPrintTextProfile")
{
   opaque = false;
   fontType = "Arial";
   fontSize = 12;
   fontColor = "0 255 0";
};

if(!isObject(GuiHealthBarProfile)) new GuiControlProfile ("GuiHealthBarProfile")
{
   opaque = false;
   fillColor = "200 0 0 200";
   border = true;
   borderColor   = "80 80 80";
};

if(!isObject(GuiPetHealthBarProfile)) new GuiControlProfile ("GuiPetHealthBarProfile")
{
   opaque = false;
   fillColor = "8 200 6 200";
   border = true;
   borderColor   = "80 80 80";
};


if(!isObject(GuiTargetHealthBarProfile)) new GuiControlProfile ("GuiTargetHealthBarProfile")
{
   opaque = false;
   fillColor = "205 129 21 200";
   border = true;
   borderColor   = "80 80 80";
};


if(!isObject(GuiChiBarProfile)) new GuiControlProfile ("GuiChiBarProfile")
{
   opaque = false;
   fillColor = "0 0 200 200";
   border = true;
   borderColor   = "80 80 80";
};

if(!isObject(GuiBreathBarProfile)) new GuiControlProfile ("GuiBreathBarProfile")
{
   opaque = false;
   fillColor = "0 216 255 255";
   border = true;
   borderColor   = "80 80 80";
};

if(!isObject(GuiPXPBarProfile)) new GuiControlProfile ("GuiPXPBarProfile")
{
   opaque = true;
   fillColor = "220 220 220 255";
   border = false;

};
if(!isObject(GuiSXPBarProfile)) new GuiControlProfile ("GuiSXPBarProfile")
{
   opaque = true;
   fillColor = "170 170 170 255";
   border = false;

};
if(!isObject(GuiTXPBarProfile)) new GuiControlProfile ("GuiTXPBarProfile")
{
   opaque = true;
   fillColor = "150 150 150 255";
   border = false;

};


if(!isObject(GuiStaminaBarProfile)) new GuiControlProfile ("GuiStaminaBarProfile")
{
   opaque = false;
   fillColor = "200 200 0 200";
   border = true;
   borderColor   = "80 80 80";
};

if(!isObject(GuiCastingBarProfile)) new GuiControlProfile ("GuiCastingBarProfile")
{
   opaque = false;
   fillColor = "219 131 255 255";
   border = true;
   borderColor   = "80 80 80";
};

if(!isObject(MoMWndProfile)) new GuiControlProfile (MoMWndProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 160";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 160";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 160";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 160";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 160";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momWindow" : "./momWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100 160";
   
   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

   mouseOverProfile = "MoMWndHLProfile";
   
};

if(!isObject(MoMWndHLProfile)) new GuiControlProfile (MoMWndHLProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 240";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 240";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 240";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 240";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 240";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";
   mouseNotOverProfile = "MoMWndProfile";
   
   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};

if(!isObject(MoMChatWndProfile)) new GuiControlProfile (MoMChatWndProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 220";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 220";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 220";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 220";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 220";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momWindow" : "./momWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100 220";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

   mouseOverProfile = "MoMChatWndHLProfile";

};

if(!isObject(MoMChatWndHLProfile)) new GuiControlProfile (MoMChatWndHLProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 255";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 255";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 255";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 255";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";
   mouseNotOverProfile = "MoMChatWndProfile";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};


if(!isObject(MoMWndAlwaysHLProfile)) new GuiControlProfile (MoMWndAlwaysHLProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 180";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 180";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 180";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 180";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 180";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};

if(!isObject(MoMSolidWndProfile)) new GuiControlProfile (MoMSolidWndProfile)
{
   opaque = true;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};

if(!isObject(MoMSolidBorderProfile)) new GuiControlProfile (MoMSolidBorderProfile)
{
   opaque = true;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   
   bitmap = ($platform $= "blah") ? "./momBorder" : "./momBorder";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};

if(!isObject(MoMBorderProfile)) new GuiControlProfile (MoMBorderProfile)
{
   opaque = false;
   border = 1;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";

   bitmap = ($platform $= "blah") ? "./momBorder" : "./momBorder";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};





if(!isObject(MoMBorderlessWndProfile)) new GuiControlProfile (MoMBorderlessWndProfile)
{
   opaque = false;
   border = false;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 80";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 80";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 80";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 200";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momWindow" : "./momWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = false;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100 80";
   
   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

   
   mouseOverProfile = "MoMBorderlessWndHLProfile";
};

if(!isObject(MoMSelectedWndProfile)) new GuiControlProfile (MoMSelectedWndProfile)
{
   opaque = true;
   border = false;
   fillColor = ($platform $= "blah") ? "200 200 200" : "80 110 100 220";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 220";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 220";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momWindow" : "./momWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = false;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";

   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

   mouseOverProfile = "MoMSelectedWndHLProfile";
};

if(!isObject(MoMBorderlessWndHLProfile)) new GuiControlProfile (MoMBorderlessWndHLProfile)
{
   opaque = false;
   border = false;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 180";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 180";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 180";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = false;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";
   mouseNotOverProfile = "MoMBorderlessWndProfile";
   
   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};

if(!isObject(MoMSelectedWndHLProfile)) new GuiControlProfile (MoMSelectedWndHLProfile)
{
   opaque = true;
   border = false;
   fillColor = ($platform $= "blah") ? "200 200 200" : "80 110 100 240";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "40 40 40 240";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "40 40 40 240";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momHLWindow" : "./momHLWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = false;
   justify = ($platform $= "blah") ? "center" : "center";
   borderColor   = "100 100 100";
   mouseNotOverProfile = "MoMSelectedWndProfile";
   soundWindowOpen = "AudioWindowOpen";
   soundWindowClose = "AudioWindowClose";

};



if(!isObject(CharWndProfile)) new GuiControlProfile (CharWndProfile)
{
   opaque = false;
   border = 2;
   fillColor = ($platform $= "blah") ? "200 200 200" : "40 40 40 240";
   fillColorHL = ($platform $= "blah") ? "190 255 255" : "64 150 150";
   fillColorNA = ($platform $= "blah") ? "255 255 255" : "150 150 150";
   fontColor = ($platform $= "blah") ? "0 0 0" : "255 255 255 200";
   fontColorHL = ($platform $= "blah") ? "200 200 200" : "0 0 0 255";
   text = "GuiWindowCtrl test";
   bitmap = ($platform $= "blah") ? "./momWindow" : "./momWindow";
   textOffset = ($platform $= "blah") ? "5 5" : "6 6";
   hasBitmapArray = true;
   justify = ($platform $= "blah") ? "center" : "left";
};


if(!isObject(CharWndInvProfile)) new GuiControlProfile (CharWndInvProfile)
{
   opaque = false;
   border = false;
   fillColor = "100 100 100 80";
   fontColor = "0 0 0";
   fontColorHL = "32 100 100";
   fixedExtent = true;
   justify = "center";
	canKeyFocus = false;
};


if(!isObject(CommandButtonProfile)) new GuiControlProfile (CommandButtonProfile)
{
   opaque = false;
   border = false;
   fillColor = "100 100 100 100";
   fontColor = "0 0 0";
   fontColorHL = "32 100 100";
   fixedExtent = true;
   justify = "center";
	canKeyFocus = false;
};

if(!isObject(ChatTextEditProfile)) new GuiControlProfile (ChatTextEditProfile)
{
   opaque = true;
   fillColor = "255 255 255";
   fillColorHL = "128 128 128";
   border = 3;
   borderThickness = 2;
   borderColor = "0 0 0";
   fontColor = "0 0 0";
   fontColorHL = "255 255 255";
   fontColorNA = "128 128 128";
   textOffset = "0 2";
   autoSizeWidth = false;
   autoSizeHeight = false;
//   tab = true;
   canKeyFocus = true;
};

//Text
if(!isObject(MoMStatText)) new GuiControlProfile ("MoMStatText")
{
   fontType = "Arial";
   fontSize = 14;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
};

if(!isObject(MoMMediumText)) new GuiControlProfile ("MoMMediumText")
{
   fontType = "Arial Bold";
   fontSize = 16;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   fontColorLink = "255 255 255";
   autoSizeWidth = true;
   autoSizeHeight = true;
};


//Text
if(!isObject(MoMBigStatText)) new GuiControlProfile ("MoMBigStatText")
{
   fontType = "Arial Bold";
   fontSize = 18;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
};


if(!isObject(MoMScrollText)) new GuiControlProfile (MoMScrollText : GuiTextProfile)
{
   fontType = "Arial Bold";
   fontSize = 15;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
   
   fontColor = "220 220 220";
   fontColorHL = "255 255 255";
   fontColorNA = "190 190 190";
   fontColorSEL= "200 200 255";
   
   fillColorHL = "90 90 90";

   fontColorLink = "200 200 255";
   fontColorLinkHL = "255 255 255";
};

if(!isObject(MoMBigScrollText)) new GuiControlProfile (MoMBigScrollText)
{
   fontType = "Arial Bold";
   fontSize = 16;
   fontColor = "46 201 203";      // default color (death msgs, scoring, inventory)
   autoSizeWidth = true;
   autoSizeHeight = true;
   fontColorHL = "60 255 255";
   fillColorHL = "100 100 100";

   fontColors[1] = "60 255 255";
   fontColors[2] = "0 255 0";   // client join/drop, tournament mode
   fontColors[3] = "255 0 0"; // gameplay, admin/voting, pack/deployable
   fontColors[4] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[5] = "255 255 0";  // global chat
   fontColors[6] = "200 200 50 200";  // used in single player game
   canKeyFocus = true;
};

if(!isObject(MoMRadioProfile)) new GuiControlProfile (MoMRadioProfile)
{

   fontType = "Arial";
   fontSize = 14;
   fontColor = "190 190 190";
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   
   fontColorHL = "220 220 220";
   fontColorNA = "190 190 190";
   fontColorSEL= "200 200 255";

   fillColorHL = "128 128 128";

   fontColorLink = "200 200 255";
   fontColorLinkHL = "255 255 255";

   fixedExtent = true;
   bitmap = ($platform $= "blah") ? "./osxRadio" : "./demoRadio";
   hasBitmapArray = true;
};



if(!isObject(MoMSmallStatText)) new GuiControlProfile ("MoMSmallStatText")
{
   fontType = "Arial";
   fontSize = 12;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
};


if(!isObject(MoMTacticalText)) new GuiControlProfile ("MoMTacticalText")
{
   fontType = "Arial";
   fontSize = 12;
   fontColor = "255 255 255";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   //autoSizeWidth = true;       // I believe this makes this small font scrunchy!!!
   //autoSizeHeight = true;
};


new GuiControlProfile ("StatTextProfile")
{
   fontType = "Arial";
   fontSize = 14;
   fontColor = "0 0 0";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
   
   fontColorHL = "32 100 100";
   fillColorHL = "200 200 200";

};

new GuiControlProfile ("MoMTextListProfile")
{
   fontType = "Arial Bold";
   fontSize = 12;
   fontColor = "46 201 203";      // default color (death msgs, scoring, inventory)
   autoSizeWidth = true;
   autoSizeHeight = true;
   fontColorHL = "60 255 255";
   fillColorHL = "100 100 100";
   
   fontColors[1] = "60 255 255";
   fontColors[2] = "0 255 0";   // client join/drop, tournament mode
   fontColors[3] = "255 0 0"; // gameplay, admin/voting, pack/deployable
   fontColors[4] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[5] = "255 255 0";  // global chat
   fontColors[6] = "200 200 50 200";  // used in single player game
   canKeyFocus = true;


};

new GuiControlProfile ("MoMTrackingTextProfile")
{
   fontType = "Arial Bold";
   fontSize = 14;
   fontColor = "46 201 203";      // default color (death msgs, scoring, inventory)
   autoSizeWidth = true;
   autoSizeHeight = true;
   fontColorHL = "60 255 255";
   fillColorHL = "100 100 100";

   fontColors[1] = "60 255 255";
   fontColors[2] = "0 255 0";   // client join/drop, tournament mode
   fontColors[3] = "255 90 90"; // gameplay, admin/voting, pack/deployable
   fontColors[4] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[5] = "255 255 0";  // global chat
   fontColors[6] = "200 200 50 200";  // used in single player game
   canKeyFocus = true;


};


new GuiControlProfile ("InvItemTextProfile")
{
   fontType = "Arial";
   fontSize = 12;
   fontColor = "0 0 0";      // default color (death msgs, scoring, inventory)
   fontColors[1] = "255 0 0";   // client join/drop, tournament mode
   fontColors[2] = "0 255 0"; // gameplay, admin/voting, pack/deployable
   fontColors[3] = "200 200 200";   // team chat, spam protection message, client tasks
   fontColors[4] = "255 255 0";  // global chat
   fontColors[5] = "200 200 50 200";  // used in single player game
   // WARNING! Colors 6-9 are reserved for name coloring
   autoSizeWidth = true;
   autoSizeHeight = true;
};


if(!isObject(MoMScrollProfile)) new GuiControlProfile (MoMScrollProfile)
{

   opaque = false;
   fillColor = "40 40 40 80";
   border = 1;
   borderThickness = 2;
   borderColor = "120 120 120 160";
   bitmap = ($platform $= "blah") ? "./momScroll" : "./momScroll";
   hasBitmapArray = true;
   
};

if(!isObject(InvButtonProfile)) new GuiControlProfile (InvButtonProfile)
{
   opaque = false;
   border = false;
   fontSize = 12;
   fillBitmap = "./buttonFill";
   fillColor = "200 200 200 80";
   fillColorHL = "255 255 255 235";
   fontColor = "180 180 180 160";
   fontColorHL = "220 220 120 220";

   fontColors[2] = "255 255 255";
   fontColors[3] = "255 255 255";
   fixedExtent = true;
   justify = "center";
   canKeyFocus = false;
   borderColor = "0 0 0";
};

if(!isObject(MenuButtonProfile)) new GuiControlProfile (MenuButtonProfile)
{
   opaque = false;
   border = false;
   fontSize = 14;
   fillBitmap = "./buttonFill";
   fillColor = "225 225 225 255";
   fillColorHL = "255 255 255 255";
   fontColor = "180 180 180 160";
   fontColorHL = "220 220 120 220";

   fontColors[2] = "255 255 255";
   fontColors[3] = "255 255 255";
   fixedExtent = true;
   justify = "center";
   canKeyFocus = false;
   borderColor = "0 0 0";
};


if(!isObject(MoMCheckBoxProfile)) new GuiControlProfile (MoMCheckBoxProfile)
{
   opaque = false;
   fillColor = "100 100 100 100";
   border = false;
   borderColor = "0 0 0";
   fontSize = 14;
   fontColor = "200 200 200";
   fontColorHL = "255 255 255";
   fixedExtent = true;
   justify = "left";
   bitmap = ($platform $= "blah") ? "./momCheck" : "./momCheck";
   hasBitmapArray = true;

};

if(!isObject(MoMPopUpMenuProfile)) new GuiControlProfile (MoMPopUpMenuProfile)
{
   opaque = true;
   mouseOverSelected = true;

   border = 4;
   borderThickness = 2;
   borderColor = "0 0 0";
   fontSize = 14;
   fontColor = "200 200 200";
   fontColorHL = "255 255 255";
   fontColorSEL = "255 255 255";
   fixedExtent = true;
   justify = "center";
   bitmap = ($platform $= "blah") ? "./momScroll" : "./momScroll";
   hasBitmapArray = true;
   fillColor = "100 100 100 255";
};

if(!isObject(MoMTextEditProfile)) new GuiControlProfile (MoMTextEditProfile)
{
   opaque = false;
   fillColor = "128 128 128 100";
   fillColorHL = "128 128 128";
   border = 3;
   borderThickness = 1;
   borderColor = "0 0 0";
   fontColor = "192 255 255";
   fontColorHL = "255 255 255";
   fontColorNA = "128 128 128";
   textOffset = "0 2";
   autoSizeWidth = false;
   autoSizeHeight = true;
   tab = false;
   canKeyFocus = true;
   cursorColor = "255 255 255 200";
};


if(!isObject(ShapeNameHudProfile)) new GuiControlProfile (ShapeNameHudProfile : GuiDefaultProfile)
{

   // font
   fontType = "Arial";
   fontSize = 20;


};

if(!isObject(MoMSliderProfile)) new GuiControlProfile (MoMSliderProfile)
{

};



