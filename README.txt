Installing Python, and the pyautogui library

1. Download and install: https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe
2. Open run dialog with Win+R, type cmd, and press ok
3. In the command prompt, type the command "py -m pip install pyautogui" and press return
4. Wait for the installation
4. Close the command prompt

Setup
1. Request an oauth code with this link https://twitchapps.com/tmi/ (don't leak this on stream)
2. Edit tcm.py, and set the correct username and oauth variables
3. To start twitch controlling mouse, double click tcm.py
4. To stop, close the command prompt that opens, or use command !quittcm
5. If something doesnt work, screenshot the command prompt and send to sharperguy

Commands:
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
!click
!rightclick
!middlemouse
!doubleclick
!quittcm

Note: 
* !movemouse moves the mouse to an exact coordinate on the screen, which is a percentage of the screen size. So !movemouse 50 50 will move to the center of the screen.
* !box will drag a box with a given size, starting from the current mouse position
* !quittcm only works for the streamer
* The commands !mouseup, !mousedown, !boxdownleft, !boxupright etc can also take an optional distance.