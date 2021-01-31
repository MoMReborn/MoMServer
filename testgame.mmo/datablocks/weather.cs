datablock AudioProfile(HeavyRainSound)
{
   filename    = "~/data/sound/environment/rain.ogg";
   description = AudioLooping2d;

};

datablock PrecipitationData(HeavyRain)
{


   dropTexture = "~/data/environment/rain";
   splashTexture = "~/data/environment/water_splash";
   dropSize = 0.75;
   splashSize = 0.2;
   useTrueBillboards = false;
   splashMS = 250;
};

 //-----------------------------------------------------------------------------

datablock AudioProfile(ThunderCrash1Sound)
{
   filename  = "~/data/sound/environment/thunder1.ogg";
   description = Audio2d;
};

datablock AudioProfile(ThunderCrash2Sound)
{
   filename  = "~/data/sound/environment/thunder2.ogg";
   description = Audio2d;
};

datablock AudioProfile(ThunderCrash3Sound)
{
   filename  = "~/data/sound/environment/thunder3.ogg";
   description = Audio2d;
};

datablock AudioProfile(ThunderCrash4Sound)
{
   filename  = "~/data/sound/environment/thunder4.ogg";
   description = Audio2d;
};

//datablock AudioProfile(LightningHitSound)
//{
//   filename  = "~/data/sound/crossbow_explosion.ogg";
//   description = AudioLightning3d;
//};

datablock LightningData(LightningStorm)
{
   strikeTextures[0]  = "~/data/environment/lightning1frame1";
   strikeTextures[1]  = "~/data/environment/lightning1frame2";
   strikeTextures[2]  = "~/data/environment/lightning1frame3";

   //strikeSound = LightningHitSound;
   thunderSounds[0] = ThunderCrash1Sound;
   thunderSounds[1] = ThunderCrash2Sound;
   thunderSounds[2] = ThunderCrash3Sound;
   thunderSounds[3] = ThunderCrash4Sound;
};


datablock PrecipitationData(HeavyRain2)
{
   soundProfile = "HeavyRainSound";
   dropTexture = "~/data/environment/mist";
   //splashTexture = "~/data/environment/mist2";
   dropSize = 10;
   splashSize = 0.1;
   useTrueBillboards = false;
   splashMS = 250;
};

datablock PrecipitationData(HeavyRain3)
{
   dropTexture = "~/data/environment/shine";
   //splashTexture = "~/data/environment/mist2";
   dropSize = 10;
   splashSize = 0.1;
   useTrueBillboards = false;
   splashMS = 250;
};

//-=-=-=-=-=-=-=-

datablock AudioProfile(Sandstormsound)
{
   filename    = "~/data/sound/environment/Wind_BlowingLoop2.ogg";
   description = AudioLooping2d;
   volume   = 1.0;
};

datablock PrecipitationData(Sandstorm)
{
   soundProfile = "Sandstormsound";

   dropTexture = "~/data/environment/sandstorm";
   splashTexture = "~/data/environment/sandstorm2";
   dropSize = 15;
   splashSize = 2;
   useTrueBillboards = false;
   splashMS = 250;
};


datablock PrecipitationData(dustspecks)
{
   dropTexture = "~/data/environment/dust";
   splashTexture = "~/data/environment/dust2";
   dropSize = 0.25;
   splashSize = 0.25;
   useTrueBillboards = false;
   splashMS = 250;
};

//-=-=-=-=-=-=-=-



datablock PrecipitationData(HeavySnow)
{
    dropTexture = "~/data/environment/snow";
   splashTexture = "~/data/environment/snow";
   dropSize = 0.27;
   splashSize = 0.27;
   useTrueBillboards = false;
   splashMS = 50;
};
