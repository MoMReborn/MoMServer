@echo off 

echo "---------------------------" 
echo "Clearing Temp Dirs..." 
echo "---------------------------" 
rmdir processedPNG /s /q 

echo "---------------------------" 
echo "Building windows..." 
echo "---------------------------" 
.\packaging\client2exe.py py2exe gameconfig=%1.cfg

echo "---------------------------" 
echo "Building journal..." 
echo "---------------------------" 
.\mud\worlddocs\gendocs.py gameconfig=%1.cfg
copy .\distrib\momworld.tar.gz .\%1.mmo\data\ui\encyclopedia\momworld.tar.gz /y 

echo "---------------------------" 
echo "Building common..." 
echo "---------------------------" 
.\packaging\builddistro.py gameconfig=%1.cfg

echo "---------------------------" 
echo "Copying to SVN..." 
echo "---------------------------" 
xcopy .\distrib\common c:\mygame\patchfiles\common /e /h /y /i 
copy .\patchlist.txt c:\mygame\patchfiles\common\patchlist.txt /y 

echo "---------------------------" 
echo "Touching Manifests..." 
echo "---------------------------" 
.\packaging\touchmanifests.py gameconfig=%1.cfg

start publishtosvn.bat
