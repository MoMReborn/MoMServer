@echo off 

echo "---------------------------" 
echo "Adding files to SVN..." 
echo "---------------------------" 
cd \ 
cd mygame 
cd patchfiles 
svn add --force * 

echo "---------------------------" 
echo "Commit to SVN..." 
echo "---------------------------" 
svn commit -m "Revision" 

pause
exit
