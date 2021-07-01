#!/usr/bin/env python3
import pyautogui as pg
import time
import socket
import re
import sys
import os
from queue import Queue
import threading
from appdirs import *
import toml
import pathlib

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"
config_dir = user_data_dir(appname, appauthor)
config_file_path = os.path.join(config_dir, "config.toml")

pg.PAUSE = 0
pg.FAILSAFE=False

defaultConfig = {
        "execution" : {
            "timeout" : 2,
            "defaultDistance" : 10
        },
        "irc" : {
            "domain" : "irc.chat.twitch.tv",
            "port" : 6667,
            "PING_MSG" : "PING :tmi.twitch.tv",
            "PONG_MSG" : "PONG :tmi.twitch.tv"
        }
}

reMoveMouse = re.compile("!(?:movemouse|mouse) ([0-9\.]+) ([0-9\.]+)")
reBox = re.compile("!box (-?[0-9\.]+) (-?[0-9\.]+)")
reClick = re.compile("!click")
reRightClick = re.compile("!rightclick")
reMiddleMouse = re.compile("!middlemouse")
reDoubleClick = re.compile("!doubleclick")
reMouseUp = re.compile("!mouseup")
reMouseUpCoord = re.compile("!mouseup ([0-9\.]+)")
reMouseDown = re.compile("!mousedown")
reMouseDownCoord = re.compile("!mousedown ([0-9\.]+)")
reMouseLeft = re.compile("!mouseleft")
reMouseLeftCoord = re.compile("!mouseleft ([0-9\.]+)")
reMouseRight = re.compile("!mouseright")
reMouseRightCoord = re.compile("!mouseright ([0-9\.]+)")
reMouseUpLeft = re.compile("!mouseupleft")
reMouseUpLeftCoord = re.compile("!mouseupleft ([0-9\.]+)")
reMouseUpRight = re.compile("!mouseupright")
reMouseUpRightCoord = re.compile("!mouseupright ([0-9\.]+)")
reMouseDownLeft = re.compile("!mousedownleft")
reMouseDownLeftCoord = re.compile("!mousedownleft ([0-9\.]+)")
reMouseDownRight = re.compile("!mousedownright")
reMouseDownRightCoord = re.compile("!mousedownright ([0-9\.]+)")
reBoxUpLeft = re.compile("!boxupleft")
reBoxUpLeftCoord = re.compile("!boxupleft ([0-9\.]+)")
reBoxUpRight = re.compile("!boxupright")
reBoxUpRightCoord = re.compile("!boxupright ([0-9\.]+)")
reBoxDownLeft = re.compile("!boxdownleft")
reBoxDownLeftCoord = re.compile("!boxdownleft ([0-9\.]+)")
reBoxDownRight = re.compile("!boxdownright")
reBoxDownRightCoord = re.compile("!boxdownright ([0-9\.]+)")
reQuit = re.compile("!quittcm")

commandQueue = Queue()

screenWidth, screenHeight = pg.size()

# Get contents of config file or defaultconfig if doesnt exist
def loadConfig():
    try:
        with open(config_file_path) as configFile:
            content = configFile.read()
            return toml.loads(content)
    except FileNotFoundError:
        return defaultConfig

# Write config to disk
def writeConfig(config):
    pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
    with open(config_file_path, "w") as configFile:
        toml.dump(config, configFile)

# CLI: display error message, press any key to exit
def errorOut(msg):
    print("ERROR: %s" % msg)
    input("Press RETURN to exit\n")
    sys.exit(1)

# CLI: Get username and oauth values if not set in config
def getCredentials(config):
    if "credentials" not in config:
        config["credentials"] = {}

    if "username" not in config["credentials"]:
        config["credentials"]["username"] = input("Please enter your stream username: ")

    if "oauth" not in config["credentials"]:
        config["credentials"]["oauth"] = input("Please enter your stream oauth: ")

    return config

def percentageToPixel(x, y):
    return screenWidth * (x/100), screenHeight * (y/100)

def openWindow():
    window = tk.Tk()
    greeting = tk.Label(text="Hello, Tkinter")
    greeting.pack()
    window.mainloop()

def moveMouse(x, y):
    x, y = percentageToPixel(x, y)
    pg.moveTo(x, y, 0.5, pg.easeInOutQuad)

def relMouse(x, y):
    x, y = percentageToPixel(float(x), float(y))
    pg.moveRel(x, y, 0.5, pg.easeInOutQuad)

def box(x, y):
    x, y = percentageToPixel(float(x), float(y))
    pg.dragRel(x, y, 0.5, pg.easeInOutQuad)

def send(server, string):
    server.send(bytes(string + '\r\n', 'utf-8'))
    
def runIrc():
    connection_data = (config["irc"]["domain"], config["irc"]["port"])
    server = socket.socket()
    server.connect(connection_data)
    send(server, 'PASS ' + config["credentials"]["oauth"])
    send(server, 'NICK ' + config["credentials"]["username"])
    send(server, 'JOIN #' + config["credentials"]["username"])
    while(True):
        try:
            message = server.recv(2048).decode('utf-8')
            if ("" == message):
                print("Connection to twitch terminated")
                server.close()
                exit(0)

            elif (config["irc"]["PING_MSG"][:4] == message[:4]):
                print("twitch pinged")
                print(repr(message))
                send(server, config["irc"]["PONG_MSG"])
            
            else:
                processChatMessage(message)

        except Exception as error:
            print("Error type: ", type(error))
            print(error.args)

def processChatMessage(message):
    print(message)

    match = reMessage.match(message)
    if match != None:
        commandQueue.put((time.time(), match.group(1), match.group(2)))

def processCommandQueue():
    while(True):
        try:
            epoch, sender, command = commandQueue.get()
            if epoch + config["execution"]["timeout"] >= time.time():
                processCommand(config["credentials"]["username"], command)
        except:
            pass

def processCommand(sender, message):
    print("\"" + message + "\"")
    defaultDistance = config["execution"]["defaultDistance"]
    match = reMoveMouse.match(message)
    if match != None:
        x = float(match.group(1))
        y = float(match.group(2))
        moveMouse(x, y)
    match = reBox.match(message)
    if match != None:
        x = float(match.group(1))
        y = float(match.group(2))
        box(x, y)
    match = reClick.match(message)
    if match != None:
        pg.click()
    match = reRightClick.match(message)
    if match != None:
        pg.click(button='right')
    match = reMiddleMouse.match(message)
    if match != None:
        pg.click(button="middle")
    match = reDoubleClick.match(message)
    if match != None:
        pg.doubleClick()
    match = reQuit.match(message)
    if match != None and sender == config["credentials"]["username"]:
        sys.exit(0)

    match = reMouseUpLeftCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(-d, -d)
        return
    match = reMouseUpLeft.match(message)
    if match != None:
        relMouse(-defaultDistance, -defaultDistance)
        return
    match = reMouseUpRightCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(d, -d)
        return
    match = reMouseUpRight.match(message)
    if match != None:
        relMouse(defaultDistance, -defaultDistance)
        return
    match = reMouseDownLeftCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(-d, d)
        return
    match = reMouseDownLeft.match(message)
    if match != None:
        relMouse(-defaultDistance, defaultDistance)
        return
    match = reMouseDownRightCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(d, d)
        return
    match = reMouseDownRight.match(message)
    if match != None:
        relMouse(defaultDistance, defaultDistance)
        return
    match = reMouseUpCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(0, -d)
        return
    match = reMouseUp.match(message)
    if match != None:
        relMouse(0, -defaultDistance)
        return
    match = reMouseDownCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(0, d)
        return
    match = reMouseDown.match(message)
    if match != None:
        relMouse(0, defaultDistance)
        return
    match = reMouseLeftCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(-d, 0)
        return
    match = reMouseLeft.match(message)
    if match != None:
        relMouse(-defaultDistance, 0)
        return
    match = reMouseRightCoord.match(message)
    if match != None:
        d = float(match.group(1))
        relMouse(d, 0)
        return
    match = reMouseRight.match(message)
    if match != None:
        relMouse(defaultDistance, 0)
        return

    match = reBoxUpLeftCoord.match(message)
    if match != None:
        d = float(match.group(1))
        box(-d, -d)
        return
    match = reBoxUpLeft.match(message)
    if match != None:
        box(-defaultDistance, -defaultDistance)
        return
    match = reBoxUpRightCoord.match(message)
    if match != None:
        d = float(match.group(1))
        box(d, -d)
        return
    match = reBoxUpRight.match(message)
    if match != None:
        box(defaultDistance, -defaultDistance)
        return
    match = reBoxDownLeftCoord.match(message)
    if match != None:
        d = float(match.group(1))
        box(-d, d)
        return
    match = reBoxDownLeft.match(message)
    if match != None:
        box(-defaultDistance, defaultDistance)
        return
    match = reBoxDownRightCoord.match(message)
    if match != None:
        d = float(match.group(1))
        box(d, d)
        return
    match = reBoxDownRight.match(message)
    if match != None:
        box(defaultDistance, defaultDistance)
        return

config = loadConfig()
config = getCredentials(config)
writeConfig(config)

# TODO: Move this somewhere sensible
reMessage = re.compile("([^\s]+)!.* PRIVMSG #" + config["credentials"]["username"] + " :(.*)")

ircThread = threading.Thread(target = runIrc, daemon = True)
ircThread.start()
processCommandQueue()
