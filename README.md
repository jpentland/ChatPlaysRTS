# Chat Plays RTS

Allow viewers to take control of your mouse and keyboard with predefined commands while streaming RTS or other games.

## Disclaimer

Chat Plays RTS is not associated with Twitch or Twitch Interactive, Inc. Chat Plays RTS reads user commands from Twitch IRC chat in accordance with Twitch developer guidelines.

The official Twitch website can be found at [https://twitch.tv](https://twitch.tv).

## Installing Python

This program requires an update python installation to use. Please download and install from. https://www.python.org/downloads/windows/

This program is primarily targeted for Windows 10, however it should also work on GNU/Linux.

## Running CPR

1. Request an oauth code with this link https://twitchapps.com/tmi/ (don't leak this on stream)
2. To start the program, double click START.bat
3. Enter your username and oauth into the boxes on screen.
4. Click Connect.
4. Chat control will be started

## Moderator commands

### Special commands which can only be used by the streamer and moderators
* !stopcontrol
        - Temporarily stop responding to all commands (except moderator commands)
* !startcontrol
        - Start responding to commands again
* !restrict [badges]
        - Temporarily restrict all commands to users with given badges. E.g.
          "!restrict subscriber,vip,moderator" allows commands to only be used by subscribers, vips and moderators.
        - This will be reset when disconnecting/reconnecting or closing
          the program
* !unrestrict
        - Remove restrictions added by the !restrict command

## Custom Commmands

* Custom commands can be configured by creating a usercommands.toml in the app directory.
* The file should be located at: C:\Users\\<username>\AppData\Local\ChatPlaysRTS\TwitchPlaysRTS\usercommands.toml
* For more information, see Commands.txt in the doc directory

## Default Commands:

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
        !northeast
        !northwest
        !southeast
        !southwest

## Note:
* !movemouse moves the mouse to an exact coordinate on the screen, which is a percentage of the screen size. So !movemouse 50 50 will move to the center of the screen.
* Mouse movement commands won't move the mouse all the way to the edge of the screen, to prevent accidental scrolling.
* The commands !mouseup, !mousedown, !boxdownleft, !boxupright etc can also take an optional distance.
* The config file is located in: C:\Users\\<username>\AppData\Local\ChatPlaysRTS\ChatPlaysRTS\config.toml, which stores credentials and other information.
* If you have any problems, please send the output.log file to a developer.
