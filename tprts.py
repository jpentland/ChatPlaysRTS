#!/usr/bin/env python3
import time
import re
import sys
import os
from queue import Queue
from appdirs import *
import toml
import pathlib
from twitchirc import TwitchIrc
from execution import Execution

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"
config_dir = user_data_dir(appname, appauthor)
config_file_path = os.path.join(config_dir, "config.toml")

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
    print(msg)
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

# Read commands from command queue
def processCommandQueue(config):

    execution = Execution(config)
    while(True):
        epoch, sender, command = irc.commandQueue.get()
        print("%s: %s" % (sender, command))
        if sender == None:
            errorOut(command)
            return
        if epoch + config["execution"]["timeout"] >= time.time():
            execution.processCommand(command)

config = loadConfig()
config = getCredentials(config)
writeConfig(config)
irc = TwitchIrc(config)
irc.start()

processCommandQueue(config)
