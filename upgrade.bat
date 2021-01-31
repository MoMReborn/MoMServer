echo "Updating Character Database" 
echo "---------------------------" 
.\mud\characterserver\upgradedb.py gameconfig=%1.cfg
copy .\data\character\character.db .\data\character\character.bak /y 
copy .\data\updated.db .\data\character\character.db /y 
