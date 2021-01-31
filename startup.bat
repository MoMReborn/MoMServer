start "%CD%" start /b .\mud\masterserver\main.py gameconfig=%1.cfg
sleep 8
start "%CD%" start /b .\mud\gmserver\gmserver.py gameconfig=%1.cfg
sleep 8
start "%CD%" start /b .\mud\characterserver\server.py gameconfig=%1.cfg
sleep 8
start "%CD%" start /b .\worlddaemon.py -worldname=Premium_MMORPG -publicname=starter -password=mmo gameconfig=%1.cfg
