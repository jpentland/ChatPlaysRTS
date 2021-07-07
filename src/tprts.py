#!/usr/bin/env python3
import time
import re
import sys
import os
from queue import Queue
from appdirs import *
import toml
import pathlib
from twitchirc import TwitchIrc, AuthenticationError
from execution import Execution
from log import Log

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"
config_dir = user_data_dir(appname, appauthor)
config_file = "config.toml"
commands_file = "commands.toml"
defaultconf_dir = "defaultconf"

defaultConfig = {
        "execution" : {
            "timeout" : 10,
            "defaultDistance" : 10,
            "mouseBorder" : 11,
            "clickRateLimit" : 0.5,
        },
        "irc" : {
            "domain" : "irc.chat.twitch.tv",
            "port" : 6667,
            "PING_MSG" : "PING :tmi.twitch.tv",
            "PONG_MSG" : "PONG :tmi.twitch.tv"
        },
        "log": {
            "echo" : True,
            "logfile" : "output.log",
        }
}

# Get contents of config file or defaultconfig if doesnt exist
def loadConfig():
    try:
        with open(os.path.join(config_dir, config_file)) as configFile:
            content = configFile.read()
            config = toml.loads(content)

            # Copy any missing default config options
            for k, v in defaultConfig.items():
                for ki, vi in v.items():
                    if k in config:
                        if ki not in config[k]:
                            config[k][ki] = vi
                    else:
                        config[k] = v

            return config

    except FileNotFoundError:
        return defaultConfig

# Get contents of command file, or create if doesn't exist
def loadCommands():
    try:
        with open(os.path.join(config_dir, commands_file)) as commandsFile:
            content = commandsFile.read()
            return toml.loads(content)["command"]
    except FileNotFoundError:
        copyDefault(commands_file)
        with open(os.path.join(defaultconf_dir, commands_file)) as commandsFile:
            content = commandsFile.read()
            return toml.loads(content)["command"]

# Copy a default config to config dir
def copyDefault(filename):
    with open(os.path.join(defaultconf_dir, filename)) as defaultFile:
        with open(os.path.join(config_dir, filename), "w") as newFile:
            content = defaultFile.read()
            newFile.write(content)

# Write config to disk
def writeConfig(config):
    pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(config_dir, config_file), "w") as configFile:
        toml.dump(config, configFile)

# CLI: display error message, press any key to exit
def errorOut(msg):
    log.log(msg)
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


config = loadConfig()
config = getCredentials(config)
log = Log(config["log"])
writeConfig(config)
irc = TwitchIrc(config, log)
triesLeft = 5
while triesLeft > 0:
    try:
        irc.start()
        break
    except AuthenticationError:
        errorOut("Invalid username or oauth")
        break
    except Exception as e:
        if triesLeft == 1:
            log.log_exception(e)
            errorOut("Failed to connect to server")
        else:
            triesLeft -= 1
            log.log("retrying...")


lastError = 0

commands = loadCommands()
execution = Execution(config, commands, irc, log)
while True:
    try:
        execution.processCommandQueue()
    except Exception as e:
        log.log_exception(e)
        if time.time() - lastError < 10:
            log.log("Program keeps crashing, please restart")
            break
        lastError = time.time()

errorOut("Quitting")
