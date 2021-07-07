-------
Twitch Plays RTS
-------

Installing Python
--------------------------------------

1. Download and install: https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe

Running TPRTS
-------------------------------------
1. Request an oauth code with this link https://twitchapps.com/tmi/ (don't leak this on stream)
2. To start the program, double click START.bat
3. If this is the first time running the program, you will be asked for your twitch username and oauth. You can paste by just right-clicking in the command prompt. Press enter to continue.
4. Chat control will be started

* To temporarily stop chat control, type the command !stopcontrol in chat
* To restart chat control, type the command !startcontrol

Custom Commmands
-------------------------------------
* Custom commands can be configured by editing the commands.toml file. This gets created the first time you run the program.
* The file also contains instructions on how to create new commands.
* The file should be located at: C:\Users\<username>\AppData\Local\TwitchPlaysRTS\TwitchPlaysRTS\commands.toml

Default Commands:
-------------------------------------
!movemouse X Y or !mouse X Y
!mouseup
!mousedown
!mouseleft
!mouseright
!mouseupleft
!mouseupright
!mousedownleft
!mousedownright
!box X Y
!boxupleft
!boxupright
!boxdownleft
!boxdownright
!click or !leftclick
!rightclick
!middleclick
!doubleclick
!north
!south
!east
!west

Note:
* !movemouse moves the mouse to an exact coordinate on the screen, which is a percentage of the screen size. So !movemouse 50 50 will move to the center of the screen.
* Mouse movement commands won't move the mouse all the way to the edge of the screen, to prevent accidental scrolling.
* The !startcontrol and !stopcontrol commands only work for the streamer
* The commands !mouseup, !mousedown, !boxdownleft, !boxupright etc can also take an optional distance.
* The config file is located in: C:\Users\<username>\AppData\Local\TwitchPlaysRTS\TwitchPlaysRTS\config.toml, which stores credentials and other information.
* If you have any problems, please send the output.log file to a developer.
