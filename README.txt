-------
Twitch Plays RTS
-------

Installing Python
--------------------------------------

1. Download and install: https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe

Running TPRTS
-------------------------------------
1. Request an oauth code with this link https://twitchapps.com/tmi/ (don't leak this on stream)
2. To start twitch controlling mouse, double click START.bat
3. If this is the first time running the program, you will be asked for your twitch username and oauth. You can paste by just right-clicking in the command prompt. Press enter to continue.
4. To stop, close the command prompt that opens
5. If something doesnt work, screenshot the command prompt and send to sharperguy

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

Note:
* !movemouse moves the mouse to an exact coordinate on the screen, which is a percentage of the screen size. So !movemouse 50 50 will move to the center of the screen.
* !box will drag a box with a given size, starting from the current mouse position
* The commands !mouseup, !mousedown, !boxdownleft, !boxupright etc can also take an optional distance.
* The config file is located in: C:\Users\<username>\AppData\Local\TwitchPlaysRTS\TwitchPlaysRTS\config.toml, which stores credentials and other information.
